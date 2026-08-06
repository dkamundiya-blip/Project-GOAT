"""
Project GOAT v0.7 — Knowledge Registry Domain Models

Defines KnowledgeRegistryRecord and KnowledgeAuditEvent domain models for Knowledge Objects.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.knowledge.enums import KnowledgeStatus, KnowledgeType
from goat.knowledge.evidence import EvidenceReference
from goat.knowledge.model import KnowledgeObject


class KnowledgeRegistryRecord(BaseModel):
    """Authoritative registry record wrapping a KnowledgeObject with persistence metadata."""

    knowledge_id: str = Field(..., description="Target Knowledge ID (KNW_<HEX16>)")
    scientific_fingerprint: str = Field(..., description="Scientific Knowledge Fingerprint (KFP_<HEX64>)")
    canonical_hash: str = Field(..., description="Canonical hash digest")
    semantic_version: str = Field(default="1.0.0", description="Semantic version string")
    knowledge_type: KnowledgeType = Field(..., description="Taxonomy classification")
    knowledge_status: KnowledgeStatus = Field(default=KnowledgeStatus.PROVISIONAL, description="Status")
    title: str = Field(..., description="Scientific title")
    knowledge_object: KnowledgeObject = Field(..., description="Wrapped KnowledgeObject instance")
    evidence_references: list[EvidenceReference] = Field(default_factory=list, description="Linked EvidenceReferences")
    registration_timestamp: str = Field(..., description="ISO 8601 UTC registration timestamp")
    provenance: str = Field(default="system", description="Registration provenance")
    notes: str = Field(default="", description="Registration notes")

    class Config:
        frozen = True
        extra = "forbid"


class KnowledgeAuditEvent(BaseModel):
    """Immutable audit trail log event for Knowledge Registry operations."""

    event_id: str = Field(..., description="Unique audit event ID")
    knowledge_id: str = Field(..., description="Target Knowledge ID")
    event_type: str = Field(..., description="Event type string ('REGISTER', 'STATUS_CHANGE', 'VERIFY')")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    previous_state: str = Field(default="", description="Previous status string")
    new_state: str = Field(default="", description="New status string")
    provenance: str = Field(default="system", description="Event provenance")
    notes: str = Field(default="", description="Event notes")

    class Config:
        frozen = True
        extra = "forbid"
