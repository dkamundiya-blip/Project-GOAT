"""
Project GOAT v0.9 — Experiment Scheduling Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.experiments.core.canonical import compute_schedule_id
from goat.experiments.core.enums import ExperimentPriority
from goat.experiments.core.models import ExperimentSchedule, ScientificExperiment


class ExperimentSchedulingEngine:
    """Experiment Scheduling Engine for registering, queueing, ordering, and managing experiment schedule metadata.

    IMPORTANT: This engine MUST NOT execute any experiment logic or trading code.
    It purely maintains execution queue ordering and schedule metadata.
    """

    PRIORITY_WEIGHTS: dict[ExperimentPriority, int] = {
        ExperimentPriority.CRITICAL: 4,
        ExperimentPriority.HIGH: 3,
        ExperimentPriority.NORMAL: 2,
        ExperimentPriority.LOW: 1,
    }

    def __init__(self) -> None:
        self._schedules: dict[str, ExperimentSchedule] = {}
        self._experiment_schedule_map: dict[str, str] = {}

    def schedule_experiment(
        self,
        experiment: ScientificExperiment,
        scheduled_timestamp: str | None = None,
        priority: ExperimentPriority | None = None,
        scheduler_id: str = "GOAT_SCHEDULER",
        metadata: dict[str, Any] | None = None,
    ) -> ExperimentSchedule:
        """Schedule an experiment for queueing and execution ordering without executing it."""
        exp_id = experiment.experiment_id
        if exp_id in self._experiment_schedule_map:
            sch_id = self._experiment_schedule_map[exp_id]
            return self._schedules[sch_id]

        target_priority = priority or experiment.priority
        now_str = datetime.now(timezone.utc).isoformat()
        target_sch_time = scheduled_timestamp or now_str

        sch_id, canonical_hash = compute_schedule_id(
            experiment_id=exp_id,
            priority=target_priority.value,
            scheduled_timestamp=target_sch_time,
        )

        schedule = ExperimentSchedule(
            schedule_id=sch_id,
            experiment_id=exp_id,
            priority=target_priority,
            scheduled_timestamp=target_sch_time,
            queue_position=len(self._schedules) + 1,
            scheduler_id=scheduler_id.strip(),
            timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._schedules[sch_id] = schedule
        self._experiment_schedule_map[exp_id] = sch_id
        self._recalculate_queue_positions()

        return self._schedules[sch_id]

    def _recalculate_queue_positions(self) -> None:
        """Re-sort schedules by priority (descending) and timestamp (ascending), updating queue positions."""
        sorted_schedules = sorted(
            self._schedules.values(),
            key=lambda s: (-self.PRIORITY_WEIGHTS[s.priority], s.scheduled_timestamp),
        )

        updated_dict: dict[str, ExperimentSchedule] = {}
        for pos, s in enumerate(sorted_schedules, start=1):
            updated_schedule = ExperimentSchedule(
                schedule_id=s.schedule_id,
                experiment_id=s.experiment_id,
                priority=s.priority,
                scheduled_timestamp=s.scheduled_timestamp,
                queue_position=pos,
                scheduler_id=s.scheduler_id,
                timestamp=s.timestamp,
                metadata=s.metadata,
                canonical_hash=s.canonical_hash,
            )
            updated_dict[s.schedule_id] = updated_schedule

        self._schedules = updated_dict

    def get_schedule(self, schedule_id: str) -> ExperimentSchedule | None:
        """Get schedule by ID."""
        return self._schedules.get(schedule_id)

    def get_schedule_for_experiment(self, experiment_id: str) -> ExperimentSchedule | None:
        """Get schedule for experiment ID."""
        sch_id = self._experiment_schedule_map.get(experiment_id)
        if not sch_id:
            return None
        return self._schedules.get(sch_id)

    def list_queue(self) -> list[ExperimentSchedule]:
        """Return scheduled queue sorted by queue_position index."""
        return sorted(self._schedules.values(), key=lambda s: s.queue_position)
