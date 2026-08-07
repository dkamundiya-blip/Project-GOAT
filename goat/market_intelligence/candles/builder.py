"""
Project GOAT Phase 4 — Universal Candle Builder (`goat.market_intelligence.candles`)

Builds canonical OHLCV candles strictly from recorded ticks across all 12 supported timeframes:
1s, 5s, 15s, 30s, 1m, 2m, 5m, 15m, 30m, 1h, 4h, 1d.
Guarantees zero repainting and automatic finalization on interval boundaries.
"""

from __future__ import annotations

import datetime
import threading
from typing import Callable, Sequence

from goat.market_intelligence.models.candle import (
    TIMEFRAME_SECONDS,
    IntelligenceCandle,
    IntelligenceTimeframe,
    compute_intelligence_candle_id,
)
from goat.market_intelligence.models.tick import RecordedTick
from goat.market_intelligence.persistence.interfaces import ICandleRepository
from goat.research.edge.canonical import compute_canonical_sha256


class UniversalCandleBuilder:
    """Institutional Multi-Timeframe Candle Builder building candles strictly from recorded ticks."""

    ALL_TIMEFRAMES: list[IntelligenceTimeframe] = list(IntelligenceTimeframe)

    def __init__(
        self,
        repository: ICandleRepository | None = None,
        timeframes: Sequence[IntelligenceTimeframe] | None = None,
        on_candle_finalized_callback: Callable[[IntelligenceCandle], None] | None = None,
    ):
        self.repository = repository
        self.active_timeframes = list(timeframes) if timeframes else self.ALL_TIMEFRAMES
        self.on_candle_finalized_callback = on_candle_finalized_callback

        # State: (symbol, timeframe_value) -> forming_candle_dict
        self._forming_candles: dict[tuple[str, str], dict] = {}
        self._lock = threading.RLock()

    def process_tick(self, tick: RecordedTick) -> list[IntelligenceCandle]:
        """Ingest a RecordedTick and update/finalize candles across all active timeframes.

        Returns:
            List of finalized completed IntelligenceCandle objects produced by this tick.
        """
        finalized_candles: list[IntelligenceCandle] = []

        try:
            tick_dt = datetime.datetime.fromisoformat(tick.timestamp.replace("Z", "+00:00"))
        except Exception:
            tick_dt = datetime.datetime.now(datetime.timezone.utc)

        epoch_sec = int(tick_dt.timestamp())

        with self._lock:
            for tf in self.active_timeframes:
                tf_str = tf.value
                sec_duration = TIMEFRAME_SECONDS.get(tf_str, 60)

                # Compute interval boundary timestamps
                interval_start_epoch = (epoch_sec // sec_duration) * sec_duration
                interval_end_epoch = interval_start_epoch + sec_duration

                open_ts = datetime.datetime.fromtimestamp(interval_start_epoch, tz=datetime.timezone.utc).isoformat()
                close_ts = datetime.datetime.fromtimestamp(interval_end_epoch, tz=datetime.timezone.utc).isoformat()

                key = (tick.symbol.upper(), tf_str)
                forming = self._forming_candles.get(key)

                if forming is None:
                    # Initialize first forming candle
                    self._forming_candles[key] = {
                        "symbol": tick.symbol.upper(),
                        "timeframe": tf,
                        "open": tick.mid_price,
                        "high": tick.mid_price,
                        "low": tick.mid_price,
                        "close": tick.mid_price,
                        "volume": 1.0,
                        "open_timestamp": open_ts,
                        "close_timestamp": close_ts,
                        "start_epoch": interval_start_epoch,
                    }
                elif forming["start_epoch"] == interval_start_epoch:
                    # Same interval window — update forming candle
                    forming["high"] = max(forming["high"], tick.mid_price)
                    forming["low"] = min(forming["low"], tick.mid_price)
                    forming["close"] = tick.mid_price
                    forming["volume"] += 1.0
                elif interval_start_epoch > forming["start_epoch"]:
                    # Interval boundary crossed — finalize current candle
                    finalized = self._build_candle_model(forming, completed=True)
                    finalized_candles.append(finalized)

                    if self.repository:
                        self.repository.save_candle(finalized)

                    if self.on_candle_finalized_callback:
                        try:
                            self.on_candle_finalized_callback(finalized)
                        except Exception:
                            pass

                    # Check for missing gap candles between forming["start_epoch"] and interval_start_epoch
                    gap_start_epoch = forming["start_epoch"] + sec_duration
                    gap_fill_price = forming["close"]
                    while gap_start_epoch < interval_start_epoch:
                        gap_end_epoch = gap_start_epoch + sec_duration
                        g_open_ts = datetime.datetime.fromtimestamp(gap_start_epoch, tz=datetime.timezone.utc).isoformat()
                        g_close_ts = datetime.datetime.fromtimestamp(gap_end_epoch, tz=datetime.timezone.utc).isoformat()

                        gap_candle_data = {
                            "symbol": tick.symbol.upper(),
                            "timeframe": tf,
                            "open": gap_fill_price,
                            "high": gap_fill_price,
                            "low": gap_fill_price,
                            "close": gap_fill_price,
                            "volume": 0.0,  # 0 volume for filled gap
                            "open_timestamp": g_open_ts,
                            "close_timestamp": g_close_ts,
                        }
                        gap_candle = self._build_candle_model(gap_candle_data, completed=True)
                        finalized_candles.append(gap_candle)

                        if self.repository:
                            self.repository.save_candle(gap_candle)

                        if self.on_candle_finalized_callback:
                            try:
                                self.on_candle_finalized_callback(gap_candle)
                            except Exception:
                                pass

                        gap_start_epoch += sec_duration

                    # Start new forming candle for current tick
                    self._forming_candles[key] = {
                        "symbol": tick.symbol.upper(),
                        "timeframe": tf,
                        "open": tick.mid_price,
                        "high": tick.mid_price,
                        "low": tick.mid_price,
                        "close": tick.mid_price,
                        "volume": 1.0,
                        "open_timestamp": open_ts,
                        "close_timestamp": close_ts,
                        "start_epoch": interval_start_epoch,
                    }

        return finalized_candles

    def get_latest_forming_candle(self, symbol: str, timeframe: str) -> IntelligenceCandle | None:
        """Get the current uncompleted forming candle for symbol and timeframe."""
        key = (symbol.upper(), timeframe.lower())
        with self._lock:
            forming = self._forming_candles.get(key)
            if forming is None:
                return None
            return self._build_candle_model(forming, completed=False)

    def force_finalize_all(self) -> list[IntelligenceCandle]:
        """Force finalize all currently forming candles (e.g. on shutdown)."""
        finalized_list: list[IntelligenceCandle] = []
        with self._lock:
            for key, forming in list(self._forming_candles.items()):
                finalized = self._build_candle_model(forming, completed=True)
                finalized_list.append(finalized)
                if self.repository:
                    self.repository.save_candle(finalized)
                if self.on_candle_finalized_callback:
                    try:
                        self.on_candle_finalized_callback(finalized)
                    except Exception:
                        pass
            self._forming_candles.clear()
        return finalized_list

    @staticmethod
    def _build_candle_model(data: dict, completed: bool) -> IntelligenceCandle:
        sym = data["symbol"]
        tf = data["timeframe"] if isinstance(data["timeframe"], IntelligenceTimeframe) else IntelligenceTimeframe(data["timeframe"])
        o = round(float(data["open"]), 8)
        h = round(float(data["high"]), 8)
        l = round(float(data["low"]), 8)
        c = round(float(data["close"]), 8)
        vol = round(float(data["volume"]), 2)
        open_ts = data["open_timestamp"]
        close_ts = data["close_timestamp"]

        candle_id, canon_hash = compute_intelligence_candle_id(
            symbol=sym,
            timeframe=tf.value,
            open_price=o,
            high_price=h,
            low_price=l,
            close_price=c,
            open_timestamp=open_ts,
            close_timestamp=close_ts,
        )

        checksum = compute_canonical_sha256(
            {
                "close": c,
                "high": h,
                "low": l,
                "open": o,
                "symbol": sym,
                "timeframe": tf.value,
                "volume": vol,
            }
        )

        return IntelligenceCandle(
            candle_id=candle_id,
            symbol=sym,
            timeframe=tf,
            open=o,
            high=h,
            low=l,
            close=c,
            volume=vol,
            open_timestamp=open_ts,
            close_timestamp=close_ts,
            completed=completed,
            checksum=checksum,
            metadata={"builder": "UniversalCandleBuilder"},
            canonical_hash=canon_hash,
        )
