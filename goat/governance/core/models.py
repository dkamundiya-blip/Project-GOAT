"""
Project GOAT v0.9 — Core Immutable Domain Models for Edge Promotion & Retirement Governance Subsystem
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.governance.core.enums import (
    EdgeStatus,
    GovernanceDecisionOutcome,
    GovernanceReason,
)


class EdgeCandidate(BaseModel):
    """Immutable domain model representing a candidate trading edge submitted to governance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    edge_id: str = Field(
        ...,
        description="Unique edge ID formatted as EDG_<HEX16>",
        pattern=r"^EDG_[A-Fa-f0-9]{16,64}$",
    )
    title: str = Field(..., min_length=3, description="Descriptive edge title")
    hypothesis_id: str = Field(
        ...,
        description="Parent ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    evaluation_id: str = Field(
        ...,
        description="Passed StatisticalEvaluation ID (STE_<HEX16>)",
        pattern=r"^STE_[A-Fa-f0-9]{16,64}$",
    )
    experiment_id: str = Field(
        ...,
        description="Target ScientificExperiment ID (EXP_<HEX16>)",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    validation_session_id: str = Field(
        ...,
        description="Passed ValidationSession ID (VSN_<HEX16>)",
        pattern=r"^VSN_[A-Fa-f0-9]{16,64}$",
    )
    evidence_ids: list[str] = Field(default_factory=list, description="Associated Evidence IDs (EVR_<HEX16>)")
    status: EdgeStatus = Field(default=EdgeStatus.CANDIDATE, description="Current edge lifecycle status")
    created_timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class PromotionAssessment(BaseModel):
    """Immutable domain model storing the evaluation of an edge against promotion criteria."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    assessment_id: str = Field(
        ...,
        description="Unique promotion assessment ID formatted as PRA_<HEX16>",
        pattern=r"^PRA_[A-Fa-f0-9]{16,64}$",
    )
    edge_id: str = Field(
        ...,
        description="Target Edge ID (EDG_<HEX16>)",
        pattern=r"^EDG_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target Hypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    is_hypothesis_passed: bool = Field(..., description="Flag indicating hypothesis verification")
    is_evidence_complete: bool = Field(..., description="Flag indicating evidence chain integrity")
    is_experiment_complete: bool = Field(..., description="Flag indicating experiment completion")
    is_statistics_complete: bool = Field(..., description="Flag indicating statistical evaluation supported")
    is_live_validation_complete: bool = Field(..., description="Flag indicating live validation passed")
    is_constitution_satisfied: bool = Field(..., description="Flag indicating Constitutional compliance")
    is_research_protocol_satisfied: bool = Field(..., description="Flag indicating PRSP v1.0 compliance")
    is_promotable: bool = Field(..., description="Overall promotion readiness recommendation")
    assessment_notes: str = Field(..., description="Detailed promotion evaluation notes")
    timestamp: str = Field(..., description="ISO 8601 assessment timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class RetirementAssessment(BaseModel):
    """Immutable domain model storing the evaluation of an edge against retirement and degradation criteria."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    assessment_id: str = Field(
        ...,
        description="Unique retirement assessment ID formatted as RTA_<HEX16>",
        pattern=r"^RTA_[A-Fa-f0-9]{16,64}$",
    )
    edge_id: str = Field(
        ...,
        description="Target Edge ID (EDG_<HEX16>)",
        pattern=r"^EDG_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target Hypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    expectancy_degradation: float = Field(default=0.0, description="Calculated expectancy degradation ratio")
    confidence_decline: float = Field(default=0.0, description="Calculated statistical confidence decline")
    structural_shift_detected: bool = Field(default=False, description="Flag indicating market regime shift")
    amendment_001_violation: bool = Field(default=False, description="Flag indicating Minimum Executable Risk violation")
    is_retirement_recommended: bool = Field(..., description="Overall retirement recommendation")
    assessment_notes: str = Field(..., description="Detailed retirement evaluation notes")
    timestamp: str = Field(..., description="ISO 8601 assessment timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class GovernanceDecision(BaseModel):
    """Immutable domain model representing the binding constitutional governance decision."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(
        ...,
        description="Unique decision ID formatted as GOV_<HEX16>",
        pattern=r"^GOV_[A-Fa-f0-9]{16,64}$",
    )
    edge_id: str = Field(
        ...,
        description="Target Edge ID (EDG_<HEX16>)",
        pattern=r"^EDG_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target Hypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    decision: GovernanceDecisionOutcome = Field(..., description="Binding constitutional decision")
    reason: GovernanceReason = Field(..., description="Governance decision rationale category")
    rationale: str = Field(..., min_length=10, description="Detailed scientific and constitutional justification")
    authorizer: str = Field(default="GOVERNANCE_BOARD", description="Authorizing board identifier")
    timestamp: str = Field(..., description="ISO 8601 decision timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class GovernanceAudit(BaseModel):
    """Immutable domain model storing the audit trail linking a decision back to the complete research chain."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    audit_id: str = Field(
        ...,
        description="Unique audit ID formatted as AUD_<HEX16>",
        pattern=r"^AUD_[A-Fa-f0-9]{16,64}$",
    )
    decision_id: str = Field(
        ...,
        description="Target GovernanceDecision ID (GOV_<HEX16>)",
        pattern=r"^GOV_[A-Fa-f0-9]{16,64}$",
    )
    edge_id: str = Field(
        ...,
        description="Target Edge ID (EDG_<HEX16>)",
        pattern=r"^EDG_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(..., description="Linked Hypothesis ID (HYP_<HEX16>)")
    evidence_ids: list[str] = Field(default_factory=list, description="Linked Evidence IDs (EVR_<HEX16>)")
    experiment_id: str = Field(..., description="Linked Experiment ID (EXP_<HEX16>)")
    evaluation_id: str = Field(..., description="Linked Evaluation ID (STE_<HEX16>)")
    validation_session_id: str = Field(..., description="Linked Live Validation Session ID (VSN_<HEX16>)")
    is_explainable: bool = Field(default=True, description="Traceability verification flag")
    is_replayable: bool = Field(default=True, description="Replayability verification flag")
    operator: str = Field(default="AUDIT_ENGINE", description="Audit operator identifier")
    timestamp: str = Field(..., description="ISO 8601 audit timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class GovernanceSummary(BaseModel):
    """Immutable domain model summarizing aggregate metrics across the governance subsystem."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(
        ...,
        description="Unique summary ID formatted as GSM_<HEX16>",
        pattern=r"^GSM_[A-Fa-f0-9]{16,64}$",
    )
    total_edges: int = Field(..., ge=0, description="Total edges registered")
    total_decisions: int = Field(..., ge=0, description="Total governance decisions issued")
    status_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by EdgeStatus")
    decision_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by GovernanceDecisionOutcome")
    reason_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by GovernanceReason")
    timestamp: str = Field(..., description="ISO 8601 summary snapshot timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
