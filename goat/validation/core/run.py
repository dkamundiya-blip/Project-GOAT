"""
Project GOAT v0.7 — Validation Run Model

Defines the immutable ValidationRun model (VRN_<HEX16>) representing one
execution of a scientific hypothesis validation process.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.validation.core.enums import DecisionType, ValidationState


def compute_run_fingerprint(
    hypothesis_id: str,
    evidence_ids: list[str],
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Validation Run Fingerprint (VRNFP_<HEX64>).

    Args:
        hypothesis_id: Hypothesis ID (HYP_<HEX16>).
        evidence_ids: Evidence IDs used in this run.
        version: Version string.

    Returns:
        String formatted as 'VRNFP_' + 64 uppercase hex characters.
    """
    payload = {
        "evidence_ids": sorted([str(e).strip() for e in evidence_ids]),
        "hypothesis_id": str(hypothesis_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"VRNFP_{digest.upper()}"


def compute_run_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Validation Run ID (VRN_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Validation Run Fingerprint (VRNFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (validation_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    validation_id = f"VRN_{digest[:16].upper()}"
    return validation_id, digest


class ValidationRun(BaseModel):
    """Immutable record of one execution of a scientific hypothesis validation."""

    validation_id: str = Field(
        ...,
        description="Unique Validation Run ID formatted as VRN_<HEX16>",
        pattern=r"^VRN_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Validation Run Fingerprint (VRNFP_<HEX64>)")
    semantic_version: str = Field(default="1.0.0", description="Semantic version")
    hypothesis_id: str = Field(..., description="Hypothesis ID (HYP_<HEX16>)")
    execution_id: str = Field(default="", description="Execution Session ID (SES_<HEX16>)")
    evidence_ids: list[str] = Field(default_factory=list, description="Evidence IDs used in this validation")
    statistical_results: dict[str, Any] = Field(default_factory=dict, description="Computed statistical scores")
    evidence_summary: dict[str, Any] = Field(default_factory=dict, description="Evidence aggregation summary")
    confidence_metrics: dict[str, float] = Field(default_factory=dict, description="Confidence metric values")
    validation_decision: str = Field(default="", description="Decision type (accepted/rejected/...)")
    decision_id: str = Field(default="", description="Decision ID (VDC_<HEX16>)")
    replay_hash: str = Field(default="", description="Replay verification hash")
    validation_state: ValidationState = Field(
        default=ValidationState.PENDING,
        description="Validation lifecycle state",
    )
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    completion_timestamp: str = Field(default="", description="ISO 8601 UTC completion timestamp")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
