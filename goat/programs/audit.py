"""
Project GOAT v0.7 — Program Audit Engine

Defines the immutable ProgramAuditEvent model representing append-only audit trail logs for scientific research programs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProgramAuditEvent(BaseModel):
    """Immutable audit trail event logged during program lifecycle transitions."""

    event_id: str = Field(..., description="Unique audit event ID (AUD_<HEX16>)")
    program_id: str = Field(..., description="Parent Program ID (PRG_<HEX16>)")
    event_type: str = Field(..., description="Event type ('CREATE', 'SCHEDULE', 'EXECUTE', 'MILESTONE', 'PAUSE', 'RESUME', 'COMPLETE', 'REPLAY', 'ARCHIVE')")
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
