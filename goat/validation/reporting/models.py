"""
Project GOAT v0.7 — Validation Report Models

Defines immutable report models for scientific hypothesis validation:
ValidationReport, ValidationSummary, ValidationAuditReport,
ValidationEvidenceReport, ValidationStatisticsReport.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ValidationReport(BaseModel):
    """Immutable summary report for a scientific hypothesis validation run."""

    report_id: str = Field(
        ...,
        description="Unique Report ID formatted as VRPT_<HEX16>",
        pattern=r"^VRPT_[A-Fa-f0-9]{16}$",
    )
    validation_run_id: str = Field(..., description="Parent Validation Run ID (VRN_<HEX16>)")
    hypothesis_id: str = Field(..., description="Target Hypothesis ID (HYP_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC report timestamp")
    decision_summary: str = Field(default="", description="Decision type summary")
    overall_confidence: float = Field(default=0.0, description="Overall scientific confidence")
    evidence_count: int = Field(default=0, description="Total evidence count")
    scores: dict[str, float] = Field(default_factory=dict, description="Validation score summary")
    threshold_results: dict[str, Any] = Field(default_factory=dict, description="Threshold evaluation results")
    reasoning: str = Field(default="", description="Decision reasoning")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Report metadata")

    class Config:
        frozen = True
        extra = "forbid"


class ValidationSummary(BaseModel):
    """Compact immutable summary for a validation outcome."""

    hypothesis_id: str = Field(..., description="Target Hypothesis ID")
    decision_type: str = Field(..., description="Decision type")
    overall_confidence: float = Field(default=0.0, description="Overall confidence")
    evidence_count: int = Field(default=0, description="Evidence count")
    thresholds_passed: int = Field(default=0, description="Thresholds passed")
    total_thresholds: int = Field(default=0, description="Total thresholds")

    class Config:
        frozen = True
        extra = "forbid"


class ValidationAuditReport(BaseModel):
    """Immutable audit trail report for a validation run."""

    report_id: str = Field(
        ...,
        description="Unique Audit Report ID formatted as VAUD_<HEX16>",
        pattern=r"^VAUD_[A-Fa-f0-9]{16}$",
    )
    validation_run_id: str = Field(..., description="Parent Validation Run ID")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    audit_events: list[dict[str, Any]] = Field(default_factory=list, description="Audit event records")
    integrity_status: str = Field(default="clean", description="Integrity verification status")

    class Config:
        frozen = True
        extra = "forbid"


class ValidationEvidenceReport(BaseModel):
    """Immutable evidence breakdown report for a validation run."""

    report_id: str = Field(
        ...,
        description="Unique Evidence Report ID formatted as VEVR_<HEX16>",
        pattern=r"^VEVR_[A-Fa-f0-9]{16}$",
    )
    validation_run_id: str = Field(..., description="Parent Validation Run ID")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    evidence_summary: dict[str, Any] = Field(default_factory=dict, description="Aggregated evidence summary")
    evidence_breakdown: list[dict[str, Any]] = Field(default_factory=list, description="Per-evidence detail")
    total_evidence: int = Field(default=0, description="Total evidence count")
    supporting_evidence: int = Field(default=0, description="Supporting evidence count")
    contradicting_evidence: int = Field(default=0, description="Contradicting evidence count")

    class Config:
        frozen = True
        extra = "forbid"


class ValidationStatisticsReport(BaseModel):
    """Immutable statistics report for a validation run."""

    report_id: str = Field(
        ...,
        description="Unique Statistics Report ID formatted as VSTR_<HEX16>",
        pattern=r"^VSTR_[A-Fa-f0-9]{16}$",
    )
    validation_run_id: str = Field(..., description="Parent Validation Run ID")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    scores: dict[str, float] = Field(default_factory=dict, description="All computed scores")
    score_weights: dict[str, float] = Field(default_factory=dict, description="Score weights used")
    computation_method: str = Field(default="deterministic_weighted_sum", description="Computation method")

    class Config:
        frozen = True
        extra = "forbid"
