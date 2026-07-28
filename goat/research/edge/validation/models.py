"""
Project GOAT v0.6 — Validation Engine Domain Contracts & Models

Defines stage decisions, lifecycle states, holdout states, machine-readable reason codes,
and StageResult abstraction with strict scientific vs operational field separation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from goat.research.edge.canonical import freeze_structure


class StageDecision(str, Enum):
    """Scientific validation outcome decision for a stage."""

    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_RUN = "NOT_RUN"


class ValidationStage(str, Enum):
    """Formal validation stages A through G."""

    STAGE_A_DISCOVERY = "STAGE_A_DISCOVERY"
    STAGE_B_RETENTION = "STAGE_B_RETENTION"
    STAGE_C_TEMPORAL = "STAGE_C_TEMPORAL"
    STAGE_D_ROBUSTNESS = "STAGE_D_ROBUSTNESS"
    STAGE_E_FALSIFICATION = "STAGE_E_FALSIFICATION"
    STAGE_F_REPLICATION = "STAGE_F_REPLICATION"
    STAGE_G_HOLDOUT = "STAGE_G_HOLDOUT"


class ValidationLifecycleState(str, Enum):
    """Validation lifecycle states for CandidateEdge evaluation."""

    REGISTERED = "REGISTERED"
    DISCOVERY_VALIDATION = "DISCOVERY_VALIDATION"
    RETENTION_VALIDATION = "RETENTION_VALIDATION"
    TEMPORAL_STABILITY = "TEMPORAL_STABILITY"
    PARAMETER_ROBUSTNESS = "PARAMETER_ROBUSTNESS"
    FALSIFICATION = "FALSIFICATION"
    CROSS_CONTEXT_REPLICATION = "CROSS_CONTEXT_REPLICATION"
    CONFIRMATORY_READY = "CONFIRMATORY_READY"
    CONFIRMATORY_VALIDATION = "CONFIRMATORY_VALIDATION"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


class HoldoutState(str, Enum):
    """HoldoutAccessGate security states."""

    SEALED = "SEALED"
    AUTHORIZED = "AUTHORIZED"
    ACCESSED = "ACCESSED"
    CONSUMED = "CONSUMED"


class ReasonCode(str, Enum):
    """Machine-readable validation reason codes."""

    PASSED = "PASSED"
    SAMPLE_TOO_SMALL = "SAMPLE_TOO_SMALL"
    EFFECT_TOO_SMALL = "EFFECT_TOO_SMALL"
    SIGNIFICANCE_FAILED = "SIGNIFICANCE_FAILED"
    RETENTION_FAILED = "RETENTION_FAILED"
    DIRECTION_REVERSED = "DIRECTION_REVERSED"
    TEMPORAL_INSTABILITY = "TEMPORAL_INSTABILITY"
    PARAMETER_INSTABILITY = "PARAMETER_INSTABILITY"
    FALSIFICATION_FAILED = "FALSIFICATION_FAILED"
    REPLICATION_FAILED = "REPLICATION_FAILED"
    INSUFFICIENT_CONTEXTS = "INSUFFICIENT_CONTEXTS"
    PREREQUISITE_FAILED = "PREREQUISITE_FAILED"
    HOLDOUT_NOT_AUTHORIZED = "HOLDOUT_NOT_AUTHORIZED"


class StageResult(BaseModel):
    """Immutable result object representing the output of a single validation stage."""

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    # Scientific Identity & Result Fields
    validation_run_id: str
    edge_id: str
    stage: ValidationStage
    decision: StageDecision
    reason_code: ReasonCode
    evidence_ids: Any = Field(default_factory=tuple)
    policy_hash: str

    # Operational Metadata (Excluded from scientific identity/decision logic)
    explanation: str = ""
    started_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_validator("validation_run_id", "edge_id", "policy_hash")
    @classmethod
    def _validate_non_empty(cls, v: str, info: Any) -> str:
        if not str(v).strip():
            raise ValueError(f"Field '{info.field_name}' must be a non-empty string")
        return str(v).strip()

    @field_validator("evidence_ids")
    @classmethod
    def _freeze_evidence_ids(cls, v: Any) -> Any:
        return freeze_structure(v)
