"""
Project GOAT v0.7 — Program Result Model

Defines the immutable ProgramResult model (PRES_<HEX16>) summarizing study, experiment, evidence, and knowledge references for a program.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_program_result_id(program_id: str, timestamp: str) -> tuple[str, str]:
    """Compute deterministic Program Result ID (PRES_<HEX16>) and full SHA-256 canonical hash.

    Args:
        program_id: Associated Program ID (PRG_<HEX16>).
        timestamp: ISO 8601 completion timestamp string.

    Returns:
        Tuple of (result_id, canonical_hash).
    """
    payload = {
        "program_id": str(program_id).strip(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    result_id = f"PRES_{digest[:16].upper()}"
    return result_id, digest


class ProgramResult(BaseModel):
    """Immutable representation summarizing the aggregated scientific results of a research program initiative."""

    result_id: str = Field(
        ...,
        description="Unique Program Result ID formatted as PRES_<HEX16>",
        pattern=r"^PRES_[A-Fa-f0-9]{16}$",
    )
    program_id: str = Field(..., description="Parent Program ID (PRG_<HEX16>)")
    study_references: list[str] = Field(default_factory=list, description="Executed Study IDs (STD_<HEX16>)")
    experiment_references: list[str] = Field(default_factory=list, description="Executed Experiment IDs (EXP_<HEX16>)")
    evidence_references: list[str] = Field(default_factory=list, description="Supporting Evidence IDs (EVD_<HEX16>)")
    knowledge_references: list[str] = Field(default_factory=list, description="Associated Knowledge IDs (KNW_<HEX16>)")
    completion_timestamp: str = Field(..., description="ISO 8601 UTC completion timestamp")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
