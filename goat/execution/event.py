"""
Project GOAT v0.7 — Execution Event Model

Defines the immutable ExecutionEvent model (EVT_<HEX16>) representing append-only
execution lifecycle events within scientific execution sessions.

Events are append-only. Execution history must never be rewritten.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.execution.enums import ExecutionState
from goat.research.edge.canonical import compute_canonical_sha256


def compute_event_id(
    session_id: str,
    scheduled_task_id: str,
    event_type: str,
    event_timestamp: str,
) -> tuple[str, str]:
    """Compute deterministic Execution Event ID (EVT_<HEX16>) and full SHA-256 event hash.

    Args:
        session_id: Parent Session ID (SES_<HEX16>).
        scheduled_task_id: Scheduled Task ID (STK_<HEX16>).
        event_type: Event type string.
        event_timestamp: ISO 8601 UTC event timestamp.

    Returns:
        Tuple of (event_id, event_hash).
    """
    payload = {
        "event_timestamp": str(event_timestamp).strip(),
        "event_type": str(event_type).strip(),
        "scheduled_task_id": str(scheduled_task_id).strip(),
        "session_id": str(session_id).strip(),
    }
    digest = compute_canonical_sha256(payload)
    event_id = f"EVT_{digest[:16].upper()}"
    return event_id, digest


class ExecutionEvent(BaseModel):
    """Immutable append-only execution event recording a state transition within an execution session."""

    event_id: str = Field(
        ...,
        description="Unique Event ID formatted as EVT_<HEX16>",
        pattern=r"^EVT_[A-Fa-f0-9]{16}$",
    )
    parent_session_id: str = Field(..., description="Parent Session ID (SES_<HEX16>)")
    scheduled_task_id: str = Field(..., description="Scheduled Task ID (STK_<HEX16>)")
    event_type: str = Field(..., description="Event type classification")
    event_timestamp: str = Field(..., description="ISO 8601 UTC event timestamp")
    previous_state: ExecutionState = Field(..., description="State before this event")
    current_state: ExecutionState = Field(..., description="State after this event")
    event_hash: str = Field(..., description="Full 64-character SHA-256 canonical event hash digest")
    event_metadata: dict[str, Any] = Field(default_factory=dict, description="Event-specific metadata")

    class Config:
        frozen = True
        extra = "forbid"
