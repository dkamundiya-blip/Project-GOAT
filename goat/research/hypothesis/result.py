"""
Project GOAT v0.4 — Hypothesis Result Schema

Structured result model representing the quantitative evaluation outcome of a hypothesis.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class HypothesisResult(BaseModel):
    """Structured evaluation output for a single hypothesis against a dataset partition."""

    hypothesis_id: str
    version: str
    dataset_fingerprint: str
    partition: str  # "train", "validation", "holdout"
    symbol: str
    timeframe: str
    conditional_sample_count: int
    baseline_sample_count: int
    conditional_stats: dict[str, float] = Field(default_factory=dict)
    baseline_stats: dict[str, float] = Field(default_factory=dict)
    effect_size_type: str = "cohens_d"
    effect_size: float = 0.0
    statistical_test_type: str = "welch_ttest"
    statistic_value: float = 0.0
    raw_p_value: float = 1.0
    adjusted_q_value: float | None = None
    confidence_interval: list[float] | None = None
    dependence_overlap_risk: bool = False
    sufficiency_status: str = "SUFFICIENT"  # "SUFFICIENT" or "INSUFFICIENT_DATA"
    validation_status: str = "UNTESTED"     # "PASSED", "FAILED", "UNTESTED"
    stability_status: str = "STABLE"        # "STABLE", "WEAKENING", "STRENGTHENING", "UNSTABLE", "STATISTICALLY_SUPPORTED_BUT_PRACTICALLY_WEAK"
    edge_score: dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)
