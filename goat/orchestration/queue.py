"""
Project GOAT v0.5 — Experiment Queue Management

Handles in-memory task queue semantics, canonical task ordering,
and status state transition guards with ZERO File I/O.
"""

from __future__ import annotations

from typing import Any

import structlog

from goat.orchestration.campaign import (
    ExperimentStatus,
    QueueSnapshot,
)
from goat.research.hypothesis.definition import HypothesisDefinition

_log = structlog.get_logger(__name__)

# Valid state transition matrix for ExperimentStatus
VALID_EXPERIMENT_TRANSITIONS: dict[ExperimentStatus, set[ExperimentStatus]] = {
    ExperimentStatus.PENDING: {
        ExperimentStatus.RUNNING,
        ExperimentStatus.SKIPPED,
        ExperimentStatus.CANCELLED,
    },
    ExperimentStatus.RUNNING: {
        ExperimentStatus.COMPLETED,
        ExperimentStatus.FAILED,
        ExperimentStatus.CANCELLED,
    },
    ExperimentStatus.COMPLETED: set(),  # Terminal
    ExperimentStatus.FAILED: {ExperimentStatus.PENDING},  # Retryable transition
    ExperimentStatus.SKIPPED: set(),    # Terminal
    ExperimentStatus.CANCELLED: set(),  # Terminal
}


class ExperimentTask:
    """Represents an individual experiment execution task."""

    def __init__(
        self,
        experiment_id: str,
        hypothesis: HypothesisDefinition,
        symbol: str,
        timeframe: str,
        priority: int = 0,
        status: ExperimentStatus = ExperimentStatus.PENDING,
        retry_count: int = 0,
    ) -> None:
        self.experiment_id = experiment_id
        self.hypothesis = hypothesis
        self.symbol = symbol
        self.timeframe = timeframe
        self.priority = priority
        self.status = status
        self.retry_count = retry_count

    @property
    def canonical_sort_key(self) -> tuple[int, str, str, str]:
        """Canonical sort key: (priority, symbol, timeframe, experiment_id)."""
        return (self.priority, self.symbol, self.timeframe, self.experiment_id)

    def to_dict(self) -> dict[str, Any]:
        """Return dict representation."""
        return {
            "experiment_id": self.experiment_id,
            "hypothesis_id": self.hypothesis.hypothesis_id,
            "hypothesis_version": self.hypothesis.version,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "priority": self.priority,
            "status": self.status.value,
            "retry_count": self.retry_count,
        }


class ExperimentQueue:
    """Deterministic in-memory task queue manager with ZERO File I/O."""

    def __init__(
        self,
        campaign_id: str,
        configuration_hash: str,
        tasks: list[ExperimentTask] | None = None,
    ) -> None:
        self.campaign_id = campaign_id
        self.configuration_hash = configuration_hash
        self._tasks: dict[str, ExperimentTask] = {}
        self._results: dict[str, dict[str, Any]] = {}

        if tasks:
            for t in tasks:
                self.add_task(t)

    def add_task(self, task: ExperimentTask) -> None:
        """Add an experiment task to the queue."""
        self._tasks[task.experiment_id] = task

    def get_task(self, experiment_id: str) -> ExperimentTask | None:
        """Retrieve a task by experiment ID."""
        return self._tasks.get(experiment_id)

    def get_all_tasks(self) -> list[ExperimentTask]:
        """Return all tasks sorted by canonical_sort_key."""
        return sorted(self._tasks.values(), key=lambda t: t.canonical_sort_key)

    def get_next_task(self) -> ExperimentTask | None:
        """Get the next PENDING task in canonical order."""
        pending = [t for t in self._tasks.values() if t.status == ExperimentStatus.PENDING]
        if not pending:
            return None
        pending.sort(key=lambda t: t.canonical_sort_key)
        return pending[0]

    def update_status(
        self,
        experiment_id: str,
        new_status: ExperimentStatus,
        result: dict[str, Any] | None = None,
    ) -> None:
        """Update a task's status while validating transition guards."""
        task = self._tasks.get(experiment_id)
        if not task:
            raise KeyError(f"Task '{experiment_id}' not found in queue.")

        current_status = task.status
        valid_targets = VALID_EXPERIMENT_TRANSITIONS.get(current_status, set())

        if new_status not in valid_targets:
            raise ValueError(
                f"Invalid status transition for task '{experiment_id}': "
                f"cannot jump from {current_status.value} to {new_status.value}."
            )

        task.status = new_status
        if result:
            self._results[experiment_id] = result

        _log.debug(
            "experiment_status_updated",
            component="ExperimentQueue",
            campaign_id=self.campaign_id,
            experiment_id=experiment_id,
            old_status=current_status.value,
            new_status=new_status.value,
        )

    def is_complete(self) -> bool:
        """Return True if all tasks are in terminal states."""
        for t in self._tasks.values():
            if t.status in (ExperimentStatus.PENDING, ExperimentStatus.RUNNING):
                return False
        return True

    def take_snapshot(self, last_event_sequence: int = 0) -> QueueSnapshot:
        """Export an immutable, frozen QueueSnapshot representing current state."""
        completed_ids = tuple(
            t.experiment_id for t in self._tasks.values() if t.status == ExperimentStatus.COMPLETED
        )
        failed_ids = tuple(
            t.experiment_id for t in self._tasks.values() if t.status == ExperimentStatus.FAILED
        )
        in_progress_ids = tuple(
            t.experiment_id for t in self._tasks.values() if t.status == ExperimentStatus.RUNNING
        )
        pending_ids = tuple(
            t.experiment_id for t in self._tasks.values() if t.status == ExperimentStatus.PENDING
        )

        return QueueSnapshot(
            campaign_id=self.campaign_id,
            configuration_hash=self.configuration_hash,
            completed_task_ids=completed_ids,
            failed_task_ids=failed_ids,
            in_progress_task_ids=in_progress_ids,
            pending_task_ids=pending_ids,
            task_results=dict(self._results),
            last_event_sequence=last_event_sequence,
        )

    @classmethod
    def from_snapshot(
        cls,
        snapshot: QueueSnapshot,
        tasks: list[ExperimentTask],
    ) -> ExperimentQueue:
        """Class factory constructing a clean new ExperimentQueue instance from snapshot."""
        queue = cls(
            campaign_id=snapshot.campaign_id,
            configuration_hash=snapshot.configuration_hash,
            tasks=tasks,
        )

        # Restore states from snapshot
        for exp_id in snapshot.completed_task_ids:
            if exp_id in queue._tasks:
                queue._tasks[exp_id].status = ExperimentStatus.COMPLETED
        for exp_id in snapshot.failed_task_ids:
            if exp_id in queue._tasks:
                queue._tasks[exp_id].status = ExperimentStatus.FAILED
        # Interrupted RUNNING tasks reset to PENDING
        for exp_id in snapshot.in_progress_task_ids:
            if exp_id in queue._tasks:
                queue._tasks[exp_id].status = ExperimentStatus.PENDING

        queue._results = dict(snapshot.task_results)
        return queue
