"""
Project GOAT v0.9 — Confidence Assessment Engine
"""

import math
from datetime import datetime, timezone
from typing import Any, Sequence

from goat.statistics.core.canonical import compute_confidence_id
from goat.statistics.core.enums import EvaluationConfidence
from goat.statistics.core.models import ConfidenceAssessment


class ConfidenceAssessmentEngine:
    """Confidence Assessment Engine for calculating, classifying, and reporting deterministic

    confidence intervals and margins of error for empirical observation datasets.
    """

    # Critical z-values for standard confidence levels
    Z_CRITICAL_MAP: dict[float, float] = {
        0.80: 1.282,
        0.85: 1.440,
        0.90: 1.645,
        0.95: 1.960,
        0.98: 2.326,
        0.99: 2.576,
        0.999: 3.291,
    }

    def __init__(self) -> None:
        self._assessments: dict[str, ConfidenceAssessment] = {}

    def calculate_confidence(
        self,
        evaluation_id: str,
        samples: Sequence[float],
        confidence_level: float = 0.95,
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ConfidenceAssessment:
        """Calculate deterministic confidence interval and margin of error for sample data."""
        if not samples:
            raise ValueError("Confidence assessment requires non-empty sample sequence.")
        if confidence_level not in self.Z_CRITICAL_MAP and not (0.5 <= confidence_level <= 0.9999):
            raise ValueError(f"Confidence level '{confidence_level}' must be between 0.5 and 0.9999.")

        n = len(samples)
        mean_val = sum(samples) / float(n)

        variance = sum((x - mean_val) ** 2 for x in samples) / (float(n - 1) if n > 1 else 1.0)
        std_dev = math.sqrt(variance)

        z_crit = self.Z_CRITICAL_MAP.get(confidence_level, 1.960)
        std_error = std_dev / math.sqrt(n) if n > 0 else 0.0
        margin_of_error = z_crit * std_error

        lower_bound = mean_val - margin_of_error
        upper_bound = mean_val + margin_of_error

        rating = self.classify_confidence(sample_size=n, margin_of_error=margin_of_error, std_dev=std_dev)
        now_str = timestamp or datetime.now(timezone.utc).isoformat()

        con_id, canonical_hash = compute_confidence_id(
            evaluation_id=evaluation_id,
            confidence_level=confidence_level,
            margin_of_error=margin_of_error,
        )

        assessment = ConfidenceAssessment(
            confidence_id=con_id,
            evaluation_id=evaluation_id.strip(),
            confidence_level=confidence_level,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            margin_of_error=margin_of_error,
            sample_size=n,
            confidence_rating=rating,
            timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._assessments[con_id] = assessment
        return assessment

    def classify_confidence(self, sample_size: int, margin_of_error: float, std_dev: float) -> EvaluationConfidence:
        """Classify confidence into qualitative levels based on sample size and error relative to std dev."""
        if sample_size < 30:
            return EvaluationConfidence.VERY_LOW
        elif sample_size < 100:
            return EvaluationConfidence.LOW
        elif sample_size < 500:
            return EvaluationConfidence.MODERATE
        elif sample_size < 2000:
            return EvaluationConfidence.HIGH
        else:
            return EvaluationConfidence.VERY_HIGH

    def get_assessment(self, confidence_id: str) -> ConfidenceAssessment | None:
        """Retrieve assessment by ID."""
        return self._assessments.get(confidence_id)

    def list_all(self) -> list[ConfidenceAssessment]:
        """List all assessments sorted by timestamp."""
        return sorted(self._assessments.values(), key=lambda c: c.timestamp)
