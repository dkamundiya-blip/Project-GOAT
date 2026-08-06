"""
Project GOAT v0.7 — Scientific Experiment Model

Defines the immutable ScientificExperiment model (EXP_<HEX16>) representing formal scientific experiment procedures.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.experiments.enums import ExperimentStatus
from goat.research.edge.canonical import compute_canonical_sha256


def compute_experiment_fingerprint(
    name: str,
    objective: str,
    hypothesis_id: str,
    protocol_version: str = "1.0.0",
) -> str:
    """Compute deterministic Scientific Experiment Fingerprint (EFP_<HEX64>).

    Args:
        name: Experiment name.
        objective: Formal scientific objective.
        hypothesis_id: Associated Hypothesis ID (HYP_<HEX16>).
        protocol_version: Protocol version string.

    Returns:
        String formatted as 'EFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "hypothesis_id": str(hypothesis_id).strip(),
        "name": str(name).strip(),
        "objective": str(objective).strip(),
        "protocol_version": str(protocol_version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EFP_{digest.upper()}"


def compute_experiment_id(name: str, fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Scientific Experiment ID (EXP_<HEX16>) and full SHA-256 canonical hash.

    Args:
        name: Experiment name.
        fingerprint: Scientific Experiment Fingerprint (EFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (experiment_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "name": str(name).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    experiment_id = f"EXP_{digest[:16].upper()}"
    return experiment_id, digest


class ScientificExperiment(BaseModel):
    """Immutable scientific object representing a formal scientific experiment procedure."""

    experiment_id: str = Field(
        ...,
        description="Unique Experiment ID formatted as EXP_<HEX16>",
        pattern=r"^EXP_[A-Fa-f0-9]{16}$",
    )
    scientific_fingerprint: str = Field(..., description="Scientific Experiment Fingerprint (EFP_<HEX64>)")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    name: str = Field(..., description="Experiment name")
    objective: str = Field(..., description="Formal scientific objective statement")
    hypothesis_id: str = Field(..., description="Associated Hypothesis ID (HYP_<HEX16>)")
    pipeline_id: str = Field(default="", description="Associated Research Pipeline ID (PIPE_<HEX16>)")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    start_timestamp: str = Field(default="", description="ISO 8601 UTC execution start timestamp")
    completion_timestamp: str = Field(default="", description="ISO 8601 UTC completion timestamp")
    protocol_version: str = Field(default="1.0.0", description="Associated Protocol version string")
    status: ExperimentStatus = Field(default=ExperimentStatus.PROPOSED, description="Experiment lifecycle status")
    provenance_metadata: dict[str, Any] = Field(default_factory=dict, description="Scientific provenance annotations")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
