"""
Project GOAT Phase 5 — Liquidity Feature Engine (`goat.feature_engineering.liquidity`)

Engineers 8 quantitative liquidity features:
Equal Highs, Equal Lows, Liquidity Sweeps, Liquidity Density, Range Compression,
Range Expansion, Stop Cluster Probability, and Liquidity Imbalance.
"""

from __future__ import annotations

from collections import deque
import threading

from goat.market_intelligence.models.candle import IntelligenceCandle


class LiquidityFeatureEngine:
    """Quantitative Liquidity Feature Engine identifying EQH/EQL, liquidity sweeps, and density metrics."""

    def __init__(self, tolerance_pct: float = 0.0005, window_size: int = 20):
        self.tolerance_pct = tolerance_pct
        self.window_size = window_size

        self._candle_history: dict[tuple[str, str], deque[IntelligenceCandle]] = {}
        self._lock = threading.RLock()

    def compute_features(self, candle: IntelligenceCandle) -> dict[str, float]:
        """Compute 8 quantitative liquidity features."""
        key = (candle.symbol.upper(), candle.timeframe.value.lower())

        with self._lock:
            if key not in self._candle_history:
                self._candle_history[key] = deque(maxlen=self.window_size)

            history = self._candle_history[key]
            history.append(candle)
            n = len(history)

            ranges = [c.price_range for c in history]
            volumes = [c.volume if c.volume > 0 else 1.0 for c in history]

            # 1. Equal Highs (EQH) & Equal Lows (EQL) Detection
            eqh_score = 0.0
            eql_score = 0.0
            eqh_price = 0.0
            eql_price = 0.0

            highs = [c.high for c in history]
            lows = [c.low for c in history]

            for i in range(n - 1):
                if abs(candle.high - highs[i]) / max(candle.high, 1e-6) <= self.tolerance_pct:
                    eqh_score = 1.0
                    eqh_price = max(candle.high, highs[i])
                    break

            for i in range(n - 1):
                if abs(candle.low - lows[i]) / max(candle.low, 1e-6) <= self.tolerance_pct:
                    eql_score = 1.0
                    eql_price = min(candle.low, lows[i])
                    break

            # 2. Liquidity Sweep Detection
            sweep_signal = 0.0
            if n > 1:
                prev_min_low = min(lows[:-1])
                prev_max_high = max(highs[:-1])

                # Bullish Sweep: price dips below previous low then closes back above it
                if candle.low < prev_min_low and candle.close > prev_min_low:
                    sweep_signal = 1.0
                # Bearish Sweep: price spikes above previous high then closes back below it
                elif candle.high > prev_max_high and candle.close < prev_max_high:
                    sweep_signal = -1.0

            # 3. Liquidity Density & Range Compression/Expansion
            c_range = max(candle.price_range, 1e-6)
            c_vol = candle.volume if candle.volume > 0 else 1.0
            liquidity_density = c_vol / c_range

            mean_range = sum(ranges) / n
            min_range = max(min(ranges), 1e-6)

            range_compression = c_range / max(mean_range, 1e-6)
            range_expansion = c_range / min_range

            # 4. Stop Cluster Probability
            if eqh_score > 0.0 or eql_score > 0.0:
                stop_cluster_prob = 0.85
            elif range_compression < 0.5:
                stop_cluster_prob = 0.65
            else:
                stop_cluster_prob = 0.20

            # 5. Liquidity Imbalance (Wick asymmetry: upper wick vs lower wick)
            body_top = max(candle.open, candle.close)
            body_bottom = min(candle.open, candle.close)
            upper_wick = candle.high - body_top
            lower_wick = body_bottom - candle.low

            imbalance_denom = upper_wick + lower_wick
            liquidity_imbalance = (upper_wick - lower_wick) / imbalance_denom if imbalance_denom > 0 else 0.0

            return {
                "equal_highs": eqh_score,
                "equal_lows": eql_score,
                "liquidity_sweep": sweep_signal,
                "liquidity_density": round(liquidity_density, 4),
                "range_compression": round(range_compression, 4),
                "range_expansion": round(range_expansion, 4),
                "stop_cluster_prob": round(stop_cluster_prob, 4),
                "liquidity_imbalance": round(liquidity_imbalance, 4),
            }
