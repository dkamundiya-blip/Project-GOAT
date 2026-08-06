"""
Project GOAT v0.7 — Scientific Study Model

Defines the immutable ScientificStudy model (STD_<HEX16>) representing multi-experiment scientific research studies.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.studies.enums import StudyStatus


def compute_study_fingerprint(
    title: str,
    question: str,
    objective: str,
    design_version: str = "1.0.0",
) -> str:
    """Compute deterministic Scientific Study Fingerprint (SFP_<HEX64>).

    Args:
        title: Study title string.
        question: Scientific research question string.
        objective: Formal research objective string.
        design_version: Design version string.

    Returns:
        String formatted as 'SFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "design_version": str(design_version).strip(),
        "objective": str(objective).strip(),
        "question": str(question).strip(),
        "title": str(title).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"SFP_{digest.upper()}"


def compute_study_id(title: str, fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Scientific Study ID (STD_<HEX16>) and full SHA-256 canonical hash.

    Args:
        title: Study title.
        fingerprint: Scientific Study Fingerprint (SFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (study_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    study_id = f"STD_{digest[:16].upper()}"
    return study_id, digest


class ScientificStudy(BaseModel):
    """Immutable representation of a master scientific research study coordinating multiple experiments."""

    study_id: str = Field(
        ...,
        description="Unique Study ID formatted as STD_<HEX16>",
        pattern=r"^STD_[A-Fa-f0-9]{16}$",
    )
    scientific_fingerprint: str = Field(..., description="Scientific Study Fingerprint (SFP_<HEX64>)")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    title: str = Field(..., description="Study title")
    scientific_question: str = Field(..., description="Target scientific question under investigation")
    research_objective: str = Field(..., description="Formal scientific objective statement")
    description: str = Field(..., description="Comprehensive study description")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    completion_timestamp: str = Field(default="", description="ISO 8601 UTC completion timestamp")
    status: StudyStatus = Field(default=StudyStatus.PROPOSED, description="Study lifecycle status")
    protocol_version: str = Field(default="1.0.0", description="Associated protocol/design version string")
    provenance_metadata: dict[str, Any] = Field(default_factory=dict, description="Scientific provenance annotations")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
