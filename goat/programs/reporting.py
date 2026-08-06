"""
Project GOAT v0.7 — Program Reporting Module

Implements immutable ProgramReport summarizing research program execution, milestone achievements, study statistics, and audit logs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.programs.design import ProgramDesign
from goat.programs.model import ScientificResearchProgram
from goat.programs.result import ProgramResult
from goat.research.edge.canonical import compute_canonical_sha256


class ProgramReport(BaseModel):
    """Immutable report summarizing scientific research program execution and audit findings."""

    report_id: str = Field(..., description="Unique Program Report ID (PREP_<HEX16>)")
    program_id: str = Field(..., description="Parent Program ID (PRG_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    final_status: str = Field(..., description="Final ProgramStatus string")
    design_summary: dict[str, Any] = Field(default_factory=dict, description="Program design summary")
    study_statistics: dict[str, Any] = Field(default_factory=dict, description="Study counts and statistics")
    experiment_statistics: dict[str, Any] = Field(default_factory=dict, description="Experiment counts")
    evidence_statistics: dict[str, Any] = Field(default_factory=dict, description="Evidence references count")
    knowledge_statistics: dict[str, Any] = Field(default_factory=dict, description="Knowledge references count")
    milestone_summary: dict[str, Any] = Field(default_factory=dict, description="Milestone status summary")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log event statistics")
    execution_timeline: list[str] = Field(default_factory=list, description="Execution timeline milestones")

    class Config:
        frozen = True
        extra = "forbid"


def generate_program_report(
    program: ScientificResearchProgram,
    design: ProgramDesign | None = None,
    result: ProgramResult | None = None,
    audit_events: list[Any] | None = None,
    timestamp: str = "",
) -> ProgramReport:
    """Generate deterministic ProgramReport.

    Args:
        program: ScientificResearchProgram instance.
        design: Optional ProgramDesign instance.
        result: Optional ProgramResult instance.
        audit_events: Optional list of ProgramAuditEvents.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable ProgramReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "program_id": program.program_id,
        "status": program.program_status.value,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"PREP_{digest[:16].upper()}"

    des_summary = {
        "objectives": design.strategic_objectives if design else "",
        "version": design.design_version if design else "",
    }

    std_count = len(result.study_references) if result else 0
    exp_count = len(result.experiment_references) if result else 0
    evd_count = len(result.evidence_references) if result else 0
    knw_count = len(result.knowledge_references) if result else 0

    timeline = [
        f"Created research program '{program.program_title}' at {program.creation_timestamp}.",
        f"Domain: {program.scientific_domain}.",
        f"Status: {program.program_status.value}.",
    ]
    if result:
        timeline.append(f"Completed research program with {std_count} studies at {result.completion_timestamp}.")

    return ProgramReport(
        report_id=report_id,
        program_id=program.program_id,
        timestamp=ts,
        final_status=program.program_status.value,
        design_summary=des_summary,
        study_statistics={"total_executed_studies": std_count},
        experiment_statistics={"total_executed_experiments": exp_count},
        evidence_statistics={"total_evidence_references": evd_count},
        knowledge_statistics={"total_knowledge_references": knw_count},
        milestone_summary={"total_milestones": len(design.milestone_ids) if design else 0},
        audit_summary={"total_audit_events": len(audit_events or [])},
        execution_timeline=timeline,
    )
