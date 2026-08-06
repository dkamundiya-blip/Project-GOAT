"""
Project GOAT v0.7 — Knowledge Graph Edge Model

Defines the immutable KnowledgeEdge model representing relationship edges in the Knowledge Graph with KEDGE_<HEX16> identity.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from goat.knowledge.enums import KnowledgeRelationshipType
from goat.research.edge.canonical import compute_canonical_sha256


def compute_knowledge_edge_id(
    parent_knowledge_id: str,
    child_knowledge_id: str,
    relationship_type: str,
) -> tuple[str, str]:
    """Compute deterministic Knowledge Edge ID (KEDGE_<HEX16>) and full SHA-256 edge hash digest.

    Args:
        parent_knowledge_id: Upstream parent Knowledge ID.
        child_knowledge_id: Downstream child Knowledge ID.
        relationship_type: KnowledgeRelationshipType string.

    Returns:
        Tuple of (edge_id, edge_hash).
    """
    payload = {
        "child_knowledge_id": str(child_knowledge_id).strip(),
        "parent_knowledge_id": str(parent_knowledge_id).strip(),
        "relationship_type": str(relationship_type).strip().lower(),
    }
    digest = compute_canonical_sha256(payload)
    edge_id = f"KEDGE_{digest[:16].upper()}"
    return edge_id, digest


class KnowledgeEdge(BaseModel):
    """Immutable representation of a relationship edge within the Knowledge Graph."""

    edge_id: str = Field(
        ...,
        description="Unique Knowledge Edge ID formatted as KEDGE_<HEX16>",
        pattern=r"^KEDGE_[A-Fa-f0-9]{16}$",
    )
    parent_knowledge_id: str = Field(..., description="Upstream parent Knowledge ID")
    child_knowledge_id: str = Field(..., description="Downstream child Knowledge ID")
    relationship_type: KnowledgeRelationshipType = Field(..., description="Knowledge relationship classification")
    scientific_notes: str = Field(default="", description="Scientific notes regarding relationship")
    edge_version: str = Field(default="1.0.0", description="Edge specification version")
    edge_hash: str = Field(..., description="Full 64-character SHA-256 canonical edge hash digest")

    class Config:
        frozen = True
        extra = "forbid"
