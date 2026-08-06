"""
Project GOAT v0.9 — Core Immutable Domain Models for Hypothesis Subsystem
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.research.core.enums import (
    EvidenceLevel,
    HypothesisPriority,
    HypothesisStatus,
)


class ScientificHypothesis(BaseModel):
    """Immutable domain model representing a scientific research hypothesis in Project GOAT."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    hypothesis_id: str = Field(
        ...,
        description="Unique deterministic hypothesis ID formatted as HYP_<HEX16>",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    title: str = Field(..., min_length=3, description="Descriptive hypothesis title")
    research_question: str = Field(..., min_length=5, description="Core scientific question being investigated")
    null_hypothesis: str = Field(..., min_length=5, description="Null hypothesis statement (H0)")
    alternative_hypothesis: str = Field(..., min_length=5, description="Alternative hypothesis statement (H1)")
    expected_behaviour: str = Field(..., min_length=5, description="Expected structural market mechanism")
    independent_variables: list[str] = Field(default_factory=list, description="List of independent variables")
    dependent_variables: list[str] = Field(default_factory=list, description="List of dependent variables")
    assumptions: list[str] = Field(default_factory=list, description="List of required underlying assumptions")
    risk_statement: str = Field(default="Unspecified risk statement.", description="Tail risk analysis statement")
    success_criteria: list[str] = Field(default_factory=list, description="Quantitative success criteria bounds")
    failure_criteria: list[str] = Field(default_factory=list, description="Explicit failure criteria bounds")
    author: str = Field(default="QUANT_RESEARCHER", description="Author or registration agent")
    created_timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    updated_timestamp: str = Field(..., description="ISO 8601 last updated timestamp")
    status: HypothesisStatus = Field(default=HypothesisStatus.DRAFT, description="Current lifecycle status")
    priority: HypothesisPriority = Field(default=HypothesisPriority.NORMAL, description="Evaluation priority rating")
    evidence_level: EvidenceLevel = Field(default=EvidenceLevel.L0, description="Evidence hierarchy level")
    revision_number: int = Field(default=1, ge=1, description="Monotonically increasing revision number")
    tags: list[str] = Field(default_factory=list, description="Indexing and classification tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class HypothesisRevision(BaseModel):
    """Immutable domain model representing a revision event for a ScientificHypothesis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    revision_id: str = Field(
        ...,
        description="Unique deterministic revision ID formatted as REV_<HEX16>",
        pattern=r"^REV_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    revision_number: int = Field(..., ge=1, description="Revision sequence index")
    previous_hash: str = Field(default="", description="Canonical SHA-256 hash of the preceding revision state")
    change_summary: str = Field(..., min_length=3, description="Summary description of changes made")
    author: str = Field(..., description="Author or editor of the revision")
    timestamp: str = Field(..., description="ISO 8601 revision timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class HypothesisValidation(BaseModel):
    """Immutable domain model representing a scientific validation evaluation for a ScientificHypothesis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    validation_id: str = Field(
        ...,
        description="Unique deterministic validation ID formatted as HVL_<HEX16>",
        pattern=r"^HVL_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    is_valid: bool = Field(..., description="Boolean flag indicating overall validation outcome")
    validation_rule_results: list[dict[str, Any]] = Field(
        default_factory=list, description="Detailed rule validation evaluation records"
    )
    validation_errors: list[str] = Field(default_factory=list, description="List of blocking validation error messages")
    validation_warnings: list[str] = Field(default_factory=list, description="List of non-blocking warning messages")
    reviewer: str = Field(..., description="Reviewer or automated validation engine identifier")
    timestamp: str = Field(..., description="ISO 8601 validation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class HypothesisApproval(BaseModel):
    """Immutable domain model representing a status change or approval decision for a ScientificHypothesis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    approval_id: str = Field(
        ...,
        description="Unique deterministic approval ID formatted as HAP_<HEX16>",
        pattern=r"^HAP_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    approver: str = Field(..., description="Approver or authority identifier")
    status: HypothesisStatus = Field(..., description="Resulting target status approved")
    approval_notes: str = Field(default="", description="Governance approval notes or rejection rationale")
    timestamp: str = Field(..., description="ISO 8601 approval timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class HypothesisRegistrySummary(BaseModel):
    """Immutable domain model summarizing the current state of the Scientific Hypothesis Registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(
        ...,
        description="Unique deterministic summary ID formatted as HRS_<HEX16>",
        pattern=r"^HRS_[A-Fa-f0-9]{16,64}$",
    )
    total_hypotheses: int = Field(..., ge=0, description="Total count of registered hypotheses")
    status_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by HypothesisStatus")
    priority_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by HypothesisPriority")
    evidence_level_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by EvidenceLevel")
    timestamp: str = Field(..., description="ISO 8601 snapshot timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
