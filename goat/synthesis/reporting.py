"""
Project GOAT v0.7 — Evidence Synthesis Reporting Module

Implements immutable EvidenceSynthesisReport summarizing evidence counts, clusters, contradictions, and replications.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.synthesis.model import EvidenceSynthesis


class EvidenceSynthesisReport(BaseModel):
    """Immutable report summarizing scientific evidence synthesis findings."""

    report_id: str = Field(..., description="Unique Synthesis Report ID (SREP_<HEX16>)")
    synthesis_id: str = Field(..., description="Parent Synthesis ID (SYN_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    evidence_counts: dict[str, int] = Field(default_factory=dict, description="Evidence references statistics")
    cluster_counts: dict[str, int] = Field(default_factory=dict, description="Cluster counts")
    contradiction_statistics: dict[str, Any] = Field(default_factory=dict, description="Contradiction analysis statistics")
    replication_statistics: dict[str, Any] = Field(default_factory=dict, description="Replication analysis statistics")
    confidence_statistics: dict[str, Any] = Field(default_factory=dict, description="Confidence statistics summary")
    provenance_summary: dict[str, Any] = Field(default_factory=dict, description="Provenance summary annotations")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log summary")

    class Config:
        frozen = True
        extra = "forbid"


def generate_synthesis_report(
    synthesis: EvidenceSynthesis,
    clusters_count: int = 0,
    timestamp: str = "",
) -> EvidenceSynthesisReport:
    """Generate deterministic EvidenceSynthesisReport.

    Args:
        synthesis: EvidenceSynthesis instance.
        clusters_count: Total clusters count.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable EvidenceSynthesisReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "synthesis_id": synthesis.synthesis_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SREP_{digest[:16].upper()}"

    return EvidenceSynthesisReport(
        report_id=report_id,
        synthesis_id=synthesis.synthesis_id,
        timestamp=ts,
        evidence_counts={"total_evidence": len(synthesis.evidence_ids)},
        cluster_counts={"total_clusters": clusters_count},
        contradiction_statistics=synthesis.conflict_summary,
        replication_statistics=synthesis.replication_summary,
        confidence_statistics=synthesis.confidence_summary,
        provenance_summary={"version": synthesis.version},
        audit_summary={"status": "clean"},
    )
