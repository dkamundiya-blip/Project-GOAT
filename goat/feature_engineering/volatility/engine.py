"""
Project GOAT Phase 5 — Volatility Feature Engine (`goat.feature_engineering.volatility`)

Engineers 9 quantitative volatility features:
ATR Percentile, Volatility Expansion, Volatility Compression, Historical Volatility,
Realized Volatility, Rolling Variance, Rolling Standard Deviation, Volatility Regime,
and Volatility Burst Detection.
"""

from __future__ import annotations

from collections import deque
import math
import threading

from goat.market_intelligence.models.candle import IntelligenceCandle
from goat.market_intelligence.models.statistics import MarketStatistics


class VolatilityFeatureEngine:
    """Quantitative Volatility Feature Engine for multi-dimensional volatility analysis."""

    def __init__(self, window_size: int = 50, atr_window: int = 100):
        self.window_size = window_size
        self.atr_window = atr_window

        self._atr_history: dict[tuple[str, str], deque[float]] = {}
        self._price_windows: dict[tuple[str, str], deque[float]] = {}
        self._log_returns: dict[tuple[str, str], deque[float]] = {}
        self._lock = threading.RLock()

    def compute_features(
        self,
        candle: IntelligenceCandle,
        current_stats: MarketStatistics | None = None,
    ) -> dict[str, float]:
        """Compute 9 quantitative volatility features."""
        key = (candle.symbol.upper(), candle.timeframe.value.lower())
        c_price = candle.close

        with self._lock:
            if key not in self._price_windows:
                self._price_windows[key] = deque(maxlen=self.window_size)
                self._log_returns[key] = deque(maxlen=self.window_size)
                self._atr_history[key] = deque(maxlen=self.atr_window)

            prices = self._price_windows[key]
            log_rets = self._log_returns[key]
            atr_hist = self._atr_history[key]

            if len(prices) > 0 and prices[-1] > 0 and c_price > 0:
                ret = math.log(c_price / prices[-1])
                log_rets.append(ret)

            prices.append(c_price)
            n = len(prices)

            # 1. Rolling Variance & Standard Deviation
            mean_p = sum(prices) / n
            var_p = sum((p - mean_p) ** 2 for p in prices) / n if n > 1 else 0.0
            std_p = math.sqrt(var_p)

            # 2. Historical & Realized Volatility
            realized_vol = sum(r ** 2 for r in log_rets) if log_rets else 0.0
            if len(log_rets) > 1:
                mean_r = sum(log_rets) / len(log_rets)
                var_r = sum((r - mean_r) ** 2 for r in log_rets) / len(log_rets)
                hist_vol = math.sqrt(var_r) * math.sqrt(252 * 1440)  # Annualized min-based
            else:
                hist_vol = 0.0

            # 3. ATR & Percentile
            current_atr = current_stats.atr if current_stats else candle.price_range
            atr_hist.append(current_atr)
            sorted_atrs = sorted(atr_hist)
            rank = sorted_atrs.index(current_atr) if current_atr in sorted_atrs else 0
            atr_percentile = rank / len(sorted_atrs) if sorted_atrs else 0.5

            # 4. Volatility Expansion & Compression
            short_win = list(log_rets)[-10:]
            long_win = list(log_rets)
            short_vol = math.sqrt(sum(r ** 2 for r in short_win) / len(short_win)) if short_win else 0.0
            long_vol = math.sqrt(sum(r ** 2 for r in long_win) / len(long_win)) if long_win else 1e-6

            vol_expansion = short_vol / max(long_vol, 1e-6)
            vol_compression = 1.0 / max(vol_expansion, 1e-6)

            # 5. Volatility Regime & Burst Detection
            if vol_expansion >= 2.0:
                regime = 1.0  # HIGH
            elif vol_expansion <= 0.6:
                regime = 0.0  # LOW
            else:
                regime = 0.5  # MEDIUM

            burst_detected = 1.0 if vol_expansion >= 2.5 else 0.0

            return {
                "atr_percentile": round(atr_percentile, 4),
                "volatility_expansion": round(vol_expansion, 6),
                "volatility_compression": round(vol_compression, 6),
                "historical_volatility": round(hist_vol, 6),
                "realized_volatility": round(realized_vol, 8),
                "rolling_variance": round(var_p, 8),
                "rolling_std": round(std_p, 8),
                "volatility_regime": regime,
                "volatility_burst_detection": burst_detected,
            }
