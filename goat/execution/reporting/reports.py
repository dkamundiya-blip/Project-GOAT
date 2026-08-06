"""
Project GOAT v0.8 — Production Execution & Scientific Execution Reporting

Defines reporting models for Execution Engine intents, decisions, lifecycles,
failures, audits, consolidated executive reporting, and legacy scientific execution reports.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.execution.core.models import (
    ExecutionAudit,
    ExecutionDecision,
    ExecutionFailure,
    ExecutionIntent,
    ExecutionLifecycle,
    ExecutionSummary,
)
from goat.execution.enums import ExecutionState as ScientificExecutionState
from goat.execution.event import ExecutionEvent
from goat.execution.model import ScientificExecutionSession
from goat.integration.core.canonical import serialize_canonical_json
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
    execution_duration: str = Field(default="", description="Total execution duration")
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
    """Generate deterministic ScientificExecutionReport."""
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "session_id": session.session_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"EREP_{digest[:16].upper()}"

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

    event_type_counts: dict[str, int] = {}
    for e in events:
        event_type_counts[e.event_type] = event_type_counts.get(e.event_type, 0) + 1

    task_final_states: dict[str, ScientificExecutionState] = {}
    for e in events:
        task_final_states[e.scheduled_task_id] = e.current_state

    completed = [tid for tid, state in task_final_states.items() if state == ScientificExecutionState.COMPLETED]
    failed = [tid for tid, state in task_final_states.items() if state == ScientificExecutionState.FAILED]

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


class ExecutionIntentReport(BaseModel):
    """Report model for ExecutionIntent."""

    report_id: str = Field(..., description="Report ID formatted as EXM_<HEX16>")
    intent: ExecutionIntent = Field(..., description="ExecutionIntent model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return f"# Execution Intent Report\n\n- **Intent ID**: `{self.intent.intent_id}`\n- **Signal ID**: `{self.intent.signal_id}`\n- **Broker ID**: `{self.intent.broker_id}`\n- **Symbol**: `{self.intent.symbol}`\n- **Side**: `{self.intent.side.value}`\n- **Quantity**: `{self.intent.quantity}`\n- **Status**: `{self.intent.status.value}`\n"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class ExecutionDecisionReport(BaseModel):
    """Report model for ExecutionDecision."""

    report_id: str = Field(..., description="Report ID formatted as EXM_<HEX16>")
    decision: ExecutionDecision = Field(..., description="ExecutionDecision model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return f"# Execution Decision Report\n\n- **Decision ID**: `{self.decision.decision_id}`\n- **Intent ID**: `{self.decision.intent_id}`\n- **Approved**: `{self.decision.approved}`\n- **Rationale**: `{self.decision.explanation}`\n"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class ExecutionLifecycleReport(BaseModel):
    """Report model for ExecutionLifecycle."""

    report_id: str = Field(..., description="Report ID formatted as EXM_<HEX16>")
    lifecycle_history: list[ExecutionLifecycle] = Field(..., description="List of lifecycle entries")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        lines = [f"# Execution Lifecycle Report ({len(self.lifecycle_history)} Entries)\n"]
        for entry in self.lifecycle_history:
            prev = entry.previous_state.value if entry.previous_state else "NONE"
            lines.append(f"- **State**: `{prev} -> {entry.state.value}` | `{entry.explanation}`")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class ExecutionFailureReport(BaseModel):
    """Report model for ExecutionFailure."""

    report_id: str = Field(..., description="Report ID formatted as EXM_<HEX16>")
    failure: ExecutionFailure = Field(..., description="ExecutionFailure model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return f"# Execution Failure Report\n\n- **Failure ID**: `{self.failure.failure_id}`\n- **Intent ID**: `{self.failure.intent_id}`\n- **Error Code**: `{self.failure.error_code}`\n- **Category**: `{self.failure.category.value}`\n- **Reason**: `{self.failure.reason}`\n"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class ExecutionAuditReport(BaseModel):
    """Report model for ExecutionAudit."""

    report_id: str = Field(..., description="Report ID formatted as EXM_<HEX16>")
    audits: list[ExecutionAudit] = Field(..., description="List of audit log entries")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        lines = [f"# Execution Audit Trail Report ({len(self.audits)} Events)\n"]
        for a in self.audits:
            lines.append(f"- **Event**: `{a.event_type.value}` | Intent: `{a.intent_id}` | `{a.details}`")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class ExecutionExecutiveReport(BaseModel):
    """Consolidated executive report for Production Execution Engine."""

    report_id: str = Field(..., description="Report ID formatted as EXM_<HEX16>")
    summary: ExecutionSummary = Field(..., description="Execution summary metrics model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return (
            f"# Project GOAT v0.8 — Step 7.4 Production Execution Engine Executive Report\n\n"
            f"- **Report ID**: `{self.report_id}`\n"
            f"- **Total Intents**: `{self.summary.total_intents}`\n"
            f"- **Dispatched Requests**: `{self.summary.dispatched_count}`\n"
            f"- **Filled Executions**: `{self.summary.filled_count}`\n"
            f"- **Rejected Executions**: `{self.summary.rejected_count}`\n"
            f"- **Execution Failures**: `{self.summary.failed_count}`\n"
            f"- **Timestamp**: `{self.timestamp}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())
