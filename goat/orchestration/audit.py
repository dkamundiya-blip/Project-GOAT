"""
Project GOAT v0.7 — Pipeline Audit Engine

Defines the immutable PipelineAuditEvent model representing append-only audit events logged during pipeline execution.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PipelineAuditEvent(BaseModel):
    """Immutable audit trail event logged during research pipeline execution."""

    event_id: str = Field(..., description="Unique audit event ID (AUD_<HEX16>)")
    pipeline_id: str = Field(..., description="Parent Research Pipeline ID (PIPE_<HEX16>)")
    stage_id: str = Field(default="", description="Target Stage ID (STAGE_<HEX16>) if applicable")
    event_type: str = Field(..., description="Event type ('STAGE_ENTER', 'STAGE_EXIT', 'STATE_CHANGE', 'FAILURE', 'RECOVERY')")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    previous_state: str = Field(default="", description="Previous pipeline or stage state")
    new_state: str = Field(default="", description="New pipeline or stage state")
    duration_seconds: float = Field(default=0.0, ge=0.0, description="Stage execution duration in seconds")
    operator: str = Field(default="system", description="Operator attribution identifier")
    failure_reason: str = Field(default="", description="Failure reason string if applicable")
    notes: str = Field(default="", description="Audit commentary notes")
    execution_hash: str = Field(default="", description="SHA-256 canonical execution hash digest")

    class Config:
        frozen = True
        extra = "forbid"
