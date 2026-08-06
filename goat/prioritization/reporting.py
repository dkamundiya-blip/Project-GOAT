"""
Project GOAT v0.7 — Research Prioritization Reporting Module

Implements immutable ResearchPriorityReport summarizing ranked research opportunities and priority queue statistics.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.prioritization.queue import ResearchPriorityQueue
from goat.research.edge.canonical import compute_canonical_sha256


class ResearchPriorityReport(BaseModel):
    """Immutable report summarizing scientific research prioritization findings and ranked queue statistics."""

    report_id: str = Field(..., description="Unique Priority Report ID (RPREP_<HEX16>)")
    queue_id: str = Field(..., description="Parent Queue ID (RPQ_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    ranked_opportunities: list[str] = Field(default_factory=list, description="Ranked Priority IDs (RPR_<HEX16>)")
    queue_statistics: dict[str, Any] = Field(default_factory=dict, description="Queue statistics")
    consensus_summaries: dict[str, Any] = Field(default_factory=dict, description="Consensus status summary")
    unresolved_conflicts: list[str] = Field(default_factory=list, description="Unresolved Conflict IDs")
    knowledge_maturity: str = Field(default="early", description="Overall research maturity classification")
    scientific_justifications: list[str] = Field(default_factory=list, description="Top opportunity justification statements")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log summary")

    class Config:
        frozen = True
        extra = "forbid"


def generate_priority_report(
    queue: ResearchPriorityQueue,
    justifications: list[str] | None = None,
    unresolved_conflicts: list[str] | None = None,
    timestamp: str = "",
) -> ResearchPriorityReport:
    """Generate deterministic ResearchPriorityReport.

    Args:
        queue: ResearchPriorityQueue instance.
        justifications: List of scientific justification strings.
        unresolved_conflicts: List of unresolved Conflict IDs.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable ResearchPriorityReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "queue_id": queue.queue_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"RPREP_{digest[:16].upper()}"

    return ResearchPriorityReport(
        report_id=report_id,
        queue_id=queue.queue_id,
        timestamp=ts,
        ranked_opportunities=queue.ordered_priority_ids,
        queue_statistics={"total_prioritized_candidates": len(queue.ordered_priority_ids)},
        consensus_summaries={"evaluated": len(queue.ordered_priority_ids)},
        unresolved_conflicts=unresolved_conflicts or [],
        scientific_justifications=justifications or [],
        audit_summary={"status": "clean"},
    )
