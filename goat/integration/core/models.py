"""
Project GOAT v0.7 — Core Immutable Models for Knowledge Integration & Evidence Graph

Defines immutable Pydantic domain models:
- KnowledgeNode (KND_<HEX16>)
- KnowledgeEdge (KED_<HEX16>)
- IntegratedKnowledge (IKN_<HEX16>)
- ConflictRecord (CFL_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.enums import (
    ConflictSeverity,
    ConflictType,
    KnowledgeNodeType,
    KnowledgeRelationship,
)


class KnowledgeNode(BaseModel):
    """Immutable node in the scientific knowledge graph."""

    node_id: str = Field(
        ...,
        description="Unique deterministic node ID formatted as KND_<HEX16>",
        pattern=r"^KND_[A-Fa-f0-9]{16}$",
    )
    title: str = Field(..., description="Descriptive title of the knowledge node")
    node_type: KnowledgeNodeType = Field(..., description="Node classification type")
    description: str = Field(default="", description="Detailed narrative description")
    originating_validation: str = Field(..., description="Originating Validation Run/Result ID")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
    fingerprint: str = Field(default="", description="Scientific Node Fingerprint (NDFP_<HEX64>)")

    class Config:
        frozen = True
        extra = "forbid"


class KnowledgeEdge(BaseModel):
    """Immutable directed edge between two knowledge nodes."""

    edge_id: str = Field(
        ...,
        description="Unique deterministic edge ID formatted as KED_<HEX16>",
        pattern=r"^KED_[A-Fa-f0-9]{16}$",
    )
    source_node: str = Field(..., description="Source node ID (KND_<HEX16>)")
    destination_node: str = Field(..., description="Destination node ID (KND_<HEX16>)")
    relationship: KnowledgeRelationship = Field(..., description="Relationship classification")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Edge confidence score (0.0 to 1.0)")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Edge metadata")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class IntegratedKnowledge(BaseModel):
    """Immutable representation of accumulated scientific understanding."""

    knowledge_id: str = Field(
        ...,
        description="Unique deterministic integrated knowledge ID formatted as IKN_<HEX16>",
        pattern=r"^IKN_[A-Fa-f0-9]{16}$",
    )
    participating_validations: list[str] = Field(default_factory=list, description="IDs of component validations")
    participating_hypotheses: list[str] = Field(default_factory=list, description="IDs of component hypotheses")
    participating_experiments: list[str] = Field(default_factory=list, description="IDs of component experiments")
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence rating")
    reproducibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Reproducibility score")
    consensus_strength: float = Field(default=0.0, ge=0.0, le=1.0, description="Consensus strength score")
    conflict_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Conflict score (0.0=no conflict)")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
    version: str = Field(default="1.0.0", description="Specification semantic version")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit tracking metadata")

    class Config:
        frozen = True
        extra = "forbid"


class ConflictRecord(BaseModel):
    """Immutable record of conflicting or ambiguous scientific findings."""

    conflict_id: str = Field(
        ...,
        description="Unique deterministic conflict ID formatted as CFL_<HEX16>",
        pattern=r"^CFL_[A-Fa-f0-9]{16}$",
    )
    validation_a: str = Field(..., description="First validation ID involved in conflict")
    validation_b: str = Field(..., description="Second validation ID involved in conflict")
    conflict_type: ConflictType = Field(..., description="Conflict classification type")
    severity: ConflictSeverity = Field(default=ConflictSeverity.MEDIUM, description="Conflict severity level")
    explanation: str = Field(..., description="Deterministic rationale for conflict classification")
    supporting_evidence: list[str] = Field(default_factory=list, description="List of evidence IDs demonstrating conflict")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
    timestamp: str = Field(default="", description="ISO 8601 UTC timestamp")

    class Config:
        frozen = True
        extra = "forbid"
