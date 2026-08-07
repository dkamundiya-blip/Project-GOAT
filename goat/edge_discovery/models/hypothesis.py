"""
Project GOAT Phase 6 — Research Hypothesis Domain Models

Defines immutable Pydantic models for quantitative hypotheses and deterministic ID computation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class HypothesisOperator(str, Enum):
    """Logical operators for feature condition evaluations."""
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    EQ = "=="
    NEQ = "!="
    BETWEEN = "BETWEEN"


class HypothesisStatus(str, Enum):
    """Lifecycle status of a research hypothesis."""
    DRAFT = "DRAFT"
    EVALUATING = "EVALUATING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    RETIRED = "RETIRED"


class HypothesisCondition(BaseModel):
    """Condition specifying a threshold on an engineered feature."""
    feature_name: str = Field(..., description="Target engineered feature key (e.g. trend_strength)")
    operator: HypothesisOperator = Field(..., description="Comparison operator")
    threshold_value: float = Field(..., description="Primary threshold float value")
    secondary_value: float | None = Field(default=None, description="Optional upper bound value for BETWEEN operator")

    def evaluate(self, feature_val: float) -> bool:
        """Evaluate condition against a numerical feature value."""
        if self.operator == HypothesisOperator.GT:
            return feature_val > self.threshold_value
        elif self.operator == HypothesisOperator.GTE:
            return feature_val >= self.threshold_value
        elif self.operator == HypothesisOperator.LT:
            return feature_val < self.threshold_value
        elif self.operator == HypothesisOperator.LTE:
            return feature_val <= self.threshold_value
        elif self.operator == HypothesisOperator.EQ:
            return abs(feature_val - self.threshold_value) < 1e-6
        elif self.operator == HypothesisOperator.NEQ:
            return abs(feature_val - self.threshold_value) >= 1e-6
        elif self.operator == HypothesisOperator.BETWEEN and self.secondary_value is not None:
            return self.threshold_value <= feature_val <= self.secondary_value
        return False

    class Config:
        frozen = True


class HypothesisPrediction(BaseModel):
    """Target prediction specification for a hypothesis."""
    target_feature: str = Field(default="future_return", description="Target feature or price return metric")
    horizon_bars: int = Field(default=5, description="Look-forward horizon in bars")
    min_return: float = Field(default=0.001, description="Minimum expected directional return threshold")
    direction: float = Field(default=1.0, description="Predicted direction: 1.0 for bullish, -1.0 for bearish")

    class Config:
        frozen = True


class ResearchHypothesis(BaseModel):
    """Immutable domain model representing a quantitative research hypothesis."""

    hypothesis_id: str = Field(
        ...,
        description="Unique hypothesis ID formatted as HYP_<HEX16>",
        pattern=r"^HYP_[A-Fa-f0-9]{16}$",
    )
    version: str = Field(default="6.0.0", description="Hypothesis model specification version")
    description: str = Field(..., description="Human-readable hypothesis description")
    conditions: list[HypothesisCondition] = Field(..., description="List of feature condition rules")
    prediction: HypothesisPrediction = Field(..., description="Target outcome prediction specification")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    author: str = Field(default="GOAT_QUANT_ENGINE", description="Creator or search strategy identifier")
    status: HypothesisStatus = Field(default=HypothesisStatus.DRAFT, description="Current lifecycle status")
    checksum: str = Field(..., description="SHA-256 canonical payload checksum")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible research metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_hypothesis_id(
    conditions: list[HypothesisCondition],
    prediction: HypothesisPrediction,
    version: str = "6.0.0",
) -> tuple[str, str]:
    """Compute deterministic (hypothesis_id, canonical_hash) for ResearchHypothesis.

    Returns:
        Tuple of (HYP_<HEX16>, SHA256_HEX64).
    """
    sorted_conditions = [
        {
            "feature_name": c.feature_name.strip(),
            "operator": c.operator.value,
            "threshold_value": round(c.threshold_value, 6),
            "secondary_value": round(c.secondary_value, 6) if c.secondary_value is not None else None,
        }
        for c in sorted(conditions, key=lambda x: (x.feature_name, x.operator.value, x.threshold_value))
    ]
    payload = {
        "conditions": sorted_conditions,
        "prediction": {
            "direction": round(prediction.direction, 4),
            "horizon_bars": prediction.horizon_bars,
            "min_return": round(prediction.min_return, 6),
            "target_feature": prediction.target_feature.strip(),
        },
        "version": version.strip(),
    }
    digest = compute_canonical_sha256(payload)
    hyp_id = f"HYP_{digest[:16].upper()}"
    return hyp_id, digest.upper()
