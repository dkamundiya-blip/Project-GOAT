"""
Project GOAT v0.7 — Validation Evidence Models

Defines the immutable ValidationEvidence model (VEV_<HEX16>) storing
all evidence supporting or rejecting a hypothesis.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_evidence_id(
    validation_run_id: str,
    experiment_reference: str,
    evidence_type: str,
    timestamp: str,
) -> tuple[str, str]:
    """Compute deterministic Validation Evidence ID (VEV_<HEX16>) and full SHA-256 hash.

    Args:
        validation_run_id: Parent Validation Run ID (VRN_<HEX16>).
        experiment_reference: Source reference ID.
        evidence_type: Evidence type string.
        timestamp: ISO 8601 UTC timestamp.

    Returns:
        Tuple of (evidence_id, evidence_hash).
    """
    payload = {
        "evidence_type": str(evidence_type).strip(),
        "experiment_reference": str(experiment_reference).strip(),
        "timestamp": str(timestamp).strip(),
        "validation_run_id": str(validation_run_id).strip(),
    }
    digest = compute_canonical_sha256(payload)
    evidence_id = f"VEV_{digest[:16].upper()}"
    return evidence_id, digest


class ValidationEvidence(BaseModel):
    """Immutable evidence record supporting or rejecting a scientific hypothesis."""

    evidence_id: str = Field(
        ...,
        description="Unique Evidence ID formatted as VEV_<HEX16>",
        pattern=r"^VEV_[A-Fa-f0-9]{16}$",
    )
    evidence_hash: str = Field(..., description="Full 64-character SHA-256 canonical evidence hash")
    validation_run_id: str = Field(default="", description="Parent Validation Run ID (VRN_<HEX16>)")
    experiment_reference: str = Field(default="", description="Source Experiment ID (EXP_<HEX16>)")
    study_reference: str = Field(default="", description="Source Study ID (STD_<HEX16>)")
    feature_reference: str = Field(default="", description="Source Feature ID")
    consensus_reference: str = Field(default="", description="Source Consensus ID (CNS_<HEX16>)")
    execution_reference: str = Field(default="", description="Source Execution Session ID (SES_<HEX16>)")
    evidence_type: str = Field(default="experiment", description="Evidence type classification")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence confidence [0.0, 1.0]")
    weight: float = Field(default=1.0, ge=0.0, description="Evidence weight for aggregation")
    supports_hypothesis: bool = Field(default=True, description="True if evidence supports the hypothesis")
    notes: str = Field(default="", description="Evidence notes")
    timestamp: str = Field(..., description="ISO 8601 UTC evidence timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Evidence metadata")

    class Config:
        frozen = True
        extra = "forbid"
