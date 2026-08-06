"""
Project GOAT v0.7 — Experiment Result Model

Defines the immutable ExperimentResult model (RES_<HEX16>) storing verified experiment outcomes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.experiments.enums import ExperimentOutcome
from goat.research.edge.canonical import compute_canonical_sha256


def compute_result_id(experiment_id: str, outcome: str, timestamp: str) -> tuple[str, str]:
    """Compute deterministic Experiment Result ID (RES_<HEX16>) and full SHA-256 canonical hash.

    Args:
        experiment_id: Associated Experiment ID (EXP_<HEX16>).
        outcome: ExperimentOutcome string.
        timestamp: ISO 8601 completion timestamp string.

    Returns:
        Tuple of (result_id, canonical_hash).
    """
    payload = {
        "experiment_id": str(experiment_id).strip(),
        "outcome": str(outcome).strip().lower(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    result_id = f"RES_{digest[:16].upper()}"
    return result_id, digest


class ExperimentResult(BaseModel):
    """Immutable representation of a scientific experiment execution outcome."""

    result_id: str = Field(
        ...,
        description="Unique Result ID formatted as RES_<HEX16>",
        pattern=r"^RES_[A-Fa-f0-9]{16}$",
    )
    experiment_id: str = Field(..., description="Associated Experiment ID (EXP_<HEX16>)")
    outcome: ExperimentOutcome = Field(..., description="Experiment outcome classification")
    supporting_evidence_ids: list[str] = Field(default_factory=list, description="Supporting Evidence IDs (EVD_<HEX16>)")
    validation_references: list[str] = Field(default_factory=list, description="Stage A-G Validation Report IDs")
    knowledge_references: list[str] = Field(default_factory=list, description="Associated Knowledge IDs (KNW_<HEX16>)")
    completion_timestamp: str = Field(..., description="ISO 8601 UTC completion timestamp")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
