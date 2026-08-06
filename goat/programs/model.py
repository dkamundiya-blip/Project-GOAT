"""
Project GOAT v0.7 — Scientific Research Program Model

Defines the immutable ScientificResearchProgram model (PRG_<HEX16>) representing top-level research program initiatives.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.programs.enums import ProgramStatus
from goat.research.edge.canonical import compute_canonical_sha256


def compute_program_fingerprint(
    title: str,
    domain: str,
    objective: str,
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Scientific Program Fingerprint (PFP_<HEX64>).

    Args:
        title: Program title string.
        domain: Scientific domain classification string.
        objective: Strategic objective string.
        version: Version string.

    Returns:
        String formatted as 'PFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "domain": str(domain).strip(),
        "objective": str(objective).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PFP_{digest.upper()}"


def compute_program_id(title: str, fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Scientific Program ID (PRG_<HEX16>) and full SHA-256 canonical hash.

    Args:
        title: Program title.
        fingerprint: Scientific Program Fingerprint (PFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (program_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    program_id = f"PRG_{digest[:16].upper()}"
    return program_id, digest


class ScientificResearchProgram(BaseModel):
    """Immutable master object representing a long-term scientific research program initiative."""

    program_id: str = Field(
        ...,
        description="Unique Program ID formatted as PRG_<HEX16>",
        pattern=r"^PRG_[A-Fa-f0-9]{16}$",
    )
    scientific_fingerprint: str = Field(..., description="Scientific Program Fingerprint (PFP_<HEX64>)")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    program_title: str = Field(..., description="Program title")
    scientific_domain: str = Field(..., description="Scientific domain classification")
    strategic_objective: str = Field(..., description="Formal strategic objective statement")
    program_description: str = Field(..., description="Comprehensive program description")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    completion_timestamp: str = Field(default="", description="ISO 8601 UTC completion timestamp")
    program_status: ProgramStatus = Field(default=ProgramStatus.PROPOSED, description="Program lifecycle status")
    program_version: str = Field(default="1.0.0", description="Program specification version string")
    provenance_metadata: dict[str, Any] = Field(default_factory=dict, description="Scientific provenance annotations")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
