"""
Project GOAT v0.7 — Validation Statistical Scores

Defines deterministic statistical scoring models for hypothesis validation.
All computations are pure deterministic — no random sampling, no probabilistic simulation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ValidationScores(BaseModel):
    """Immutable container for all computed validation statistical scores."""

    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score [0.0, 1.0]")
    evidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence strength score [0.0, 1.0]")
    agreement_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence agreement score [0.0, 1.0]")
    reproducibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Reproducibility score [0.0, 1.0]")
    robustness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Cross-context robustness score [0.0, 1.0]")
    stability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Temporal stability score [0.0, 1.0]")
    validation_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Threshold pass rate score [0.0, 1.0]")
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall scientific confidence [0.0, 1.0]")

    class Config:
        frozen = True
        extra = "forbid"


def compute_confidence_score(
    total_evidence: int,
    validated_count: int,
    max_evidence: int = 20,
) -> float:
    """Compute deterministic confidence score from evidence counts.

    Confidence = validated_count / max(total_evidence, 1), capped by evidence saturation.

    Args:
        total_evidence: Total evidence count.
        validated_count: Number of validated evidence records.
        max_evidence: Evidence count for full saturation.

    Returns:
        Score in [0.0, 1.0].
    """
    if total_evidence <= 0:
        return 0.0
    base = validated_count / max(total_evidence, 1)
    saturation = min(total_evidence / max(max_evidence, 1), 1.0)
    return round(min(base * saturation, 1.0), 6)


def compute_evidence_score(
    total_weight: float,
    max_weight: float = 20.0,
) -> float:
    """Compute deterministic evidence strength score from total weight.

    Args:
        total_weight: Sum of evidence weights.
        max_weight: Weight for full saturation.

    Returns:
        Score in [0.0, 1.0].
    """
    if total_weight <= 0:
        return 0.0
    return round(min(total_weight / max(max_weight, 0.001), 1.0), 6)


def compute_agreement_score(
    supporting_count: int,
    contradicting_count: int,
) -> float:
    """Compute deterministic agreement score.

    Agreement = supporting / (supporting + contradicting).

    Args:
        supporting_count: Number of supporting evidence.
        contradicting_count: Number of contradicting evidence.

    Returns:
        Score in [0.0, 1.0].
    """
    total = supporting_count + contradicting_count
    if total <= 0:
        return 0.0
    return round(supporting_count / total, 6)


def compute_reproducibility_score(
    replication_count: int,
    min_replications: int = 3,
) -> float:
    """Compute deterministic reproducibility score from replication count.

    Args:
        replication_count: Number of independent replications.
        min_replications: Replications required for full score.

    Returns:
        Score in [0.0, 1.0].
    """
    if replication_count <= 0:
        return 0.0
    return round(min(replication_count / max(min_replications, 1), 1.0), 6)


def compute_robustness_score(
    cross_context_count: int,
    min_contexts: int = 3,
) -> float:
    """Compute deterministic robustness score from cross-context replication.

    Args:
        cross_context_count: Number of independent contexts confirming.
        min_contexts: Contexts required for full score.

    Returns:
        Score in [0.0, 1.0].
    """
    if cross_context_count <= 0:
        return 0.0
    return round(min(cross_context_count / max(min_contexts, 1), 1.0), 6)


def compute_stability_score(
    consistent_periods: int,
    total_periods: int,
) -> float:
    """Compute deterministic temporal stability score.

    Stability = consistent_periods / total_periods.

    Args:
        consistent_periods: Number of consistent temporal periods.
        total_periods: Total temporal periods evaluated.

    Returns:
        Score in [0.0, 1.0].
    """
    if total_periods <= 0:
        return 0.0
    return round(min(consistent_periods / total_periods, 1.0), 6)


def compute_validation_score(
    thresholds_passed: int,
    total_thresholds: int,
) -> float:
    """Compute deterministic validation threshold pass rate score.

    Args:
        thresholds_passed: Number of thresholds met.
        total_thresholds: Total number of thresholds evaluated.

    Returns:
        Score in [0.0, 1.0].
    """
    if total_thresholds <= 0:
        return 0.0
    return round(min(thresholds_passed / total_thresholds, 1.0), 6)


def compute_overall_confidence(
    confidence: float,
    evidence: float,
    agreement: float,
    reproducibility: float,
    robustness: float,
    stability: float,
    validation: float,
    weights: dict[str, float] | None = None,
) -> float:
    """Compute deterministic overall scientific confidence as a weighted sum.

    Default weights: confidence=0.20, evidence=0.15, agreement=0.20,
    reproducibility=0.15, robustness=0.10, stability=0.10, validation=0.10

    Args:
        confidence: Confidence score.
        evidence: Evidence score.
        agreement: Agreement score.
        reproducibility: Reproducibility score.
        robustness: Robustness score.
        stability: Stability score.
        validation: Validation score.
        weights: Optional custom weight dictionary.

    Returns:
        Score in [0.0, 1.0].
    """
    w = weights or {
        "confidence": 0.20,
        "evidence": 0.15,
        "agreement": 0.20,
        "reproducibility": 0.15,
        "robustness": 0.10,
        "stability": 0.10,
        "validation": 0.10,
    }

    result = (
        confidence * w.get("confidence", 0.20)
        + evidence * w.get("evidence", 0.15)
        + agreement * w.get("agreement", 0.20)
        + reproducibility * w.get("reproducibility", 0.15)
        + robustness * w.get("robustness", 0.10)
        + stability * w.get("stability", 0.10)
        + validation * w.get("validation", 0.10)
    )
    return round(min(max(result, 0.0), 1.0), 6)
