"""
Project GOAT v0.7 — Study Audit Engine

Defines the immutable StudyAuditEvent model representing append-only audit log events for scientific studies.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StudyAuditEvent(BaseModel):
    """Immutable audit trail event logged during study lifecycle transitions."""

    event_id: str = Field(..., description="Unique audit event ID (AUD_<HEX16>)")
    study_id: str = Field(..., description="Parent Study ID (STD_<HEX16>)")
    event_type: str = Field(..., description="Event type ('CREATE', 'SCHEDULE', 'EXECUTE', 'PAUSE', 'RESUME', 'COMPLETE', 'REPLAY', 'ARCHIVE')")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    previous_state: str = Field(default="", description="Previous status string")
    new_state: str = Field(default="", description="New status string")
    operator: str = Field(default="system", description="Operator attribution identifier")
    failure_reason: str = Field(default="", description="Failure reason string if applicable")
    notes: str = Field(default="", description="Audit commentary notes")
    execution_hash: str = Field(default="", description="SHA-256 canonical execution hash digest")

    class Config:
        frozen = True
        extra = "forbid"
