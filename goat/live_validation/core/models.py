"""
Project GOAT v0.9 — Core Immutable Domain Models for Controlled Live Scientific Validation Subsystem
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
    ValidationStatus,
)


class LiveValidationCandidate(BaseModel):
    """Immutable domain model representing a candidate hypothesis eligible for live scientific validation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate_id: str = Field(
        ...,
        description="Unique candidate ID formatted as LVC_<HEX16>",
        pattern=r"^LVC_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
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
    evidence_ids: list[str] = Field(default_factory=list, description="Associated Evidence IDs (EVR_<HEX16>)")
    replay_id: str = Field(default="", description="Associated Replay ID (RPL_<HEX16>)")
    status: ValidationStatus = Field(default=ValidationStatus.ELIGIBLE, description="Candidate eligibility status")
    eligibility_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Qualification eligibility score")
    created_timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ValidationSession(BaseModel):
    """Immutable domain model representing an active controlled live scientific validation session."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str = Field(
        ...,
        description="Unique session ID formatted as VSN_<HEX16>",
        pattern=r"^VSN_[A-Fa-f0-9]{16,64}$",
    )
    candidate_id: str = Field(
        ...,
        description="Target Candidate ID (LVC_<HEX16>)",
        pattern=r"^LVC_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target Hypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    status: ValidationStatus = Field(default=ValidationStatus.RUNNING, description="Session lifecycle status")
    monitoring_status: MonitoringStatus = Field(default=MonitoringStatus.NORMAL, description="Health monitoring status")
    start_timestamp: str = Field(..., description="ISO 8601 session start timestamp")
    end_timestamp: str | None = Field(default=None, description="ISO 8601 session end timestamp if completed")
    total_observations: int = Field(default=0, ge=0, description="Count of live observations recorded")
    operator: str = Field(default="LIVE_VALIDATION_ENGINE", description="Operator identifier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ValidationObservation(BaseModel):
    """Immutable domain model storing an individual empirical live validation observation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    observation_id: str = Field(
        ...,
        description="Unique observation ID formatted as VOB_<HEX16>",
        pattern=r"^VOB_[A-Fa-f0-9]{16,64}$",
    )
    session_id: str = Field(
        ...,
        description="Target Session ID (VSN_<HEX16>)",
        pattern=r"^VSN_[A-Fa-f0-9]{16,64}$",
    )
    timestamp: str = Field(..., description="ISO 8601 observation timestamp")
    live_outcome: float = Field(..., description="Empirical live outcome metric observed")
    expected_outcome: float = Field(..., description="Statistical expectation benchmark")
    slippage: float = Field(default=0.0, description="Observed execution slippage")
    spread: float = Field(default=0.0, ge=0.0, description="Observed market spread")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Observed latency in milliseconds")
    fill_ratio: float = Field(default=1.0, ge=0.0, le=1.0, description="Observed fill consistency ratio")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ValidationDecision(BaseModel):
    """Immutable domain model storing the formal scientific conclusion derived for a live validation session."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(
        ...,
        description="Unique decision ID formatted as VDC_<HEX16>",
        pattern=r"^VDC_[A-Fa-f0-9]{16,64}$",
    )
    session_id: str = Field(
        ...,
        description="Target Session ID (VSN_<HEX16>)",
        pattern=r"^VSN_[A-Fa-f0-9]{16,64}$",
    )
    candidate_id: str = Field(
        ...,
        description="Target Candidate ID (LVC_<HEX16>)",
        pattern=r"^LVC_[A-Fa-f0-9]{16,64}$",
    )
    decision: ValidationDecisionOutcome = Field(..., description="Scientific validation decision outcome")
    rationale: str = Field(..., min_length=5, description="Detailed scientific justification for decision")
    timestamp: str = Field(..., description="ISO 8601 decision timestamp")
    authorizer: str = Field(default="RETIREMENT_ENGINE", description="Authorizer component identifier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ValidationSummary(BaseModel):
    """Immutable domain model summarizing aggregate metrics across the live validation subsystem."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(
        ...,
        description="Unique summary ID formatted as VSM_<HEX16>",
        pattern=r"^VSM_[A-Fa-f0-9]{16,64}$",
    )
    total_candidates: int = Field(..., ge=0, description="Total candidates registered")
    total_sessions: int = Field(..., ge=0, description="Total sessions initiated")
    total_observations: int = Field(..., ge=0, description="Total observations recorded")
    status_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by ValidationStatus")
    decision_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by ValidationDecisionOutcome")
    timestamp: str = Field(..., description="ISO 8601 summary snapshot timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ValidationAudit(BaseModel):
    """Immutable domain model logging append-only audit events for live validation sessions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    audit_id: str = Field(
        ...,
        description="Unique audit ID formatted as VAU_<HEX16>",
        pattern=r"^VAU_[A-Fa-f0-9]{16,64}$",
    )
    session_id: str = Field(
        ...,
        description="Target Session ID (VSN_<HEX16>)",
        pattern=r"^VSN_[A-Fa-f0-9]{16,64}$",
    )
    action: str = Field(..., description="Audit action ('CREATE', 'PAUSE', 'RESUME', 'COMPLETE', 'TERMINATE')")
    previous_status: ValidationStatus = Field(..., description="Previous ValidationStatus")
    new_status: ValidationStatus = Field(..., description="New ValidationStatus")
    operator: str = Field(default="SYSTEM", description="Operator attribution")
    timestamp: str = Field(..., description="ISO 8601 audit timestamp")
    notes: str = Field(default="", description="Audit commentary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
