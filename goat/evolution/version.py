"""
Project GOAT v0.7 — Knowledge Version Model

Defines the immutable KnowledgeVersion model (KVR_<HEX16>) representing versioned scientific knowledge states.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_version_id(knowledge_id: str, version_number: int = 1) -> tuple[str, str]:
    """Compute deterministic Knowledge Version ID (KVR_<HEX16>) and full SHA-256 version hash.

    Args:
        knowledge_id: Target Knowledge ID (KNW_<HEX16>).
        version_number: Version number integer.

    Returns:
        Tuple of (version_id, version_hash).
    """
    payload = {
        "knowledge_id": str(knowledge_id).strip(),
        "version_number": int(version_number),
    }
    digest = compute_canonical_sha256(payload)
    version_id = f"KVR_{digest[:16].upper()}"
    return version_id, digest


class KnowledgeVersion(BaseModel):
    """Immutable version object representing a specific historical or active version of a scientific knowledge object."""

    version_id: str = Field(
        ...,
        description="Unique Version ID formatted as KVR_<HEX16>",
        pattern=r"^KVR_[A-Fa-f0-9]{16}$",
    )
    knowledge_id: str = Field(..., description="Target Knowledge ID (KNW_<HEX16>)")
    version_number: int = Field(default=1, ge=1, description="1-indexed version number")
    parent_version_id: str = Field(default="", description="Parent Version ID (KVR_<HEX16>) if refined/superseded")
    child_version_ids: list[str] = Field(default_factory=list, description="Child Version IDs (KVR_<HEX16>)")
    consensus_reference: str = Field(default="", description="Supporting Consensus ID (CNS_<HEX16>)")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    status: str = Field(default="active", description="Version status ('active', 'superseded', 'retired')")
    version_hash: str = Field(..., description="Full 64-character SHA-256 canonical version hash digest")

    class Config:
        frozen = True
        extra = "forbid"
