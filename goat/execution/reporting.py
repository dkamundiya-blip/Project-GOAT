"""
Project GOAT v0.7 — Scientific Execution Reporting Module

Implements immutable ScientificExecutionReport summarizing execution sessions,
event statistics, execution timelines, and task completion status.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.execution.enums import ExecutionState
from goat.execution.event import ExecutionEvent
from goat.execution.model import ScientificExecutionSession
from goat.research.edge.canonical import compute_canonical_sha256


class ScientificExecutionReport(BaseModel):
    """Immutable report summarizing scientific execution session state and event statistics."""

    report_id: str = Field(..., description="Unique Execution Report ID (EREP_<HEX16>)")
    session_id: str = Field(..., description="Parent Session ID (SES_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    session_metadata: dict[str, Any] = Field(default_factory=dict, description="Session-level metadata")
    executed_tasks: list[str] = Field(default_factory=list, description="Executed task IDs in order")
    execution_timeline: list[dict[str, Any]] = Field(default_factory=list, description="Chronological event timeline")
    event_statistics: dict[str, Any] = Field(default_factory=dict, description="Event type counts and statistics")
    execution_duration: str = Field(default="", description="Total execution duration (ISO 8601 duration or descriptive)")
    completed_tasks: list[str] = Field(default_factory=list, description="Task IDs that completed successfully")
    failed_tasks: list[str] = Field(default_factory=list, description="Task IDs that failed")
    replay_verification: str = Field(default="not_verified", description="Replay verification status")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit trail summary")

    class Config:
        frozen = True
        extra = "forbid"


def generate_execution_report(
    session: ScientificExecutionSession,
    events: list[ExecutionEvent],
    timestamp: str = "",
) -> ScientificExecutionReport:
    """Generate deterministic ScientificExecutionReport.

    Args:
        session: ScientificExecutionSession instance.
        events: List of ExecutionEvent instances for this session.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable ScientificExecutionReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "session_id": session.session_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"EREP_{digest[:16].upper()}"

    # Build event timeline
    timeline = [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "event_timestamp": e.event_timestamp,
            "previous_state": e.previous_state.value,
            "current_state": e.current_state.value,
            "scheduled_task_id": e.scheduled_task_id,
        }
        for e in events
    ]

    # Event type statistics
    event_type_counts: dict[str, int] = {}
    for e in events:
        event_type_counts[e.event_type] = event_type_counts.get(e.event_type, 0) + 1

    # Categorize tasks by final state (last event per task)
    task_final_states: dict[str, ExecutionState] = {}
    for e in events:
        task_final_states[e.scheduled_task_id] = e.current_state

    completed = [tid for tid, state in task_final_states.items() if state == ExecutionState.COMPLETED]
    failed = [tid for tid, state in task_final_states.items() if state == ExecutionState.FAILED]

    # Duration
    duration = ""
    if session.start_timestamp and session.end_timestamp:
        duration = f"{session.start_timestamp} -> {session.end_timestamp}"

    return ScientificExecutionReport(
        report_id=report_id,
        session_id=session.session_id,
        timestamp=ts,
        session_metadata={
            "session_id": session.session_id,
            "source_schedule_id": session.source_schedule_id,
            "semantic_version": session.semantic_version,
            "session_status": session.session_status.value,
            "total_tasks": len(session.executed_task_ids),
        },
        executed_tasks=list(session.executed_task_ids),
        execution_timeline=timeline,
        event_statistics={
            "total_events": len(events),
            "event_type_counts": event_type_counts,
        },
        execution_duration=duration,
        completed_tasks=completed,
        failed_tasks=failed,
        replay_verification="not_verified",
        audit_summary={"status": "clean", "event_count": len(events)},
    )
