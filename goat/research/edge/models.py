"""
Project GOAT v0.6 — Validation Run & Confirmatory Audit Identity Models

Defines deterministic identity generation functions for ValidationRun (VAL_<HEX16>),
ConfirmatoryAudit (AUD_<HEX16>), and ValidationContextUniverse (CTX_<HEX16>) according to SPEC.3 architecture.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Sequence

from pydantic import BaseModel, Field, field_validator

from goat.research.edge.canonical import compute_canonical_sha256, freeze_structure
from goat.research.edge.enums import EdgeScope


def compute_validation_run_id(
    edge_id: str,
    policy_hash: str,
    dataset_fingerprint: str,
    candidate_target_scope: str | EdgeScope,
    goat_version: str = "v0.6.0",
) -> str:
    """Compute deterministic SHA-256 validation run identity string: VAL_<HEX16>."""
    if not str(edge_id).strip():
        raise ValueError("edge_id must be a non-empty string")
    if not str(policy_hash).strip():
        raise ValueError("policy_hash must be a non-empty string")
    if not str(dataset_fingerprint).strip():
        raise ValueError("dataset_fingerprint must be a non-empty string")

    scope_str = candidate_target_scope.value if isinstance(candidate_target_scope, EdgeScope) else str(candidate_target_scope)

    payload = {
        "candidate_target_scope": scope_str.strip().upper(),
        "dataset_fingerprint": str(dataset_fingerprint).strip(),
        "edge_id": str(edge_id).strip(),
        "policy_hash": str(policy_hash).strip(),
    }
    digest = compute_canonical_sha256(payload, length=16)
    return f"VAL_{digest.upper()}"


def compute_confirmatory_audit_id(
    validation_run_id: str,
    frozen_hypothesis_version: str,
    dataset_fingerprint: str,
    policy_hash: str,
    holdout_partition_identity: str = "holdout_sealed_v1",
) -> str:
    """Compute deterministic SHA-256 confirmatory audit identity string: AUD_<HEX16>."""
    if not str(validation_run_id).strip():
        raise ValueError("validation_run_id must be a non-empty string")
    if not str(frozen_hypothesis_version).strip():
        raise ValueError("frozen_hypothesis_version must be a non-empty string")
    if not str(dataset_fingerprint).strip():
        raise ValueError("dataset_fingerprint must be a non-empty string")
    if not str(policy_hash).strip():
        raise ValueError("policy_hash must be a non-empty string")

    payload = {
        "dataset_fingerprint": str(dataset_fingerprint).strip(),
        "frozen_hypothesis_version": str(frozen_hypothesis_version).strip(),
        "holdout_partition_identity": str(holdout_partition_identity).strip(),
        "policy_hash": str(policy_hash).strip(),
        "validation_run_id": str(validation_run_id).strip(),
    }
    digest = compute_canonical_sha256(payload, length=16)
    return f"AUD_{digest.upper()}"


def compute_universe_id(
    contexts: Sequence[str],
    universe_schema_version: int = 1,
) -> str:
    """Compute deterministic SHA-256 pre-registered context universe identity string: CTX_<HEX16>."""
    clean_contexts = sorted({str(k).strip() for k in contexts if str(k).strip()})
    if not clean_contexts:
        raise ValueError("contexts must be a non-empty sequence of context key strings")

    payload = {
        "contexts": clean_contexts,
        "universe_schema_version": int(universe_schema_version),
    }
    digest = compute_canonical_sha256(payload, length=16)
    return f"CTX_{digest.upper()}"


class ValidationContextUniverse(BaseModel):
    """Immutable domain model for a pre-registered context universe."""

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    universe_id: str = ""
    universe_schema_version: int = 1
    contexts: Any = Field(default_factory=tuple)
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("contexts")
    @classmethod
    def _validate_contexts(cls, v: Any) -> Any:
        clean = sorted({str(k).strip() for k in v if str(k).strip()})
        if not clean:
            raise ValueError("contexts must be a non-empty sequence of context key strings")
        return freeze_structure(tuple(clean))

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        computed = compute_universe_id(
            contexts=self.contexts,
            universe_schema_version=self.universe_schema_version,
        )
        if self.universe_id and self.universe_id != computed:
            raise ValueError(f"Supplied universe_id '{self.universe_id}' does not match computed '{computed}'")
        object.__setattr__(self, "universe_id", computed)


class ValidationRunInfo(BaseModel):
    """Immutable metadata model for a validation run."""

    model_config = {"frozen": True}

    validation_run_id: str = ""
    edge_id: str
    policy_hash: str
    dataset_fingerprint: str
    candidate_target_scope: EdgeScope
    goat_version: str = "v0.6.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("edge_id", "policy_hash", "dataset_fingerprint")
    @classmethod
    def _validate_non_empty(cls, v: str, info: Any) -> str:
        if not str(v).strip():
            raise ValueError(f"Field '{info.field_name}' must be a non-empty string")
        return str(v).strip()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        computed = compute_validation_run_id(
            edge_id=self.edge_id,
            policy_hash=self.policy_hash,
            dataset_fingerprint=self.dataset_fingerprint,
            candidate_target_scope=self.candidate_target_scope,
            goat_version=self.goat_version,
        )
        if self.validation_run_id and self.validation_run_id != computed:
            raise ValueError(f"Supplied validation_run_id '{self.validation_run_id}' does not match computed '{computed}'")
        object.__setattr__(self, "validation_run_id", computed)
