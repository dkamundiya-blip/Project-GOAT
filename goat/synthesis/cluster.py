"""
Project GOAT v0.7 — Evidence Cluster Model

Defines the immutable EvidenceCluster model (CLS_<HEX16>) grouping related evidence references with confidence statistics.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_cluster_id(member_evidence_ids: list[str]) -> tuple[str, str]:
    """Compute deterministic Evidence Cluster ID (CLS_<HEX16>) and full SHA-256 cluster hash.

    Args:
        member_evidence_ids: List of Evidence IDs (EVD_<HEX16>) in cluster.

    Returns:
        Tuple of (cluster_id, cluster_hash).
    """
    payload = {
        "members": sorted([str(e).strip() for e in member_evidence_ids]),
    }
    digest = compute_canonical_sha256(payload)
    cluster_id = f"CLS_{digest[:16].upper()}"
    return cluster_id, digest


class EvidenceCluster(BaseModel):
    """Immutable scientific cluster grouping related evidence references with statistical confidence annotations."""

    cluster_id: str = Field(
        ...,
        description="Unique Evidence Cluster ID formatted as CLS_<HEX16>",
        pattern=r"^CLS_[A-Fa-f0-9]{16}$",
    )
    member_evidence_ids: list[str] = Field(default_factory=list, description="Member Evidence IDs (EVD_<HEX16>)")
    supporting_study_ids: list[str] = Field(default_factory=list, description="Supporting Study IDs (STD_<HEX16>)")
    supporting_experiment_ids: list[str] = Field(default_factory=list, description="Supporting Experiment IDs (EXP_<HEX16>)")
    confidence_statistics: dict[str, Any] = Field(default_factory=dict, description="Aggregated confidence statistics")
    replication_count: int = Field(default=0, ge=0, description="Count of independent replications")
    provenance: str = Field(default="system", description="Scientific provenance string")
    cluster_hash: str = Field(..., description="Full 64-character SHA-256 canonical cluster hash digest")

    class Config:
        frozen = True
        extra = "forbid"
