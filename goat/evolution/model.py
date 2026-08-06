"""
Project GOAT v0.7 — Knowledge Evolution Model

Defines the immutable KnowledgeEvolution model (KEV_<HEX16>) representing historical knowledge evolution transitions.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.evolution.enums import KnowledgeEvolutionType
from goat.research.edge.canonical import compute_canonical_sha256


def compute_evolution_fingerprint(
    previous_knowledge_id: str,
    new_knowledge_id: str,
    evolution_type: str,
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Knowledge Evolution Fingerprint (EVFP_<HEX64>).

    Args:
        previous_knowledge_id: Previous Knowledge ID (KNW_<HEX16>).
        new_knowledge_id: New Knowledge ID (KNW_<HEX16>).
        evolution_type: KnowledgeEvolutionType string.
        version: Version string.

    Returns:
        String formatted as 'EVFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "evolution_type": str(evolution_type).strip().lower(),
        "new_knowledge_id": str(new_knowledge_id).strip(),
        "previous_knowledge_id": str(previous_knowledge_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EVFP_{digest.upper()}"


def compute_evolution_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Knowledge Evolution ID (KEV_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Knowledge Evolution Fingerprint (EVFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (evolution_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    evolution_id = f"KEV_{digest[:16].upper()}"
    return evolution_id, digest


class KnowledgeEvolution(BaseModel):
    """Immutable master object capturing a version transition in scientific knowledge evolution."""

    evolution_id: str = Field(
        ...,
        description="Unique Evolution ID formatted as KEV_<HEX16>",
        pattern=r"^KEV_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Knowledge Evolution Fingerprint (EVFP_<HEX64>)")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    previous_knowledge_id: str = Field(default="", description="Previous Knowledge ID (KNW_<HEX16>) if applicable")
    new_knowledge_id: str = Field(..., description="New Knowledge ID (KNW_<HEX16>)")
    consensus_id: str = Field(default="", description="Supporting Consensus ID (CNS_<HEX16>)")
    evolution_type: KnowledgeEvolutionType = Field(..., description="Evolution transition classification")
    change_summary: str = Field(..., description="Summary statement explaining why knowledge changed")
    provenance: str = Field(default="system", description="Scientific provenance attribution")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
