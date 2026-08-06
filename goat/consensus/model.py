"""
Project GOAT v0.7 — Scientific Consensus Model

Defines the immutable ScientificConsensus model (CNS_<HEX16>) representing overall scientific consensus assessment.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.consensus.enums import ConsensusStatus
from goat.research.edge.canonical import compute_canonical_sha256


def compute_consensus_fingerprint(
    synthesis_ids: list[str],
    knowledge_ids: list[str],
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Scientific Consensus Fingerprint (CNFP_<HEX64>).

    Args:
        synthesis_ids: List of Evidence Synthesis IDs (SYN_<HEX16>).
        knowledge_ids: List of Knowledge IDs (KNW_<HEX16>).
        version: Version string.

    Returns:
        String formatted as 'CNFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "knowledge_ids": sorted([str(k).strip() for k in knowledge_ids]),
        "synthesis_ids": sorted([str(s).strip() for s in synthesis_ids]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"CNFP_{digest.upper()}"


def compute_consensus_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Scientific Consensus ID (CNS_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Scientific Consensus Fingerprint (CNFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (consensus_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    consensus_id = f"CNS_{digest[:16].upper()}"
    return consensus_id, digest


class ScientificConsensus(BaseModel):
    """Immutable scientific object representing formal consensus assessment over synthesized evidence body."""

    consensus_id: str = Field(
        ...,
        description="Unique Consensus ID formatted as CNS_<HEX16>",
        pattern=r"^CNS_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Scientific Consensus Fingerprint (CNFP_<HEX64>)")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    synthesis_ids: list[str] = Field(default_factory=list, description="Supporting Synthesis IDs (SYN_<HEX16>)")
    knowledge_ids: list[str] = Field(default_factory=list, description="Target Knowledge IDs (KNW_<HEX16>)")
    consensus_status: ConsensusStatus = Field(default=ConsensusStatus.INSUFFICIENT_EVIDENCE, description="Consensus status")
    confidence_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence level rating (0.0 to 1.0)")
    conflict_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Conflict level rating (0.0 to 1.0)")
    replication_strength: float = Field(default=0.0, ge=0.0, description="Aggregated replication strength score")
    research_maturity: str = Field(default="early", description="Research maturity classification ('early', 'intermediate', 'mature')")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
