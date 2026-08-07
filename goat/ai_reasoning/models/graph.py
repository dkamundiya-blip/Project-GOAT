"""
Project GOAT Phase 7 — Research Knowledge Graph Domain Models

Defines immutable Pydantic models for Research Knowledge Graph nodes, edges, and SHA-256 canonical hashing.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class NodeType(str, Enum):
    """Types of nodes in the Research Knowledge Graph."""
    FEATURE = "FEATURE"
    HYPOTHESIS = "HYPOTHESIS"
    EDGE = "EDGE"
    REGIME = "REGIME"
    SYMBOL = "SYMBOL"
    SESSION = "SESSION"
    TIMEFRAME = "TIMEFRAME"
    VALIDATION_RESULT = "VALIDATION_RESULT"


class EdgeType(str, Enum):
    """Types of directed relationships between graph nodes."""
    DERIVED_FROM = "DERIVED_FROM"
    EVALUATED_BY = "EVALUATED_BY"
    VALIDATED_ON = "VALIDATED_ON"
    ACTIVE_IN = "ACTIVE_IN"
    APPLIES_TO = "APPLIES_TO"
    DECAYS_IN = "DECAYS_IN"


class ResearchGraphNode(BaseModel):
    """Immutable node in the Research Knowledge Graph."""

    node_id: str = Field(..., description="Unique node ID formatted as RKN_<HEX16>", pattern=r"^RKN_[A-Fa-f0-9]{16}$")
    node_type: NodeType = Field(..., description="Category of research node")
    name: str = Field(..., description="Human-readable node label/key")
    properties: dict[str, Any] = Field(default_factory=dict, description="Node attribute dictionary")
    canonical_hash: str = Field(..., description="SHA-256 canonical digest")

    class Config:
        frozen = True
        extra = "forbid"


class ResearchGraphEdge(BaseModel):
    """Immutable directed edge connecting two research nodes."""

    edge_id: str = Field(..., description="Unique edge ID formatted as RKE_<HEX16>", pattern=r"^RKE_[A-Fa-f0-9]{16}$")
    source_id: str = Field(..., description="Source node_id")
    target_id: str = Field(..., description="Target node_id")
    edge_type: EdgeType = Field(..., description="Relationship classification")
    properties: dict[str, Any] = Field(default_factory=dict, description="Edge metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_node_id(node_type: NodeType, name: str) -> tuple[str, str]:
    """Compute deterministic node_id and canonical_hash for a ResearchGraphNode."""
    payload = {"name": name.strip(), "node_type": node_type.value}
    digest = compute_canonical_sha256(payload)
    return f"RKN_{digest[:16].upper()}", digest.upper()


def compute_edge_id(source_id: str, target_id: str, edge_type: EdgeType) -> tuple[str, str]:
    """Compute deterministic edge_id and canonical_hash for a ResearchGraphEdge."""
    payload = {"edge_type": edge_type.value, "source_id": source_id.strip(), "target_id": target_id.strip()}
    digest = compute_canonical_sha256(payload)
    return f"RKE_{digest[:16].upper()}", digest.upper()
