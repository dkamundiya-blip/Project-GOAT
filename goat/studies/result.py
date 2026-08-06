"""
Project GOAT v0.7 — Study Result Model

Defines the immutable StudyResult model (SRES_<HEX16>) summarizing experiment references and evidence for a study.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_study_result_id(study_id: str, timestamp: str) -> tuple[str, str]:
    """Compute deterministic Study Result ID (SRES_<HEX16>) and full SHA-256 canonical hash.

    Args:
        study_id: Associated Study ID (STD_<HEX16>).
        timestamp: ISO 8601 completion timestamp string.

    Returns:
        Tuple of (result_id, canonical_hash).
    """
    payload = {
        "study_id": str(study_id).strip(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    result_id = f"SRES_{digest[:16].upper()}"
    return result_id, digest


class StudyResult(BaseModel):
    """Immutable representation summarizing the aggregated scientific results of a research study."""

    result_id: str = Field(
        ...,
        description="Unique Study Result ID formatted as SRES_<HEX16>",
        pattern=r"^SRES_[A-Fa-f0-9]{16}$",
    )
    study_id: str = Field(..., description="Parent Study ID (STD_<HEX16>)")
    experiment_references: list[str] = Field(default_factory=list, description="Executed Experiment IDs (EXP_<HEX16>)")
    evidence_references: list[str] = Field(default_factory=list, description="Supporting Evidence IDs (EVD_<HEX16>)")
    knowledge_references: list[str] = Field(default_factory=list, description="Associated Knowledge IDs (KNW_<HEX16>)")
    completion_timestamp: str = Field(..., description="ISO 8601 UTC completion timestamp")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
