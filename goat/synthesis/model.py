"""
Project GOAT v0.7 — Evidence Synthesis Model

Defines the immutable EvidenceSynthesis model (SYN_<HEX16>) representing aggregated scientific evidence findings.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_synthesis_fingerprint(
    evidence_ids: list[str],
    knowledge_ids: list[str],
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Evidence Synthesis Fingerprint (SFP_<HEX64>).

    Args:
        evidence_ids: List of Evidence IDs (EVD_<HEX16>).
        knowledge_ids: List of Knowledge IDs (KNW_<HEX16>).
        version: Semantic version string.

    Returns:
        String formatted as 'SFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "evidence_ids": sorted([str(e).strip() for e in evidence_ids]),
        "knowledge_ids": sorted([str(k).strip() for k in knowledge_ids]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"SFP_{digest.upper()}"


def compute_synthesis_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Evidence Synthesis ID (SYN_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Scientific Synthesis Fingerprint (SFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (synthesis_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    synthesis_id = f"SYN_{digest[:16].upper()}"
    return synthesis_id, digest


class EvidenceSynthesis(BaseModel):
    """Immutable scientific object representing aggregated evidence synthesis findings across studies."""

    synthesis_id: str = Field(
        ...,
        description="Unique Synthesis ID formatted as SYN_<HEX16>",
        pattern=r"^SYN_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Scientific Synthesis Fingerprint (SFP_<HEX64>)")
    version: str = Field(default="1.0.0", description="Semantic specification version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    evidence_ids: list[str] = Field(default_factory=list, description="Aggregated Evidence IDs (EVD_<HEX16>)")
    knowledge_ids: list[str] = Field(default_factory=list, description="Associated Knowledge IDs (KNW_<HEX16>)")
    confidence_summary: dict[str, Any] = Field(default_factory=dict, description="Aggregated confidence statistics summary")
    replication_summary: dict[str, Any] = Field(default_factory=dict, description="Replication analysis summary")
    conflict_summary: dict[str, Any] = Field(default_factory=dict, description="Contradiction analysis summary")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
