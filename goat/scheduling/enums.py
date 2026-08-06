"""
Project GOAT v0.7 — Scientific Scheduling Enums

Defines ScheduleExecutionState enum representing execution states of scheduled research tasks.
"""

from __future__ import annotations

from enum import Enum


class ScheduleExecutionState(str, Enum):
    """Execution state of a scheduled task or schedule."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
