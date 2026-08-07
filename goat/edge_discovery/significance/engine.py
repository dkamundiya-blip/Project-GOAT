"""
Project GOAT Phase 6 — Statistical Significance Engine (`goat.edge_discovery.significance`)

Performs rigorous statistical testing: Bootstrap confidence intervals, Monte Carlo simulations,
Student's t-test p-values, Cohen's d effect sizes, and statistical power calculations.
"""

from __future__ import annotations

import math
import random
from typing import Sequence


class StatisticalSignificanceEngine:
    """Quantitative Statistical Significance Engine validating statistical significance and robustness."""

    def __init__(self, bootstrap_resamples: int = 1000, alpha: float = 0.05):
        self.bootstrap_resamples = bootstrap_resamples
        self.alpha = alpha

    def evaluate_significance(self, returns: Sequence[float]) -> dict[str, float]:
        """Perform statistical significance testing on a sequence of edge returns.

        Returns:
            Dictionary containing p_value, ci_low, ci_high, effect_size, std_error, power, monte_carlo_score.
        """
        n = len(returns)
        if n < 5:
            return {
                "p_value": 1.0,
                "confidence_interval_low": 0.0,
                "confidence_interval_high": 0.0,
                "effect_size": 0.0,
                "standard_error": 0.0,
                "statistical_power": 0.0,
                "monte_carlo_score": 0.0,
            }

        mean_r = sum(returns) / n
        var_r = sum((r - mean_r) ** 2 for r in returns) / (n - 1) if n > 1 else 0.0
        std_r = math.sqrt(var_r)
        std_error = std_r / math.sqrt(n) if n > 0 else 0.0

        # 1. Cohen's d Effect Size
        effect_size = (mean_r / max(std_r, 1e-6)) if std_r > 0 else 0.0

        # 2. Student's t-statistic & Approximate P-Value (one-sided against H0: mean <= 0)
        t_stat = mean_r / max(std_error, 1e-6) if std_error > 0 else 0.0
        # Standard normal approximation for large N
        p_value = 0.5 * math.erfc(t_stat / math.sqrt(2.0))

        # 3. Bootstrap Confidence Interval (95%)
        bootstrap_means: list[float] = []
        rnd = random.Random(42)  # Deterministic seed for reproducible testing
        ret_list = list(returns)

        for _ in range(self.bootstrap_resamples):
            resample = [rnd.choice(ret_list) for _ in range(n)]
            bootstrap_means.append(sum(resample) / n)

        bootstrap_means.sort()
        low_idx = int(self.bootstrap_resamples * (self.alpha / 2.0))
        high_idx = int(self.bootstrap_resamples * (1.0 - self.alpha / 2.0))

        ci_low = bootstrap_means[low_idx]
        ci_high = bootstrap_means[high_idx]

        # 4. Statistical Power Estimate
        # Power approximation based on non-central t distribution Z-score
        z_alpha = 1.645  # 95% one-sided Z threshold
        power_z = (t_stat - z_alpha)
        statistical_power = 0.5 * (1.0 + math.erf(power_z / math.sqrt(2.0)))
        statistical_power = max(0.0, min(1.0, statistical_power))

        # 5. Monte Carlo Permutation Score
        # Fraction of randomized trials where permuted mean < actual mean
        mc_pass_count = 0
        mc_trials = 200
        for _ in range(mc_trials):
            permuted = [r * (1.0 if rnd.random() > 0.5 else -1.0) for r in ret_list]
            if mean_r > (sum(permuted) / n):
                mc_pass_count += 1
        monte_carlo_score = mc_pass_count / mc_trials

        return {
            "p_value": round(p_value, 6),
            "confidence_interval_low": round(ci_low, 6),
            "confidence_interval_high": round(ci_high, 6),
            "effect_size": round(effect_size, 4),
            "standard_error": round(std_error, 6),
            "statistical_power": round(statistical_power, 4),
            "monte_carlo_score": round(monte_carlo_score, 4),
        }
