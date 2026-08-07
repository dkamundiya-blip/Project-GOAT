"""
Project GOAT Phase 4 — Event Detection Engine (`goat.market_intelligence.events`)

Detects market anomalies and structural events: Large Spikes, Crashes, Extreme Candles,
Volatility Expansion/Contraction, Gaps, Spread Anomalies, Connection Interruptions, and Market Pauses.
"""

from __future__ import annotations

import datetime
import threading
from typing import Any, Sequence

from goat.market_intelligence.models.candle import IntelligenceCandle
from goat.market_intelligence.models.event import (
    IntelligenceEventType,
    MarketEvent,
    compute_market_event_id,
)
from goat.market_intelligence.models.market_state import MarketState
from goat.market_intelligence.models.statistics import MarketStatistics
from goat.market_intelligence.models.tick import RecordedTick
from goat.market_intelligence.persistence.interfaces import IEventRepository
from goat.research.edge.canonical import compute_canonical_sha256


class EventDetectionEngine:
    """Institutional Event Detection Engine for real-time market anomaly and structural event monitoring."""

    def __init__(
        self,
        repository: IEventRepository | None = None,
        spike_threshold_pct: float = 0.015,       # 1.5% single tick/bar upward jump
        crash_threshold_pct: float = 0.015,       # 1.5% single tick/bar downward drop
        extreme_candle_mult: float = 2.5,         # 2.5x average candle size
        vol_expansion_mult: float = 2.0,          # 2.0x volatility increase
        vol_contraction_mult: float = 0.5,        # 0.5x volatility decrease
        gap_threshold_sec: float = 5.0,           # 5.0s timestamp gap
        spread_anomaly_mult: float = 3.0,         # 3.0x mean spread
        pause_duration_sec: float = 30.0,         # 30s zero tick activity
    ):
        self.repository = repository
        self.spike_threshold_pct = spike_threshold_pct
        self.crash_threshold_pct = crash_threshold_pct
        self.extreme_candle_mult = extreme_candle_mult
        self.vol_expansion_mult = vol_expansion_mult
        self.vol_contraction_mult = vol_contraction_mult
        self.gap_threshold_sec = gap_threshold_sec
        self.spread_anomaly_mult = spread_anomaly_mult
        self.pause_duration_sec = pause_duration_sec

        # State tracking per symbol
        self._last_ticks: dict[str, RecordedTick] = {}
        self._last_stats: dict[str, MarketStatistics] = {}
        self._lock = threading.RLock()

    def process_tick(self, tick: RecordedTick, current_stats: MarketStatistics | None = None) -> list[MarketEvent]:
        """Evaluate incoming RecordedTick for price spikes, crashes, gaps, spread anomalies, and pauses."""
        events: list[MarketEvent] = []
        sym = tick.symbol.upper()

        with self._lock:
            last_tick = self._last_ticks.get(sym)
            self._last_ticks[sym] = tick

            if last_tick:
                # Price change ratio
                if last_tick.mid_price > 0:
                    price_change_pct = (tick.mid_price - last_tick.mid_price) / last_tick.mid_price

                    # 1. LARGE_SPIKE
                    if price_change_pct >= self.spike_threshold_pct:
                        confidence = min(1.0, price_change_pct / (self.spike_threshold_pct * 2))
                        events.append(
                            self._create_event(
                                symbol=sym,
                                timestamp=tick.timestamp,
                                event_type=IntelligenceEventType.LARGE_SPIKE,
                                confidence=confidence,
                                metadata={
                                    "price_change_pct": round(price_change_pct, 6),
                                    "prev_price": last_tick.mid_price,
                                    "curr_price": tick.mid_price,
                                },
                            )
                        )

                    # 2. CRASH
                    if price_change_pct <= -self.crash_threshold_pct:
                        confidence = min(1.0, abs(price_change_pct) / (self.crash_threshold_pct * 2))
                        events.append(
                            self._create_event(
                                symbol=sym,
                                timestamp=tick.timestamp,
                                event_type=IntelligenceEventType.CRASH,
                                confidence=confidence,
                                metadata={
                                    "price_change_pct": round(price_change_pct, 6),
                                    "prev_price": last_tick.mid_price,
                                    "curr_price": tick.mid_price,
                                },
                            )
                        )

                # 3. GAP
                try:
                    t1 = datetime.datetime.fromisoformat(last_tick.timestamp.replace("Z", "+00:00"))
                    t2 = datetime.datetime.fromisoformat(tick.timestamp.replace("Z", "+00:00"))
                    delta_sec = (t2 - t1).total_seconds()
                    if delta_sec >= self.gap_threshold_sec:
                        confidence = min(1.0, delta_sec / (self.gap_threshold_sec * 3))
                        events.append(
                            self._create_event(
                                symbol=sym,
                                timestamp=tick.timestamp,
                                event_type=IntelligenceEventType.GAP,
                                confidence=confidence,
                                metadata={
                                    "time_gap_seconds": round(delta_sec, 2),
                                    "threshold_seconds": self.gap_threshold_sec,
                                },
                            )
                        )
                except Exception:
                    pass

            # 4. SPREAD_ANOMALY
            if current_stats and current_stats.mean_spread > 0:
                if tick.spread >= current_stats.mean_spread * self.spread_anomaly_mult:
                    confidence = min(1.0, tick.spread / (current_stats.mean_spread * self.spread_anomaly_mult * 2))
                    events.append(
                        self._create_event(
                            symbol=sym,
                            timestamp=tick.timestamp,
                            event_type=IntelligenceEventType.SPREAD_ANOMALY,
                            confidence=confidence,
                            metadata={
                                "spread": tick.spread,
                                "mean_spread": current_stats.mean_spread,
                                "multiplier": round(tick.spread / current_stats.mean_spread, 2),
                            },
                        )
                    )

        return events

    def process_candle(self, candle: IntelligenceCandle, current_stats: MarketStatistics | None = None) -> list[MarketEvent]:
        """Evaluate finalized IntelligenceCandle for extreme candle range."""
        events: list[MarketEvent] = []
        sym = candle.symbol.upper()

        if current_stats and current_stats.average_candle_size > 0:
            c_range = candle.price_range
            avg_sz = current_stats.average_candle_size
            if c_range >= avg_sz * self.extreme_candle_mult:
                confidence = min(1.0, c_range / (avg_sz * self.extreme_candle_mult * 2))
                events.append(
                    self._create_event(
                        symbol=sym,
                        timestamp=candle.close_timestamp,
                        event_type=IntelligenceEventType.EXTREME_CANDLE,
                        confidence=confidence,
                        metadata={
                            "candle_range": c_range,
                            "average_candle_size": avg_sz,
                            "multiplier": round(c_range / avg_sz, 2),
                            "timeframe": candle.timeframe.value,
                        },
                    )
                )
        return events

    def process_statistics(self, stats: MarketStatistics) -> list[MarketEvent]:
        """Evaluate updated MarketStatistics for Volatility Expansion or Contraction."""
        events: list[MarketEvent] = []
        sym = stats.symbol.upper()

        with self._lock:
            last_stat = self._last_stats.get(sym)
            self._last_stats[sym] = stats

            if last_stat and last_stat.rolling_volatility > 0 and stats.rolling_volatility > 0:
                vol_ratio = stats.rolling_volatility / last_stat.rolling_volatility

                # VOLATILITY_EXPANSION
                if vol_ratio >= self.vol_expansion_mult:
                    confidence = min(1.0, vol_ratio / (self.vol_expansion_mult * 2))
                    events.append(
                        self._create_event(
                            symbol=sym,
                            timestamp=stats.timestamp,
                            event_type=IntelligenceEventType.VOLATILITY_EXPANSION,
                            confidence=confidence,
                            metadata={
                                "volatility_ratio": round(vol_ratio, 4),
                                "prev_volatility": last_stat.rolling_volatility,
                                "curr_volatility": stats.rolling_volatility,
                            },
                        )
                    )

                # VOLATILITY_CONTRACTION
                if vol_ratio <= self.vol_contraction_mult:
                    confidence = min(1.0, (1.0 / max(vol_ratio, 1e-4)) / (1.0 / self.vol_contraction_mult * 2))
                    events.append(
                        self._create_event(
                            symbol=sym,
                            timestamp=stats.timestamp,
                            event_type=IntelligenceEventType.VOLATILITY_CONTRACTION,
                            confidence=confidence,
                            metadata={
                                "volatility_ratio": round(vol_ratio, 4),
                                "prev_volatility": last_stat.rolling_volatility,
                                "curr_volatility": stats.rolling_volatility,
                            },
                        )
                    )
        return events

    def record_connection_interruption(self, symbol: str, reason: str = "WebSocket Disconnected") -> MarketEvent:
        """Explicitly record a CONNECTION_INTERRUPTION event."""
        ts_now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return self._create_event(
            symbol=symbol.upper(),
            timestamp=ts_now,
            event_type=IntelligenceEventType.CONNECTION_INTERRUPTION,
            confidence=1.0,
            metadata={"reason": reason},
        )

    def record_market_pause(self, symbol: str, duration_seconds: float) -> MarketEvent:
        """Explicitly record a MARKET_PAUSE event."""
        ts_now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return self._create_event(
            symbol=symbol.upper(),
            timestamp=ts_now,
            event_type=IntelligenceEventType.MARKET_PAUSE,
            confidence=min(1.0, duration_seconds / self.pause_duration_sec),
            metadata={"pause_duration_seconds": round(duration_seconds, 2)},
        )

    def _create_event(
        self,
        symbol: str,
        timestamp: str,
        event_type: IntelligenceEventType,
        confidence: float,
        metadata: dict[str, Any],
    ) -> MarketEvent:
        event_id, canon_hash = compute_market_event_id(
            symbol=symbol,
            timestamp=timestamp,
            event_type=event_type,
            confidence=confidence,
        )

        checksum = compute_canonical_sha256(
            {
                "confidence": round(float(confidence), 4),
                "event_type": event_type.value,
                "symbol": symbol,
                "timestamp": timestamp,
            }
        )

        event = MarketEvent(
            event_id=event_id,
            timestamp=timestamp,
            symbol=symbol,
            event_type=event_type,
            confidence=round(float(confidence), 4),
            checksum=checksum,
            metadata=metadata,
            canonical_hash=canon_hash,
        )

        if self.repository:
            self.repository.save_event(event)

        return event
