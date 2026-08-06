"""
Project GOAT v0.7 — Consensus Reporting Module

Implements immutable ConsensusReport summarizing scientific consensus status, research maturity, and unresolved conflicts.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.consensus.model import ScientificConsensus
from goat.research.edge.canonical import compute_canonical_sha256


class ConsensusReport(BaseModel):
    """Immutable report summarizing scientific consensus evaluation findings."""

    report_id: str = Field(..., description="Unique Consensus Report ID (CREP_<HEX16>)")
    consensus_id: str = Field(..., description="Parent Consensus ID (CNS_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    status_summary: str = Field(..., description="ConsensusStatus string")
    supporting_syntheses: list[str] = Field(default_factory=list, description="Supporting Synthesis IDs")
    replication_statistics: dict[str, Any] = Field(default_factory=dict, description="Replication strength statistics")
    contradiction_statistics: dict[str, Any] = Field(default_factory=dict, description="Conflict level statistics")
    confidence_statistics: dict[str, Any] = Field(default_factory=dict, description="Confidence level statistics")
    maturity_assessment: str = Field(..., description="Research maturity classification")
    unresolved_conflicts: list[str] = Field(default_factory=list, description="Unresolved Conflict IDs")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log summary")

    class Config:
        frozen = True
        extra = "forbid"


def generate_consensus_report(
    consensus: ScientificConsensus,
    unresolved_conflicts: list[str] | None = None,
    timestamp: str = "",
) -> ConsensusReport:
    """Generate deterministic ConsensusReport.

    Args:
        consensus: ScientificConsensus instance.
        unresolved_conflicts: Optional list of unresolved Conflict IDs.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable ConsensusReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "consensus_id": consensus.consensus_id,
        "status": consensus.consensus_status.value,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"CREP_{digest[:16].upper()}"

    return ConsensusReport(
        report_id=report_id,
        consensus_id=consensus.consensus_id,
        timestamp=ts,
        status_summary=consensus.consensus_status.value,
        supporting_syntheses=consensus.synthesis_ids,
        replication_statistics={"replication_strength": consensus.replication_strength},
        contradiction_statistics={"conflict_level": consensus.conflict_level},
        confidence_statistics={"confidence_level": consensus.confidence_level},
        maturity_assessment=consensus.research_maturity,
        unresolved_conflicts=unresolved_conflicts or [],
        audit_summary={"status": "clean"},
    )
