"""
Project GOAT v0.6 — Validation Report Domain Models

Defines canonical Pydantic models for ValidationReport according to SPEC.4 architecture.
"""

from __future__ import annotations

from typing import Any, Sequence

from pydantic import BaseModel, Field


class EdgeIdentityModel(BaseModel):
    """Immutable domain model for candidate edge identity in report."""

    model_config = {"frozen": True}

    edge_id: str
    proposition_name: str
    causal_primitive: str
    target_feature: str
    economic_rationale_category: str
    base_condition_spec: Any
    edge_schema_version: int = 1


class HypothesisIdentityModel(BaseModel):
    """Immutable domain model for parameterization hypothesis identity in report."""

    model_config = {"frozen": True}

    hypothesis_version: str
    condition_parameters: Any
    forward_outcome_metric: str
    forward_horizon: int


class PolicySpecificationModel(BaseModel):
    """Immutable domain model for frozen validation policy in report."""

    model_config = {"frozen": True}

    policy_hash: str
    policy_id: str
    version: str
    multiplicity_strategy: str
    meta_analysis_method: str
    stage_a_alpha: float
    stage_a_effect_min: float
    stage_a_min_sample: int
    stage_b_min_retention_ratio: float
    stage_c_min_folds: int
    stage_c_min_positive_ratio: float
    stage_c_max_fold_cv: float
    stage_d_perturbation_delta: float
    stage_d_min_stable_ratio: float
    stage_d_max_allowed_drop: float
    stage_e_fail_on_contradictory_inversion: bool
    stage_f_min_replication_pct: float
    stage_f_meta_alpha: float


class DataProvenanceModel(BaseModel):
    """Immutable domain model for dataset & context universe provenance in report."""

    model_config = {"frozen": True}

    dataset_fingerprint: str
    candidate_target_scope: str
    context_universe_id: str = ""
    contexts: tuple[str, ...] = Field(default_factory=tuple)


class ValidationSummaryModel(BaseModel):
    """Immutable domain model for validation lifecycle & decision summary in report."""

    model_config = {"frozen": True}

    lifecycle_state: str
    highest_completed_stage: str
    overall_decision: str
    confirmatory_status: str


class StageSummaryModel(BaseModel):
    """Immutable domain model for individual validation stage summary in report."""

    model_config = {"frozen": True}

    stage: str
    decision: str
    reason_code: str
    explanation: str = ""
    evidence_count: int = 0
    evidence_ids: tuple[str, ...] = Field(default_factory=tuple)


class ConfirmatoryAuditModel(BaseModel):
    """Immutable domain model for confirmatory holdout audit provenance in report."""

    model_config = {"frozen": True}

    audit_id: str
    frozen_hypothesis_version: str
    policy_hash: str
    dataset_fingerprint: str
    holdout_partition_identity: str


class SoftwareProvenanceModel(BaseModel):
    """Immutable domain model for software & environment provenance in report."""

    model_config = {"frozen": True}

    goat_version: str = "v0.6.0"
    python_version: str = "3.14.0"
    git_commit: str = "c32fe497709e5bd03263ede3447a67cf8cc61cf9"


class IntegrityMetadataModel(BaseModel):
    """Immutable domain model for cryptographic integrity proof in report."""

    model_config = {"frozen": True}

    evidence_count: int
    evidence_payload_hashes: tuple[str, ...] = Field(default_factory=tuple)
    report_content_hash: str
    verification_status: str = "VERIFIED"


class ValidationReport(BaseModel):
    """Immutable canonical ValidationReport representation."""

    model_config = {"frozen": True}

    report_schema_version: int = 1
    report_id: str
    validation_run_id: str
    generated_at_utc: str
    edge_identity: EdgeIdentityModel
    hypothesis_identity: HypothesisIdentityModel
    policy_specification: PolicySpecificationModel
    data_provenance: DataProvenanceModel
    validation_summary: ValidationSummaryModel
    stage_results: tuple[StageSummaryModel, ...]
    confirmatory_audit: ConfirmatoryAuditModel | None = None
    software_provenance: SoftwareProvenanceModel = Field(default_factory=SoftwareProvenanceModel)
    integrity: IntegrityMetadataModel
