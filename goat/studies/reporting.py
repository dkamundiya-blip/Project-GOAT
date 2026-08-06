"""
Project GOAT v0.7 — Study Reporting Module

Implements immutable StudyReport summarizing study execution timeline, experiment statistics, evidence counts, and audit logs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.studies.design import StudyDesign
from goat.studies.model import ScientificStudy
from goat.studies.result import StudyResult


class StudyReport(BaseModel):
    """Immutable report summarizing scientific study execution and audit findings."""

    report_id: str = Field(..., description="Unique Study Report ID (SREP_<HEX16>)")
    study_id: str = Field(..., description="Parent Study ID (STD_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    final_status: str = Field(..., description="Final StudyStatus string")
    design_summary: dict[str, Any] = Field(default_factory=dict, description="Study design summary")
    experiment_statistics: dict[str, Any] = Field(default_factory=dict, description="Experiment counts and ordering")
    evidence_counts: dict[str, Any] = Field(default_factory=dict, description="Evidence references count")
    knowledge_counts: dict[str, Any] = Field(default_factory=dict, description="Knowledge references count")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log event statistics")
    execution_timeline: list[str] = Field(default_factory=list, description="Execution timeline milestones")

    class Config:
        frozen = True
        extra = "forbid"


def generate_study_report(
    study: ScientificStudy,
    design: StudyDesign | None = None,
    result: StudyResult | None = None,
    audit_events: list[Any] | None = None,
    timestamp: str = "",
) -> StudyReport:
    """Generate deterministic StudyReport.

    Args:
        study: ScientificStudy instance.
        design: Optional StudyDesign instance.
        result: Optional StudyResult instance.
        audit_events: Optional list of StudyAuditEvents.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable StudyReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "status": study.status.value,
        "study_id": study.study_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SREP_{digest[:16].upper()}"

    des_summary = {
        "objective": design.research_objective if design else "",
        "version": design.design_version if design else "",
    }

    exp_count = len(result.experiment_references) if result else 0
    evd_count = len(result.evidence_references) if result else 0
    knw_count = len(result.knowledge_references) if result else 0

    timeline = [
        f"Created study '{study.title}' at {study.creation_timestamp}.",
        f"Status: {study.status.value}.",
    ]
    if result:
        timeline.append(f"Completed study with {exp_count} experiments at {result.completion_timestamp}.")

    return StudyReport(
        report_id=report_id,
        study_id=study.study_id,
        timestamp=ts,
        final_status=study.status.value,
        design_summary=des_summary,
        experiment_statistics={"total_executed_experiments": exp_count},
        evidence_counts={"total_evidence_references": evd_count},
        knowledge_counts={"total_knowledge_references": knw_count},
        audit_summary={"total_audit_events": len(audit_events or [])},
        execution_timeline=timeline,
    )
