"""
Project GOAT v0.7 — Knowledge Evolution Reporting Module

Implements immutable KnowledgeEvolutionReport summarizing knowledge version evolution, lineage, and consensus references.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.evolution.model import KnowledgeEvolution
from goat.evolution.version import KnowledgeVersion
from goat.research.edge.canonical import compute_canonical_sha256


class KnowledgeEvolutionReport(BaseModel):
    """Immutable report summarizing scientific knowledge evolution and version transitions."""

    report_id: str = Field(..., description="Unique Evolution Report ID (EREP_<HEX16>)")
    evolution_id: str = Field(..., description="Parent Evolution ID (KEV_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    previous_version_id: str = Field(default="", description="Previous Version ID (KVR_<HEX16>)")
    current_version_id: str = Field(..., description="Current Version ID (KVR_<HEX16>)")
    evolution_type: str = Field(..., description="KnowledgeEvolutionType string")
    consensus_reference: str = Field(default="", description="Consensus reference (CNS_<HEX16>)")
    change_summary: str = Field(..., description="Statement explaining why knowledge changed")
    lineage_statistics: dict[str, Any] = Field(default_factory=dict, description="Lineage statistics")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log summary")

    class Config:
        frozen = True
        extra = "forbid"


def generate_evolution_report(
    evolution: KnowledgeEvolution,
    current_version: KnowledgeVersion,
    ancestors_count: int = 0,
    timestamp: str = "",
) -> KnowledgeEvolutionReport:
    """Generate deterministic KnowledgeEvolutionReport.

    Args:
        evolution: KnowledgeEvolution instance.
        current_version: Current KnowledgeVersion instance.
        ancestors_count: Count of ancestor versions.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable KnowledgeEvolutionReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "evolution_id": evolution.evolution_id,
        "version_id": current_version.version_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"EREP_{digest[:16].upper()}"

    return KnowledgeEvolutionReport(
        report_id=report_id,
        evolution_id=evolution.evolution_id,
        timestamp=ts,
        previous_version_id=current_version.parent_version_id,
        current_version_id=current_version.version_id,
        evolution_type=evolution.evolution_type.value,
        consensus_reference=evolution.consensus_id,
        change_summary=evolution.change_summary,
        lineage_statistics={"ancestors_count": ancestors_count, "version_number": current_version.version_number},
        audit_summary={"status": "clean"},
    )
