"""
Project GOAT v0.7 — Scientific Graph Node Model

Defines the immutable GraphNode model representing structural feature nodes in the dependency DAG,
with deterministic NODE_<HEX16> identity calculation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_node_id(feature_id: str, scientific_fingerprint: str, depth: int = 0) -> str:
    """Compute deterministic Graph Node ID (NODE_<HEX16>).

    Args:
        feature_id: Feature ID (FEAT_<HEX16>).
        scientific_fingerprint: Scientific Feature Fingerprint (FPT_<HEX64>).
        depth: Integer dependency depth in DAG.

    Returns:
        String formatted as 'NODE_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "depth": int(depth),
        "feature_id": str(feature_id).strip(),
        "scientific_fingerprint": str(scientific_fingerprint).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NODE_{digest[:16].upper()}"


class GraphNode(BaseModel):
    """Immutable representation of a scientific node within the Feature Dependency Graph."""

    node_id: str = Field(
        ...,
        description="Unique Graph Node ID formatted as NODE_<HEX16>",
        pattern=r"^NODE_[A-Fa-f0-9]{16}$",
    )
    feature_id: str = Field(..., description="Target Feature ID (FEAT_<HEX16>)")
    scientific_fingerprint: str = Field(..., description="Scientific Feature Fingerprint (FPT_<HEX64>)")
    canonical_hash: str = Field(..., description="SHA-256 canonical AST hash digest")
    node_version: str = Field(default="1.0.0", description="Graph node specification version")
    dependency_depth: int = Field(default=0, ge=0, description="Dependency depth from root primitives")
    topological_index: int = Field(default=0, ge=0, description="Topological evaluation ordering index")
    graph_hash_reference: str = Field(default="", description="Reference digest of parent graph topology")
    node_metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata annotations")
    node_status: str = Field(default="active", description="Node status in graph ('active', 'deprecated')")
    node_provenance: str = Field(default="system", description="Node generation provenance")

    class Config:
        frozen = True
        extra = "forbid"
