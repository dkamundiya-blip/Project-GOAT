"""
Project GOAT Phase 5 — Trend Feature Engine (`goat.feature_engineering.trend`)

Engineers 10 quantitative trend features:
Trend Direction, Trend Strength, Slope, Rolling Slope, EMA Distance, Moving Average Alignment,
Trend Persistence, Trend Age, Trend Stability, and Directional Efficiency.
"""

from __future__ import annotations

from collections import deque
import math
import threading
from typing import Sequence

from goat.market_intelligence.models.candle import IntelligenceCandle


class TrendFeatureEngine:
    """Quantitative Trend Feature Engine executing O(1) streaming calculations."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self._price_windows: dict[tuple[str, str], deque[float]] = {}
        self._slope_windows: dict[tuple[str, str], deque[float]] = {}
        self._ema_5: dict[tuple[str, str], float] = {}
        self._ema_20: dict[tuple[str, str], float] = {}
        self._ema_50: dict[tuple[str, str], float] = {}
        self._last_direction: dict[tuple[str, str], float] = {}
        self._trend_age: dict[tuple[str, str], int] = {}
        self._trend_persistence: dict[tuple[str, str], int] = {}
        self._lock = threading.RLock()

    def compute_features(self, candle: IntelligenceCandle) -> dict[str, float]:
        """Compute 10 quantitative trend features for a given candle."""
        key = (candle.symbol.upper(), candle.timeframe.value.lower())
        c_price = candle.close

        with self._lock:
            if key not in self._price_windows:
                self._price_windows[key] = deque(maxlen=self.window_size)
                self._slope_windows[key] = deque(maxlen=10)
                self._ema_5[key] = c_price
                self._ema_20[key] = c_price
                self._ema_50[key] = c_price
                self._last_direction[key] = 0.0
                self._trend_age[key] = 0
                self._trend_persistence[key] = 0

            prices = self._price_windows[key]
            prices.append(c_price)
            n = len(prices)

            # Update Exponential Moving Averages (EMA)
            self._ema_5[key] = (c_price * (2 / 6)) + (self._ema_5[key] * (1 - (2 / 6)))
            self._ema_20[key] = (c_price * (2 / 21)) + (self._ema_20[key] * (1 - (2 / 21)))
            self._ema_50[key] = (c_price * (2 / 51)) + (self._ema_50[key] * (1 - (2 / 51)))

            ema5 = self._ema_5[key]
            ema20 = self._ema_20[key]
            ema50 = self._ema_50[key]

            # 1. Slope & Stability (R-squared)
            slope = 0.0
            r_squared = 0.0
            if n > 1:
                xs = list(range(n))
                mean_x = (n - 1) / 2.0
                mean_y = sum(prices) / n
                var_x = sum((x - mean_x) ** 2 for x in xs)
                cov_xy = sum((xs[i] - mean_x) * (prices[i] - mean_y) for i in range(n))
                slope = cov_xy / var_x if var_x > 0 else 0.0

                var_y = sum((y - mean_y) ** 2 for y in prices)
                if var_y > 0 and var_x > 0:
                    r_squared = min(1.0, max(0.0, (cov_xy ** 2) / (var_x * var_y)))

            slope_win = self._slope_windows[key]
            slope_win.append(slope)
            rolling_slope = sum(slope_win) / len(slope_win)

            # 2. Trend Direction & Strength
            if slope > 1e-6:
                direction = 1.0
            elif slope < -1e-6:
                direction = -1.0
            else:
                direction = 0.0

            trend_strength = math.sqrt(r_squared) * (abs(slope) / (c_price * 0.01 + 1e-6))
            trend_strength = min(1.0, max(0.0, trend_strength))

            # 3. EMA Distance
            ema_distance = (c_price - ema20) / max(ema20, 1e-6)

            # 4. Moving Average Alignment
            if ema5 > ema20 > ema50:
                ma_alignment = 1.0
            elif ema5 < ema20 < ema50:
                ma_alignment = -1.0
            else:
                ma_alignment = 0.0

            # 5. Trend Persistence & Age
            prev_dir = self._last_direction[key]
            if direction == prev_dir and direction != 0.0:
                self._trend_persistence[key] += 1
                self._trend_age[key] += 1
            elif direction != 0.0:
                self._trend_persistence[key] = 1
                self._trend_age[key] = 1
                self._last_direction[key] = direction
            else:
                self._trend_age[key] += 1

            # 6. Directional Efficiency (Kaufman Efficiency Ratio)
            net_change = abs(prices[-1] - prices[0])
            sum_diffs = sum(abs(prices[i] - prices[i - 1]) for i in range(1, n))
            directional_efficiency = net_change / sum_diffs if sum_diffs > 0 else 1.0

            return {
                "trend_direction": round(direction, 4),
                "trend_strength": round(trend_strength, 4),
                "slope": round(slope, 8),
                "rolling_slope": round(rolling_slope, 8),
                "ema_distance": round(ema_distance, 6),
                "ma_alignment": round(ma_alignment, 4),
                "trend_persistence": float(self._trend_persistence[key]),
                "trend_age": float(self._trend_age[key]),
                "trend_stability": round(r_squared, 6),
                "directional_efficiency": round(directional_efficiency, 6),
            }
