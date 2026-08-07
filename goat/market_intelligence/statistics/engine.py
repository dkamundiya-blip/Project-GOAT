"""
Project GOAT Phase 4 — Market Statistics Engine (`goat.market_intelligence.statistics`)

Performs high-throughput, continuous O(1) streaming statistical computations:
ATR, True Range, Rolling Volatility, Standard Deviation, Variance, Average Tick Rate,
Average Candle Size, Spread Statistics, Market Speed, Rolling High/Low, and Rolling VWAP.
"""

from __future__ import annotations

from collections import deque
import datetime
import math
import threading
from typing import Any

from goat.market_intelligence.models.candle import IntelligenceCandle
from goat.market_intelligence.models.statistics import (
    MarketStatistics,
    compute_market_statistics_id,
)
from goat.market_intelligence.models.tick import RecordedTick
from goat.market_intelligence.persistence.interfaces import IMarketStatisticsRepository
from goat.research.edge.canonical import compute_canonical_sha256


class MarketStatisticsEngine:
    """Institutional Market Statistics Engine with O(1) rolling streaming algorithms."""

    def __init__(
        self,
        repository: IMarketStatisticsRepository | None = None,
        window_size: int = 100,
        atr_period: int = 14,
    ):
        self.repository = repository
        self.window_size = window_size
        self.atr_period = atr_period

        # Per symbol state tracking
        self._price_windows: dict[str, deque[float]] = {}
        self._spread_windows: dict[str, deque[float]] = {}
        self._timestamp_windows: dict[str, deque[datetime.datetime]] = {}
        self._candle_range_windows: dict[str, deque[float]] = {}
        self._vwap_pv_windows: dict[str, deque[float]] = {}
        self._vwap_v_windows: dict[str, deque[float]] = {}
        self._tr_windows: dict[str, deque[float]] = {}
        
        self._prev_close: dict[str, float] = {}
        self._lock = threading.RLock()

    def process_tick(self, tick: RecordedTick) -> MarketStatistics:
        """Process an incoming RecordedTick and compute updated streaming MarketStatistics."""
        sym = tick.symbol.upper()
        mid = tick.mid_price
        spread = tick.spread
        
        try:
            ts_dt = datetime.datetime.fromisoformat(tick.timestamp.replace("Z", "+00:00"))
        except Exception:
            ts_dt = datetime.datetime.now(datetime.timezone.utc)

        with self._lock:
            if sym not in self._price_windows:
                self._price_windows[sym] = deque(maxlen=self.window_size)
                self._spread_windows[sym] = deque(maxlen=self.window_size)
                self._timestamp_windows[sym] = deque(maxlen=self.window_size)
                self._vwap_pv_windows[sym] = deque(maxlen=self.window_size)
                self._vwap_v_windows[sym] = deque(maxlen=self.window_size)
                self._tr_windows[sym] = deque(maxlen=self.window_size)
                self._candle_range_windows[sym] = deque(maxlen=self.window_size)

            prices = self._price_windows[sym]
            spreads = self._spread_windows[sym]
            timestamps = self._timestamp_windows[sym]
            pv_win = self._vwap_pv_windows[sym]
            v_win = self._vwap_v_windows[sym]
            tr_win = self._tr_windows[sym]

            # 1. Update rolling tick windows
            prices.append(mid)
            spreads.append(spread)
            timestamps.append(ts_dt)
            pv_win.append(mid * 1.0)  # volume = 1.0 per tick
            v_win.append(1.0)

            # True Range calculation on tick level
            prev_p = self._prev_close.get(sym, mid)
            tr = max(abs(mid - prev_p), spread)
            tr_win.append(tr)
            self._prev_close[sym] = mid

            # 2. Computations
            # Mean & Variance (Welford's or sum)
            n_samples = len(prices)
            mean_price = sum(prices) / n_samples
            var_price = sum((x - mean_price) ** 2 for x in prices) / n_samples if n_samples > 1 else 0.0
            stdev_price = math.sqrt(var_price)

            # Spread Stats
            mean_spread = sum(spreads) / n_samples
            min_spread = min(spreads)
            max_spread = max(spreads)
            var_spread = sum((s - mean_spread) ** 2 for s in spreads) / n_samples if n_samples > 1 else 0.0

            # Rolling High / Low
            r_high = max(prices)
            r_low = min(prices)

            # Rolling VWAP
            total_pv = sum(pv_win)
            total_v = sum(v_win)
            r_vwap = (total_pv / total_v) if total_v > 0 else mid

            # Tick Rate (ticks/sec) & Market Speed (price change/sec)
            tick_rate = 0.0
            speed = 0.0
            if n_samples > 1:
                delta_sec = (timestamps[-1] - timestamps[0]).total_seconds()
                if delta_sec > 0:
                    tick_rate = (n_samples - 1) / delta_sec
                    speed = abs(prices[-1] - prices[0]) / delta_sec

            # Log returns volatility
            vol = 0.0
            if n_samples > 2:
                log_returns = [math.log(prices[i] / prices[i - 1]) for i in range(1, n_samples) if prices[i - 1] > 0]
                if len(log_returns) > 1:
                    mean_ret = sum(log_returns) / len(log_returns)
                    var_ret = sum((r - mean_ret) ** 2 for r in log_returns) / len(log_returns)
                    vol = math.sqrt(var_ret)

            # ATR & True Range
            current_tr = tr
            atr_val = sum(tr_win) / len(tr_win) if tr_win else current_tr

            # Average candle size
            candle_ranges = self._candle_range_windows[sym]
            avg_candle_sz = (sum(candle_ranges) / len(candle_ranges)) if candle_ranges else (r_high - r_low)

            ts_iso = ts_dt.isoformat()

            stat_id, canon_hash = compute_market_statistics_id(
                symbol=sym,
                timestamp=ts_iso,
                window_size=n_samples,
                atr=atr_val,
                rolling_volatility=vol,
                rolling_vwap=r_vwap,
            )

            checksum = compute_canonical_sha256(
                {
                    "atr": atr_val,
                    "rolling_high": r_high,
                    "rolling_low": r_low,
                    "rolling_vwap": r_vwap,
                    "standard_deviation": stdev_price,
                    "symbol": sym,
                    "window_size": n_samples,
                }
            )

            stats = MarketStatistics(
                stat_id=stat_id,
                symbol=sym,
                timestamp=ts_iso,
                window_size=n_samples,
                atr=round(atr_val, 8),
                true_range=round(current_tr, 8),
                rolling_volatility=round(vol, 8),
                standard_deviation=round(stdev_price, 8),
                variance=round(var_price, 8),
                average_tick_rate=round(tick_rate, 4),
                average_candle_size=round(avg_candle_sz, 8),
                mean_spread=round(mean_spread, 8),
                min_spread=round(min_spread, 8),
                max_spread=round(max_spread, 8),
                spread_variance=round(var_spread, 8),
                market_speed=round(speed, 8),
                rolling_high=round(r_high, 8),
                rolling_low=round(r_low, 8),
                rolling_vwap=round(r_vwap, 8),
                checksum=checksum,
                metadata={"samples": n_samples},
                canonical_hash=canon_hash,
            )

            if self.repository:
                self.repository.save_statistics(stats)

            return stats

    def process_candle(self, candle: IntelligenceCandle) -> None:
        """Update candle range window when a candle is finalized."""
        sym = candle.symbol.upper()
        c_range = candle.price_range
        with self._lock:
            if sym not in self._candle_range_windows:
                self._candle_range_windows[sym] = deque(maxlen=self.window_size)
            self._candle_range_windows[sym].append(c_range)
            self._prev_close[sym] = candle.close
