"""
Project GOAT v0.9 — Core Immutable Domain Models for Statistical Evaluation Subsystem
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.statistics.core.enums import (
    EvaluationConfidence,
    EvaluationStatus,
    ScientificDecision,
)


class StatisticalEvaluation(BaseModel):
    """Immutable domain model representing a formal statistical evaluation of an experiment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evaluation_id: str = Field(
        ...,
        description="Unique deterministic evaluation ID formatted as STE_<HEX16>",
        pattern=r"^STE_[A-Fa-f0-9]{16,64}$",
    )
    experiment_id: str = Field(
        ...,
        description="Target ScientificExperiment ID (EXP_<HEX16>)",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    status: EvaluationStatus = Field(default=EvaluationStatus.PENDING, description="Lifecycle evaluation status")
    decision: ScientificDecision = Field(default=ScientificDecision.INCONCLUSIVE, description="Final scientific decision outcome")
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.9999, description="Statistical confidence level threshold (e.g. 0.95)")
    confidence_rating: EvaluationConfidence = Field(default=EvaluationConfidence.MODERATE, description="Qualitative confidence rating")
    p_value: float = Field(default=1.0, ge=0.0, le=1.0, description="Computed p-value statistic")
    effect_size: float = Field(default=0.0, description="Computed effect size metric (e.g. Cohen's d)")
    expected_value: float = Field(default=0.0, description="Computed mathematical expectancy per sample")
    sample_size: int = Field(default=0, ge=0, description="Total sample size evaluated")
    evaluator: str = Field(default="STATISTICAL_ENGINE", description="Evaluator module or agent identifier")
    timestamp: str = Field(..., description="ISO 8601 evaluation completion timestamp")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ConfidenceAssessment(BaseModel):
    """Immutable domain model storing confidence interval calculations and classification details."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    confidence_id: str = Field(
        ...,
        description="Unique deterministic confidence ID formatted as CON_<HEX16>",
        pattern=r"^CON_[A-Fa-f0-9]{16,64}$",
    )
    evaluation_id: str = Field(
        ...,
        description="Target StatisticalEvaluation ID (STE_<HEX16>)",
        pattern=r"^STE_[A-Fa-f0-9]{16,64}$",
    )
    confidence_level: float = Field(..., ge=0.5, le=0.9999, description="Target confidence interval level (e.g. 0.95)")
    lower_bound: float = Field(..., description="Lower bound of calculated confidence interval")
    upper_bound: float = Field(..., description="Upper bound of calculated confidence interval")
    margin_of_error: float = Field(..., ge=0.0, description="Calculated margin of error")
    sample_size: int = Field(..., ge=1, description="Sample size used for interval estimation")
    confidence_rating: EvaluationConfidence = Field(default=EvaluationConfidence.MODERATE, description="Qualitative rating")
    timestamp: str = Field(..., description="ISO 8601 assessment timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class SignificanceAssessment(BaseModel):
    """Immutable domain model storing null hypothesis testing and p-value significance evaluation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    significance_id: str = Field(
        ...,
        description="Unique deterministic significance ID formatted as SIG_<HEX16>",
        pattern=r"^SIG_[A-Fa-f0-9]{16,64}$",
    )
    evaluation_id: str = Field(
        ...,
        description="Target StatisticalEvaluation ID (STE_<HEX16>)",
        pattern=r"^STE_[A-Fa-f0-9]{16,64}$",
    )
    p_value: float = Field(..., ge=0.0, le=1.0, description="Computed empirical p-value")
    test_statistic: float = Field(..., description="Computed test statistic value (z-score / t-stat)")
    alpha_threshold: float = Field(default=0.01, ge=0.0001, le=0.1, description="Significance alpha threshold (default 0.01)")
    is_significant: bool = Field(..., description="Flag indicating p_value < alpha_threshold")
    multiple_comparison_correction: str = Field(default="NONE", description="Correction applied (NONE / BONFERRONI / BENJAMINI_HOCHBERG)")
    adjusted_p_value: float = Field(default=1.0, ge=0.0, le=1.0, description="Multiple-comparison adjusted p-value")
    timestamp: str = Field(..., description="ISO 8601 assessment timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ExpectancyAssessment(BaseModel):
    """Immutable domain model storing expected value and distribution expectancy metrics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    expectancy_id: str = Field(
        ...,
        description="Unique deterministic expectancy ID formatted as EXP_<HEX16>",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    evaluation_id: str = Field(
        ...,
        description="Target StatisticalEvaluation ID (STE_<HEX16>)",
        pattern=r"^STE_[A-Fa-f0-9]{16,64}$",
    )
    expected_value: float = Field(..., description="Calculated expected value metric per observation")
    win_rate: float = Field(..., ge=0.0, le=1.0, description="Empirical win rate ratio (0.0 to 1.0)")
    loss_rate: float = Field(..., ge=0.0, le=1.0, description="Empirical loss rate ratio (0.0 to 1.0)")
    average_gain: float = Field(default=0.0, ge=0.0, description="Average positive gain per winning observation")
    average_loss: float = Field(default=0.0, ge=0.0, description="Average negative magnitude per losing observation")
    profit_factor: float = Field(default=0.0, ge=0.0, description="Ratio of gross gains to gross losses")
    sample_size: int = Field(..., ge=0, description="Sample size analyzed")
    timestamp: str = Field(..., description="ISO 8601 assessment timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class EvaluationDecision(BaseModel):
    """Immutable domain model representing the final scientific decision outcome appended to an experiment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(
        ...,
        description="Unique deterministic decision ID formatted as EVD_<HEX16>",
        pattern=r"^EVD_[A-Fa-f0-9]{16,64}$",
    )
    evaluation_id: str = Field(
        ...,
        description="Target StatisticalEvaluation ID (STE_<HEX16>)",
        pattern=r"^STE_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    decision: ScientificDecision = Field(..., description="Scientific decision outcome")
    confidence_rating: EvaluationConfidence = Field(default=EvaluationConfidence.MODERATE, description="Confidence rating")
    decision_rationale: str = Field(..., min_length=5, description="Detailed scientific rationale for decision")
    authorizer: str = Field(default="STATISTICAL_BOARD", description="Authorizer agent or board identifier")
    timestamp: str = Field(..., description="ISO 8601 decision timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class EvaluationSummary(BaseModel):
    """Immutable domain model summarizing aggregate statistical evaluation metrics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(
        ...,
        description="Unique deterministic summary ID formatted as SUM_<HEX16>",
        pattern=r"^SUM_[A-Fa-f0-9]{16,64}$",
    )
    total_evaluations: int = Field(..., ge=0, description="Total count of statistical evaluations")
    total_decisions: int = Field(..., ge=0, description="Total count of formalized decisions")
    decision_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by ScientificDecision")
    confidence_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by EvaluationConfidence")
    status_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by EvaluationStatus")
    timestamp: str = Field(..., description="ISO 8601 summary snapshot timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
