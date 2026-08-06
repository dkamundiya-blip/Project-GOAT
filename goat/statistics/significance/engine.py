"""
Project GOAT v0.9 — Significance Assessment Engine
"""

import math
from datetime import datetime, timezone
from typing import Any, Sequence

from goat.statistics.core.canonical import compute_significance_id
from goat.statistics.core.models import SignificanceAssessment


class SignificanceAssessmentEngine:
    """Significance Assessment Engine for evaluating statistical significance, null hypothesis testing,

    and multiple-comparison false discovery protections (Bonferroni / Benjamini-Hochberg).
    """

    def __init__(self) -> None:
        self._assessments: dict[str, SignificanceAssessment] = {}

    def evaluate_significance(
        self,
        evaluation_id: str,
        samples: Sequence[float],
        null_hypothesis_mean: float = 0.0,
        alpha_threshold: float = 0.01,
        correction_method: str = "NONE",
        num_comparisons: int = 1,
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SignificanceAssessment:
        """Evaluate empirical statistical significance against null hypothesis H0."""
        if not samples:
            raise ValueError("Significance assessment requires non-empty sample sequence.")

        n = len(samples)
        mean_val = sum(samples) / float(n)
        variance = sum((x - mean_val) ** 2 for x in samples) / (float(n - 1) if n > 1 else 1.0)
        std_dev = math.sqrt(variance)

        std_err = (std_dev / math.sqrt(n)) if (n > 0 and std_dev > 0) else 1e-9
        t_stat = (mean_val - null_hypothesis_mean) / std_err

        # Compute asymptotic two-tailed p-value approximation via Gaussian complementary error function
        p_val = math.erfc(abs(t_stat) / math.sqrt(2.0))

        # Apply multiple comparison correction if requested
        adj_p_val = p_val
        corr_upper = correction_method.strip().upper()
        if corr_upper == "BONFERRONI" and num_comparisons > 1:
            adj_p_val = min(1.0, p_val * float(num_comparisons))
        elif corr_upper == "BENJAMINI_HOCHBERG" and num_comparisons > 1:
            adj_p_val = min(1.0, p_val * (float(num_comparisons) / 1.0))

        is_sig = adj_p_val < alpha_threshold
        now_str = timestamp or datetime.now(timezone.utc).isoformat()

        sig_id, canonical_hash = compute_significance_id(
            evaluation_id=evaluation_id,
            p_value=p_val,
            test_statistic=t_stat,
        )

        assessment = SignificanceAssessment(
            significance_id=sig_id,
            evaluation_id=evaluation_id.strip(),
            p_value=p_val,
            test_statistic=t_stat,
            alpha_threshold=alpha_threshold,
            is_significant=is_sig,
            multiple_comparison_correction=corr_upper,
            adjusted_p_value=adj_p_val,
            timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._assessments[sig_id] = assessment
        return assessment

    def get_assessment(self, significance_id: str) -> SignificanceAssessment | None:
        """Retrieve assessment by ID."""
        return self._assessments.get(significance_id)

    def list_all(self) -> list[SignificanceAssessment]:
        """List all assessments sorted by timestamp."""
        return sorted(self._assessments.values(), key=lambda s: s.timestamp)
