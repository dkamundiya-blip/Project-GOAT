"""
Project GOAT v0.7 — Scientific Scheduling Reporting Module

Implements immutable ScientificSchedulingReport summarizing schedule execution queues,
dependency statistics, and task state breakdowns.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.scheduling.enums import ScheduleExecutionState
from goat.scheduling.model import ResearchSchedule
from goat.scheduling.task import ScheduledTask


class ScientificSchedulingReport(BaseModel):
    """Immutable report summarizing scientific scheduling execution state and dependency statistics."""

    report_id: str = Field(..., description="Unique Scheduling Report ID (SREP_<HEX16>)")
    schedule_id: str = Field(..., description="Parent Schedule ID (SCH_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    schedule_metadata: dict[str, Any] = Field(default_factory=dict, description="Schedule-level metadata")
    execution_queue: list[str] = Field(default_factory=list, description="Ordered task IDs in execution order")
    dependency_statistics: dict[str, Any] = Field(default_factory=dict, description="Dependency graph statistics")
    blocked_tasks: list[str] = Field(default_factory=list, description="Task IDs currently blocked")
    completed_tasks: list[str] = Field(default_factory=list, description="Task IDs completed")
    waiting_tasks: list[str] = Field(default_factory=list, description="Task IDs waiting for dependencies")
    execution_readiness: float = Field(default=0.0, ge=0.0, le=1.0, description="Fraction of tasks ready or completed")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit trail summary")

    class Config:
        frozen = True
        extra = "forbid"


def generate_scheduling_report(
    schedule: ResearchSchedule,
    tasks: list[ScheduledTask],
    timestamp: str = "",
) -> ScientificSchedulingReport:
    """Generate deterministic ScientificSchedulingReport.

    Args:
        schedule: ResearchSchedule instance.
        tasks: List of ScheduledTask instances belonging to the schedule.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable ScientificSchedulingReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "schedule_id": schedule.schedule_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SREP_{digest[:16].upper()}"

    # Categorize tasks by state
    blocked = [t.task_schedule_id for t in tasks if t.execution_state == ScheduleExecutionState.BLOCKED]
    completed = [t.task_schedule_id for t in tasks if t.execution_state == ScheduleExecutionState.COMPLETED]
    waiting = [t.task_schedule_id for t in tasks if t.execution_state == ScheduleExecutionState.WAITING]
    ready = [t.task_schedule_id for t in tasks if t.execution_state == ScheduleExecutionState.READY]
    pending = [t.task_schedule_id for t in tasks if t.execution_state == ScheduleExecutionState.PENDING]

    total = len(tasks)
    ready_or_completed = len(ready) + len(completed)
    readiness = round(ready_or_completed / total, 10) if total > 0 else 0.0

    # Dependency statistics
    satisfied_count = sum(1 for t in tasks if t.dependency_satisfaction)
    dep_stats = {
        "total_tasks": total,
        "dependencies_satisfied": satisfied_count,
        "dependencies_unsatisfied": total - satisfied_count,
    }

    return ScientificSchedulingReport(
        report_id=report_id,
        schedule_id=schedule.schedule_id,
        timestamp=ts,
        schedule_metadata={
            "schedule_id": schedule.schedule_id,
            "semantic_version": schedule.semantic_version,
            "source_plan_count": len(schedule.source_plan_ids),
            "total_scheduled_tasks": total,
        },
        execution_queue=list(schedule.execution_order),
        dependency_statistics=dep_stats,
        blocked_tasks=blocked,
        completed_tasks=completed,
        waiting_tasks=waiting,
        execution_readiness=readiness,
        audit_summary={"status": "clean", "pending_count": len(pending), "ready_count": len(ready)},
    )
