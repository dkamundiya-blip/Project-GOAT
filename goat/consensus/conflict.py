"""
Project GOAT v0.7 — Consensus Conflict Model

Defines the immutable ConsensusConflict model (CCF_<HEX16>) recording unresolved scientific evidence disagreements.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_conflict_id(evidence_references: list[str], severity: str = "high") -> tuple[str, str]:
    """Compute deterministic Consensus Conflict ID (CCF_<HEX16>) and full SHA-256 conflict hash.

    Args:
        evidence_references: List of Evidence IDs (EVD_<HEX16>) in conflict.
        severity: Conflict severity string.

    Returns:
        Tuple of (conflict_id, conflict_hash).
    """
    payload = {
        "evidence_references": sorted([str(e).strip() for e in evidence_references]),
        "severity": str(severity).strip().lower(),
    }
    digest = compute_canonical_sha256(payload)
    conflict_id = f"CCF_{digest[:16].upper()}"
    return conflict_id, digest


class ConsensusConflict(BaseModel):
    """Immutable record capturing unresolved scientific disagreements across evidence syntheses."""

    conflict_id: str = Field(
        ...,
        description="Unique Consensus Conflict ID formatted as CCF_<HEX16>",
        pattern=r"^CCF_[A-Fa-f0-9]{16}$",
    )
    evidence_references: list[str] = Field(default_factory=list, description="Evidence IDs (EVD_<HEX16>) involved")
    synthesis_references: list[str] = Field(default_factory=list, description="Synthesis IDs (SYN_<HEX16>) involved")
    severity: str = Field(default="high", description="Conflict severity rating")
    resolution_status: str = Field(default="unresolved", description="Resolution status ('unresolved', 'resolved', 'dismissed')")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    conflict_hash: str = Field(..., description="Full 64-character SHA-256 canonical conflict hash digest")

    class Config:
        frozen = True
        extra = "forbid"
