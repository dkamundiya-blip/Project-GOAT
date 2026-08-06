"""
Project GOAT v0.7 — Experiment Reporting Module

Implements immutable ExperimentReport summarizing experiment execution timeline, protocol rules, evidence references, and audit events.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.experiments.model import ScientificExperiment
from goat.experiments.protocol import ExperimentProtocol
from goat.experiments.result import ExperimentResult
from goat.research.edge.canonical import compute_canonical_sha256


class ExperimentReport(BaseModel):
    """Immutable report summarizing scientific experiment execution and audit findings."""

    report_id: str = Field(..., description="Unique Experiment Report ID (EREP_<HEX16>)")
    experiment_id: str = Field(..., description="Parent Experiment ID (EXP_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    final_status: str = Field(..., description="Final ExperimentStatus string")
    protocol_summary: dict[str, Any] = Field(default_factory=dict, description="Protocol specification summary")
    outcome_summary: dict[str, Any] = Field(default_factory=dict, description="Outcome and result summary")
    evidence_summary: dict[str, Any] = Field(default_factory=dict, description="Evidence references summary")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit event trail summary")
    execution_timeline: list[str] = Field(default_factory=list, description="Execution timeline milestones")

    class Config:
        frozen = True
        extra = "forbid"


def generate_experiment_report(
    experiment: ScientificExperiment,
    protocol: ExperimentProtocol | None = None,
    result: ExperimentResult | None = None,
    audit_events: list[Any] | None = None,
    timestamp: str = "",
) -> ExperimentReport:
    """Generate deterministic ExperimentReport.

    Args:
        experiment: ScientificExperiment instance.
        protocol: Optional ExperimentProtocol instance.
        result: Optional ExperimentResult instance.
        audit_events: Optional list of ExperimentAuditEvents.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable ExperimentReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    
    payload = {
        "exp_id": experiment.experiment_id,
        "status": experiment.status.value,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"EREP_{digest[:16].upper()}"

    prot_dict = {
        "name": protocol.protocol_name if protocol else "",
        "stages_count": len(protocol.stages) if protocol else 0,
        "version": protocol.protocol_version if protocol else "",
    }

    res_dict = {
        "outcome": result.outcome.value if result else "pending",
        "result_id": result.result_id if result else "",
    }

    timeline = [
        f"Created experiment '{experiment.name}' at {experiment.creation_timestamp}.",
        f"Status: {experiment.status.value}.",
    ]
    if result:
        timeline.append(f"Completed experiment with outcome '{result.outcome.value}' at {result.completion_timestamp}.")

    return ExperimentReport(
        report_id=report_id,
        experiment_id=experiment.experiment_id,
        timestamp=ts,
        final_status=experiment.status.value,
        protocol_summary=prot_dict,
        outcome_summary=res_dict,
        evidence_summary={"supporting_evidence_count": len(result.supporting_evidence_ids) if result else 0},
        audit_summary={"total_audit_events": len(audit_events or [])},
        execution_timeline=timeline,
    )
