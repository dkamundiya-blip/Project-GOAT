"""
Project GOAT Phase 5 — Momentum Feature Engine (`goat.feature_engineering.momentum`)

Engineers 8 quantitative momentum features:
ROC, Momentum Strength, Momentum Acceleration, Momentum Persistence,
Price Velocity, Price Acceleration, Directional Impulse, and Multi-timeframe Momentum.
"""

from __future__ import annotations

from collections import deque
import math
import threading

from goat.market_intelligence.models.candle import IntelligenceCandle


class MomentumFeatureEngine:
    """Quantitative Momentum Feature Engine providing streaming momentum derivatives."""

    def __init__(self, period: int = 14):
        self.period = period

        self._price_history: dict[tuple[str, str], deque[float]] = {}
        self._roc_history: dict[tuple[str, str], deque[float]] = {}
        self._velocity_history: dict[tuple[str, str], deque[float]] = {}
        self._symbol_momentum: dict[str, dict[str, float]] = {}  # symbol -> {timeframe: momentum}
        self._persistence: dict[tuple[str, str], int] = {}
        self._lock = threading.RLock()

    def compute_features(self, candle: IntelligenceCandle) -> dict[str, float]:
        """Compute 8 quantitative momentum features."""
        key = (candle.symbol.upper(), candle.timeframe.value.lower())
        c_price = candle.close
        volume = candle.volume if candle.volume > 0 else 1.0

        with self._lock:
            if key not in self._price_history:
                self._price_history[key] = deque(maxlen=self.period + 1)
                self._roc_history[key] = deque(maxlen=10)
                self._velocity_history[key] = deque(maxlen=10)
                self._persistence[key] = 0

            prices = self._price_history[key]
            prices.append(c_price)
            n = len(prices)

            # 1. Rate of Change (ROC)
            prev_price = prices[0] if n > 1 else c_price
            roc = (c_price - prev_price) / max(prev_price, 1e-6)

            roc_hist = self._roc_history[key]
            prev_roc = roc_hist[-1] if roc_hist else 0.0
            roc_hist.append(roc)

            # 2. Momentum Acceleration
            momentum_acc = roc - prev_roc

            # 3. Price Velocity & Acceleration
            velocity = (prices[-1] - prices[-2]) if n > 1 else 0.0
            vel_hist = self._velocity_history[key]
            prev_vel = vel_hist[-1] if vel_hist else 0.0
            vel_hist.append(velocity)
            price_acc = velocity - prev_vel

            # 4. Momentum Strength & Persistence
            mom_strength = round(max(-1.0, min(1.0, roc * 100.0)), 4)

            if roc > 0:
                if self._persistence[key] >= 0:
                    self._persistence[key] += 1
                else:
                    self._persistence[key] = 1
            elif roc < 0:
                if self._persistence[key] <= 0:
                    self._persistence[key] -= 1
                else:
                    self._persistence[key] = -1

            # 5. Directional Impulse
            directional_impulse = round(velocity * math.log(1.0 + volume), 6)

            # Track for Multi-timeframe momentum
            sym = candle.symbol.upper()
            if sym not in self._symbol_momentum:
                self._symbol_momentum[sym] = {}
            self._symbol_momentum[sym][candle.timeframe.value.lower()] = mom_strength

            mtf_scores = list(self._symbol_momentum[sym].values())
            mtf_momentum = sum(mtf_scores) / len(mtf_scores) if mtf_scores else mom_strength

            return {
                "roc": round(roc, 6),
                "momentum_strength": mom_strength,
                "momentum_acceleration": round(momentum_acc, 6),
                "momentum_persistence": float(self._persistence[key]),
                "price_velocity": round(velocity, 6),
                "price_acceleration": round(price_acc, 6),
                "directional_impulse": directional_impulse,
                "mtf_momentum": round(mtf_momentum, 4),
            }
