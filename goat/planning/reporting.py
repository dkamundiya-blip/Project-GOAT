"""
Project GOAT v0.7 — Scientific Planning Reporting Module

Implements immutable ScientificPlanningReport summarizing plan tasks, execution order, and complexity.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.planning.model import ScientificPlan
from goat.research.edge.canonical import compute_canonical_sha256


class ScientificPlanningReport(BaseModel):
    """Immutable report summarizing scientific planning task DAGs and execution sequence."""

    report_id: str = Field(..., description="Unique Planning Report ID (PREP_<HEX16>)")
    plan_id: str = Field(..., description="Parent Plan ID (PLN_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    task_statistics: dict[str, Any] = Field(default_factory=dict, description="Task count statistics")
    dependency_statistics: dict[str, Any] = Field(default_factory=dict, description="Dependency graph statistics")
    topological_execution_order: list[str] = Field(default_factory=list, description="Ordered Task IDs in topological order")
    complexity_assessment: str = Field(default="moderate", description="Complexity assessment")
    supporting_priorities: list[str] = Field(default_factory=list, description="Supporting Priority IDs")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log summary")

    class Config:
        frozen = True
        extra = "forbid"


def generate_planning_report(
    plan: ScientificPlan,
    topological_order: list[str],
    timestamp: str = "",
) -> ScientificPlanningReport:
    """Generate deterministic ScientificPlanningReport.

    Args:
        plan: ScientificPlan instance.
        topological_order: List of task IDs in topological execution order.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable ScientificPlanningReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "plan_id": plan.plan_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"PREP_{digest[:16].upper()}"

    return ScientificPlanningReport(
        report_id=report_id,
        plan_id=plan.plan_id,
        timestamp=ts,
        task_statistics={"total_planned_tasks": len(topological_order)},
        dependency_statistics={"graph_id": plan.dependency_graph_id},
        topological_execution_order=topological_order,
        complexity_assessment=plan.estimated_complexity,
        supporting_priorities=plan.source_priority_ids,
        audit_summary={"status": "clean"},
    )
