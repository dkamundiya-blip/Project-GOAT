"""
Project GOAT v0.9 — Immutable Pydantic V2 Domain Models for Edge Knowledge Graph Subsystem
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.knowledge.core.enums import (
    NodeType,
    PathValidity,
    RelationshipType,
    ValidationStatus,
)


class KnowledgeNode(BaseModel):
    """Immutable Node in the Scientific Knowledge Graph."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str = Field(..., description="Deterministic node ID with prefix KND_")
    node_type: NodeType = Field(..., description="Classification of knowledge entity")
    entity_id: str = Field(..., description="Referenced underlying entity ID (e.g. OBS_, EDC_, etc.)")
    label: str = Field(..., description="Human and machine readable entity label")
    timestamp: str = Field(..., description="ISO-8601 timestamp of entity creation")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Arbitrary entity attributes")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class KnowledgeRelationship(BaseModel):
    """Immutable Directed Edge / Relationship in the Scientific Knowledge Graph."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    relationship_id: str = Field(..., description="Deterministic relationship ID with prefix REL_")
    source_node_id: str = Field(..., description="Source KnowledgeNode ID")
    target_node_id: str = Field(..., description="Target KnowledgeNode ID")
    relationship_type: RelationshipType = Field(..., description="Directed relationship classification")
    weight: float = Field(default=1.0, ge=0.0, description="Strength / weight of scientific link")
    timestamp: str = Field(..., description="ISO-8601 timestamp of link creation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class KnowledgeGraph(BaseModel):
    """Immutable Scientific Knowledge Graph State Container."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    graph_id: str = Field(..., description="Deterministic graph ID with prefix KGR_")
    graph_name: str = Field(..., description="Descriptive name of knowledge graph")
    node_ids: list[str] = Field(default_factory=list, description="IDs of graph nodes")
    relationship_ids: list[str] = Field(default_factory=list, description="IDs of graph relationships")
    created_at: str = Field(..., description="ISO-8601 creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class ScientificPath(BaseModel):
    """Immutable Traversal Path Representing an Unbroken Scientific Lineage Chain."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    path_id: str = Field(..., description="Deterministic path ID with prefix PTH_")
    source_node_id: str = Field(..., description="Starting source node ID")
    target_node_id: str = Field(..., description="Ending target node ID")
    node_chain: list[str] = Field(..., min_length=1, description="Ordered sequence of node IDs in path")
    relationship_chain: list[str] = Field(default_factory=list, description="Ordered sequence of relationship IDs")
    validity: PathValidity = Field(..., description="Scientific path validity classification")
    path_length: int = Field(..., ge=0, description="Number of hops in path")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class RelationshipValidation(BaseModel):
    """Immutable Validation Assessment for Knowledge Graph Audit."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    validation_id: str = Field(..., description="Deterministic validation ID with prefix VAL_")
    graph_id: str = Field(..., description="Validated KnowledgeGraph ID")
    status: ValidationStatus = Field(..., description="Overall validation status")
    is_valid: bool = Field(..., description="Boolean indicating whether graph integrity is sound")
    broken_chain_count: int = Field(default=0, ge=0, description="Count of broken scientific chains")
    orphan_node_count: int = Field(default=0, ge=0, description="Count of isolated orphan nodes")
    cycle_count: int = Field(default=0, ge=0, description="Count of invalid circular cycles")
    duplicate_count: int = Field(default=0, ge=0, description="Count of duplicate relationships")
    violations: list[str] = Field(default_factory=list, description="Detailed text descriptions of violations")
    timestamp: str = Field(..., description="ISO-8601 audit timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class KnowledgeSummary(BaseModel):
    """Immutable Executive Summary of the Edge Knowledge Graph Memory."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(..., description="Deterministic summary ID with prefix KSM_")
    timestamp: str = Field(..., description="ISO-8601 summary timestamp")
    total_nodes: int = Field(default=0, ge=0, description="Total nodes count")
    total_relationships: int = Field(default=0, ge=0, description="Total relationships count")
    total_graphs: int = Field(default=0, ge=0, description="Total archived knowledge graphs count")
    total_paths_analyzed: int = Field(default=0, ge=0, description="Total scientific paths analyzed")
    node_type_counts: dict[str, int] = Field(default_factory=dict, description="Node counts by NodeType")
    relationship_type_counts: dict[str, int] = Field(default_factory=dict, description="Relationship counts by RelationshipType")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")
