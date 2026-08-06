"""
Project GOAT v0.7 — Scientific Graph Edge Model

Defines the immutable GraphEdge model representing dependency relationships between features in the DAG,
with deterministic EDGE_<HEX16> identity calculation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_edge_id(
    parent_feature_id: str,
    child_feature_id: str,
    dependency_type: str = "required",
) -> tuple[str, str]:
    """Compute deterministic Graph Edge ID (EDGE_<HEX16>) and full SHA-256 edge hash digest.

    Args:
        parent_feature_id: Upstream parent Feature ID.
        child_feature_id: Downstream child Feature ID.
        dependency_type: Dependency classification ('required', 'optional').

    Returns:
        Tuple of (edge_id, edge_hash) where:
          - edge_id is 'EDGE_' + first 16 uppercase hex chars of digest.
          - edge_hash is full 64-char hex digest.
    """
    payload = {
        "child_feature_id": str(child_feature_id).strip(),
        "dependency_type": str(dependency_type).strip().lower(),
        "parent_feature_id": str(parent_feature_id).strip(),
    }
    digest = compute_canonical_sha256(payload)
    edge_id = f"EDGE_{digest[:16].upper()}"
    return edge_id, digest


class GraphEdge(BaseModel):
    """Immutable representation of a directed dependency edge within the Feature Dependency Graph."""

    edge_id: str = Field(
        ...,
        description="Unique Graph Edge ID formatted as EDGE_<HEX16>",
        pattern=r"^EDGE_[A-Fa-f0-9]{16}$",
    )
    parent_feature_id: str = Field(..., description="Upstream parent Feature ID")
    child_feature_id: str = Field(..., description="Downstream child Feature ID")
    dependency_type: str = Field(default="required", description="Dependency type: 'required' or 'optional'")
    is_required: bool = Field(default=True, description="Boolean flag indicating if dependency is non-optional")
    scientific_notes: str = Field(default="", description="Scientific notes regarding the edge relationship")
    edge_version: str = Field(default="1.0.0", description="Edge specification version")
    edge_hash: str = Field(..., description="Full 64-character SHA-256 canonical edge hash digest")

    class Config:
        frozen = True
        extra = "forbid"
