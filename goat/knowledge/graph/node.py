"""
Project GOAT v0.7 — Knowledge Graph Node Model

Defines the immutable KnowledgeNode model representing nodes in the Knowledge Graph with KNODE_<HEX16> identity.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_knowledge_node_id(knowledge_id: str, scientific_fingerprint: str, depth: int = 0) -> str:
    """Compute deterministic Knowledge Node ID (KNODE_<HEX16>).

    Args:
        knowledge_id: Target Knowledge ID (KNW_<HEX16>).
        scientific_fingerprint: Scientific Knowledge Fingerprint (KFP_<HEX64>).
        depth: Dependency depth integer.

    Returns:
        String formatted as 'KNODE_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "depth": int(depth),
        "knowledge_id": str(knowledge_id).strip(),
        "scientific_fingerprint": str(scientific_fingerprint).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"KNODE_{digest[:16].upper()}"


class KnowledgeNode(BaseModel):
    """Immutable representation of a node within the Knowledge Graph."""

    node_id: str = Field(
        ...,
        description="Unique Knowledge Node ID formatted as KNODE_<HEX16>",
        pattern=r"^KNODE_[A-Fa-f0-9]{16}$",
    )
    knowledge_id: str = Field(..., description="Target Knowledge ID (KNW_<HEX16>)")
    scientific_fingerprint: str = Field(..., description="Scientific Knowledge Fingerprint (KFP_<HEX64>)")
    canonical_hash: str = Field(..., description="Canonical hash digest")
    knowledge_type: str = Field(..., description="Knowledge taxonomy type")
    depth: int = Field(default=0, ge=0, description="Node depth in Knowledge Graph")
    topological_index: int = Field(default=0, ge=0, description="Topological evaluation ordering index")
    node_metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
