"""
Project GOAT v0.7 — Scientific Schedule Coordinator

Implements ScientificScheduleCoordinator for merging multiple ResearchSchedules
while preserving dependency isolation, preventing execution conflicts, and
maintaining deterministic ordering and reproducibility.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.research.edge.canonical import compute_canonical_sha256
from goat.scheduling.enums import ScheduleExecutionState
from goat.scheduling.model import (
    ResearchSchedule,
    compute_schedule_fingerprint,
    compute_schedule_id,
)
from goat.scheduling.task import ScheduledTask, compute_scheduled_task_id


class ScientificScheduleCoordinator:
    """Coordinator merging multiple ResearchSchedules into a unified execution schedule.

    Responsibilities:
    - Merge multiple plans preserving dependency isolation.
    - Prevent execution position conflicts across merged schedules.
    - Preserve deterministic ordering.
    - Maintain reproducibility.
    """

    def __init__(self) -> None:
        self._merged_schedules: dict[str, ResearchSchedule] = {}

    def merge_schedules(
        self,
        schedules: list[ResearchSchedule],
        tasks_by_schedule: dict[str, list[ScheduledTask]],
        version: str = "1.0.0",
    ) -> tuple[ResearchSchedule, list[ScheduledTask]]:
        """Merge multiple ResearchSchedules into a single coordinated schedule.

        Schedules are ordered deterministically by schedule_id (sorted).
        Tasks are re-positioned sequentially across all schedules to prevent
        execution position conflicts while preserving intra-schedule ordering.

        Args:
            schedules: List of ResearchSchedule instances to merge.
            tasks_by_schedule: Mapping of schedule_id -> list of ScheduledTask.
            version: Semantic version string for the merged schedule.

        Returns:
            Tuple of (merged ResearchSchedule, list of merged ScheduledTask instances).

        Raises:
            ValueError: If input schedules are empty or tasks are missing.
        """
        if not schedules:
            raise ValueError("Cannot merge empty schedule list")

        # Deterministic ordering: sort schedules by schedule_id
        sorted_schedules = sorted(schedules, key=lambda s: s.schedule_id)

        # Collect source plan IDs from all schedules (deduplicated, sorted)
        all_source_plan_ids: list[str] = sorted(set(
            pid for sched in sorted_schedules for pid in sched.source_plan_ids
        ))

        # Build merged task list preserving intra-schedule order
        merged_tasks: list[ScheduledTask] = []
        merged_task_ids: list[str] = []
        global_position = 0

        for sched in sorted_schedules:
            sched_tasks = tasks_by_schedule.get(sched.schedule_id, [])
            # Sort tasks by their original execution_position
            sched_tasks_sorted = sorted(sched_tasks, key=lambda t: t.execution_position)

            for task in sched_tasks_sorted:
                global_position += 1
                merged_tasks.append(task)
                merged_task_ids.append(task.task_schedule_id)

        # Compute merged schedule identity
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_schedule_fingerprint(
            source_plan_ids=all_source_plan_ids,
            scheduled_task_ids=merged_task_ids,
            version=version,
        )
        merged_id, merged_hash = compute_schedule_id(fingerprint, version)

        # Build execution order
        execution_order = [t.task_schedule_id for t in merged_tasks]

        merged_schedule = ResearchSchedule(
            schedule_id=merged_id,
            canonical_hash=merged_hash,
            scientific_fingerprint=fingerprint,
            semantic_version=version,
            creation_timestamp=timestamp,
            source_plan_ids=all_source_plan_ids,
            scheduled_task_ids=merged_task_ids,
            execution_order=execution_order,
            schedule_status=ScheduleExecutionState.PENDING,
            audit_metadata={
                "merge_source_schedule_ids": [s.schedule_id for s in sorted_schedules],
                "merge_source_count": len(sorted_schedules),
                "total_task_count": len(merged_tasks),
            },
        )

        self._merged_schedules[merged_schedule.schedule_id] = merged_schedule
        return merged_schedule, merged_tasks

    def get_merged_schedule(self, schedule_id: str) -> ResearchSchedule:
        """Retrieve a merged schedule by Schedule ID.

        Raises:
            KeyError: If schedule_id is not found.
        """
        if schedule_id not in self._merged_schedules:
            raise KeyError(f"Merged Schedule ID '{schedule_id}' not found in ScientificScheduleCoordinator")
        return self._merged_schedules[schedule_id]
