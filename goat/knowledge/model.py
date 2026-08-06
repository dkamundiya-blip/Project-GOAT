"""
Project GOAT v0.7 — Knowledge Object Model

Defines the immutable KnowledgeObject model representing preserved scientific knowledge (KNW_<HEX16>)
with deterministic fingerprinting (KFP_<HEX64>) and canonical serialization.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.knowledge.enums import KnowledgeStatus, KnowledgeType
from goat.research.edge.canonical import compute_canonical_sha256


def compute_knowledge_fingerprint(
    knowledge_type: str,
    title: str,
    abstract: str,
    parent_ids: list[str],
) -> str:
    """Compute deterministic Scientific Knowledge Fingerprint (KFP_<HEX64>).

    Args:
        knowledge_type: KnowledgeType string value.
        title: Scientific title string.
        abstract: Scientific abstract or formula text.
        parent_ids: Upstream parent knowledge IDs.

    Returns:
        String formatted as 'KFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "abstract": str(abstract).strip(),
        "knowledge_type": str(knowledge_type).strip().lower(),
        "parent_ids": sorted([str(p).strip() for p in parent_ids]),
        "title": str(title).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"KFP_{digest.upper()}"


def compute_knowledge_id(knowledge_type: str, scientific_fingerprint: str, semantic_version: str = "1.0.0") -> str:
    """Compute deterministic Knowledge ID (KNW_<HEX16>).

    Args:
        knowledge_type: KnowledgeType string value.
        scientific_fingerprint: Scientific Knowledge Fingerprint (KFP_<HEX64>).
        semantic_version: Semantic version string.

    Returns:
        String formatted as 'KNW_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "knowledge_type": str(knowledge_type).strip().lower(),
        "scientific_fingerprint": str(scientific_fingerprint).strip(),
        "version": str(semantic_version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"KNW_{digest[:16].upper()}"


class KnowledgeObject(BaseModel):
    """Immutable representation of a verified scientific knowledge object."""

    knowledge_id: str = Field(
        ...,
        description="Unique Knowledge ID formatted as KNW_<HEX16>",
        pattern=r"^KNW_[A-Fa-f0-9]{16}$",
    )
    scientific_fingerprint: str = Field(..., description="Scientific Knowledge Fingerprint (KFP_<HEX64>)")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    semantic_version: str = Field(default="1.0.0", description="Semantic version string")
    knowledge_type: KnowledgeType = Field(..., description="Taxonomy classification type")
    title: str = Field(..., description="Scientific title")
    description: str = Field(..., description="Detailed scientific description")
    abstract: str = Field(default="", description="Formal scientific abstract or equation summary")
    source_artifact_ids: list[str] = Field(default_factory=list, description="Associated source artifact IDs")
    parent_knowledge_ids: list[str] = Field(default_factory=list, description="Upstream parent Knowledge IDs")
    supporting_evidence_ids: list[str] = Field(default_factory=list, description="Supporting Evidence IDs (EVD_<HEX16>)")
    related_knowledge_ids: list[str] = Field(default_factory=list, description="Cross-referenced Knowledge IDs")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    last_verified_timestamp: str = Field(..., description="ISO 8601 UTC last verification timestamp")
    registry_version: str = Field(default="1.0.0", description="Registry schema version")
    provenance_metadata: dict[str, Any] = Field(default_factory=dict, description="Scientific provenance annotations")
    scientific_notes: str = Field(default="", description="Scientific commentary and observation notes")
    knowledge_status: KnowledgeStatus = Field(default=KnowledgeStatus.PROVISIONAL, description="Lifecycle status")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Append-only audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
