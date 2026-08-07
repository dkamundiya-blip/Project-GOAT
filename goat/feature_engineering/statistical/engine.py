"""
Project GOAT Phase 5 — Statistical Feature Engine (`goat.feature_engineering.statistical`)

Engineers 10 quantitative statistical features:
Z-score, Percentile Rank, Rolling Mean, Rolling Median, Rolling Entropy,
Hurst Exponent, Mean Reversion Score, Autocorrelation, Distribution Skew, and Distribution Kurtosis.
"""

from __future__ import annotations

from collections import deque
import math
import threading

from goat.market_intelligence.models.candle import IntelligenceCandle


class StatisticalFeatureEngine:
    """Quantitative Statistical Feature Engine computing distribution moments, entropy, and Hurst exponent."""

    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self._price_windows: dict[tuple[str, str], deque[float]] = {}
        self._return_windows: dict[tuple[str, str], deque[float]] = {}
        self._lock = threading.RLock()

    def compute_features(self, candle: IntelligenceCandle) -> dict[str, float]:
        """Compute 10 quantitative statistical features."""
        key = (candle.symbol.upper(), candle.timeframe.value.lower())
        c_price = candle.close

        with self._lock:
            if key not in self._price_windows:
                self._price_windows[key] = deque(maxlen=self.window_size)
                self._return_windows[key] = deque(maxlen=self.window_size)

            prices = self._price_windows[key]
            returns = self._return_windows[key]

            if len(prices) > 0 and prices[-1] > 0 and c_price > 0:
                r = math.log(c_price / prices[-1])
                returns.append(r)

            prices.append(c_price)
            n = len(prices)

            # 1. Rolling Mean & Median
            rolling_mean = sum(prices) / n
            sorted_p = sorted(prices)
            rolling_median = sorted_p[n // 2] if n % 2 != 0 else (sorted_p[n // 2 - 1] + sorted_p[n // 2]) / 2.0

            # 2. Z-Score & Percentile Rank
            var_p = sum((p - rolling_mean) ** 2 for p in prices) / n if n > 1 else 0.0
            std_p = math.sqrt(var_p)
            z_score = (c_price - rolling_mean) / max(std_p, 1e-6)

            rank_idx = sorted_p.index(c_price) if c_price in sorted_p else 0
            percentile_rank = rank_idx / max(n - 1, 1)

            # 3. Mean Reversion Score
            mean_reversion_score = -z_score  # High positive score when price is below mean

            # 4. Distribution Skew & Kurtosis
            skew = 0.0
            kurtosis = 0.0
            if n > 2 and std_p > 1e-6:
                m3 = sum((p - rolling_mean) ** 3 for p in prices) / n
                m4 = sum((p - rolling_mean) ** 4 for p in prices) / n
                skew = m3 / (std_p ** 3)
                kurtosis = (m4 / (std_p ** 4)) - 3.0

            # 5. Lag-1 Autocorrelation of Returns
            autocorr = 0.0
            if len(returns) > 3:
                r_list = list(returns)
                mean_r = sum(r_list) / len(r_list)
                denom = sum((x - mean_r) ** 2 for x in r_list)
                if denom > 1e-8:
                    num = sum((r_list[i] - mean_r) * (r_list[i - 1] - mean_r) for i in range(1, len(r_list)))
                    autocorr = num / denom

            # 6. Rolling Shannon Entropy of Returns
            entropy = 0.0
            if len(returns) >= 10:
                # Bin returns into 5 histogram bins
                min_r, max_r = min(returns), max(returns)
                span = max(max_r - min_r, 1e-6)
                bins = [0] * 5
                for r in returns:
                    b_idx = min(4, int((r - min_r) / span * 5))
                    bins[b_idx] += 1
                total_r = len(returns)
                entropy = -sum((cnt / total_r) * math.log2(cnt / total_r) for cnt in bins if cnt > 0)

            # 7. Hurst Exponent (Rescaled Range R/S)
            hurst = 0.5  # Random walk default
            if n >= 20:
                # R/S calculation
                devs = [p - rolling_mean for p in prices]
                cum_devs = [sum(devs[:i+1]) for i in range(n)]
                R = max(cum_devs) - min(cum_devs)
                S = max(std_p, 1e-6)
                RS = R / S
                if RS > 0:
                    hurst = math.log(RS) / math.log(n)
                    hurst = max(0.0, min(1.0, hurst))

            return {
                "z_score": round(z_score, 4),
                "percentile_rank": round(percentile_rank, 4),
                "rolling_mean": round(rolling_mean, 8),
                "rolling_median": round(rolling_median, 8),
                "rolling_entropy": round(entropy, 4),
                "hurst_exponent": round(hurst, 4),
                "mean_reversion_score": round(mean_reversion_score, 4),
                "autocorrelation": round(autocorr, 4),
                "distribution_skew": round(skew, 4),
                "distribution_kurtosis": round(kurtosis, 4),
            }
