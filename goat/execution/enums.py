"""
Project GOAT v0.7 — Scientific Execution Enums

Defines ExecutionState enum representing execution lifecycle states
for scientific research execution sessions and tasks.
"""

from __future__ import annotations

from enum import Enum


class ExecutionState(str, Enum):
    """Execution lifecycle state of a scientific execution session or task."""

    CREATED = "created"
    QUEUED = "queued"
    READY = "ready"
    STARTED = "started"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
