"""
Project GOAT v0.7 — Scheduled Task Model

Defines the immutable ScheduledTask model (STK_<HEX16>) representing scheduled plan task execution steps.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.scheduling.enums import ScheduleExecutionState


def compute_scheduled_task_id(
    schedule_id: str,
    source_plan_task_id: str,
    position: int,
) -> tuple[str, str]:
    """Compute deterministic Scheduled Task ID (STK_<HEX16>) and full SHA-256 task schedule hash.

    Args:
        schedule_id: Parent Schedule ID (SCH_<HEX16>).
        source_plan_task_id: Source Plan Task ID (PTK_<HEX16>).
        position: 1-indexed execution position integer.

    Returns:
        Tuple of (task_schedule_id, task_schedule_hash).
    """
    payload = {
        "position": int(position),
        "schedule_id": str(schedule_id).strip(),
        "source_plan_task_id": str(source_plan_task_id).strip(),
    }
    digest = compute_canonical_sha256(payload)
    task_schedule_id = f"STK_{digest[:16].upper()}"
    return task_schedule_id, digest


class ScheduledTask(BaseModel):
    """Immutable scheduled task artifact representing an executable task scheduled within a ResearchSchedule."""

    task_schedule_id: str = Field(
        ...,
        description="Unique Task Schedule ID formatted as STK_<HEX16>",
        pattern=r"^STK_[A-Fa-f0-9]{16}$",
    )
    parent_schedule_id: str = Field(..., description="Parent Schedule ID (SCH_<HEX16>)")
    source_plan_task_id: str = Field(..., description="Source Plan Task ID (PTK_<HEX16>)")
    execution_position: int = Field(default=1, ge=1, description="1-indexed execution queue position")
    execution_state: ScheduleExecutionState = Field(default=ScheduleExecutionState.PENDING, description="Scheduled task execution state")
    dependency_satisfaction: bool = Field(default=False, description="True if all task dependencies are satisfied")
    planned_start_sequence: int = Field(default=1, ge=1, description="Planned start sequence tick")
    planned_finish_sequence: int = Field(default=1, ge=1, description="Planned finish sequence tick")
    task_schedule_hash: str = Field(..., description="Full 64-character SHA-256 canonical task schedule hash digest")

    class Config:
        frozen = True
        extra = "forbid"
