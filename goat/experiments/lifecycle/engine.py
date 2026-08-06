"""
Project GOAT v0.9 — Scientific Experiment Lifecycle Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.experiments.core.canonical import compute_experiment_id, compute_lifecycle_id
from goat.experiments.core.enums import (
    ExperimentPriority,
    ExperimentStatus,
    ExperimentType,
)
from goat.experiments.core.models import ExperimentLifecycle, ScientificExperiment


class ScientificExperimentLifecycleEngine:
    """Scientific Experiment Lifecycle Engine for managing deterministic state transitions

    and maintaining strict audit trails across experiment lifecycles.
    """

    # Allowed state transition map
    VALID_TRANSITIONS: dict[ExperimentStatus, set[ExperimentStatus]] = {
        ExperimentStatus.PLANNED: {
            ExperimentStatus.APPROVED,
            ExperimentStatus.FAILED,
            ExperimentStatus.ARCHIVED,
        },
        ExperimentStatus.APPROVED: {
            ExperimentStatus.READY,
            ExperimentStatus.RUNNING,
            ExperimentStatus.FAILED,
            ExperimentStatus.ARCHIVED,
        },
        ExperimentStatus.READY: {
            ExperimentStatus.RUNNING,
            ExperimentStatus.FAILED,
            ExperimentStatus.ARCHIVED,
        },
        ExperimentStatus.RUNNING: {
            ExperimentStatus.PAUSED,
            ExperimentStatus.COMPLETED,
            ExperimentStatus.FAILED,
            ExperimentStatus.ARCHIVED,
        },
        ExperimentStatus.PAUSED: {
            ExperimentStatus.RUNNING,
            ExperimentStatus.FAILED,
            ExperimentStatus.ARCHIVED,
        },
        ExperimentStatus.COMPLETED: {
            ExperimentStatus.ARCHIVED,
        },
        ExperimentStatus.FAILED: {
            ExperimentStatus.ARCHIVED,
        },
        ExperimentStatus.ARCHIVED: set(),  # Terminal state
    }

    def __init__(self) -> None:
        self._experiments: dict[str, ScientificExperiment] = {}
        self._lifecycles: dict[str, list[ExperimentLifecycle]] = {}

    def create_experiment(
        self,
        hypothesis_id: str,
        title: str,
        description: str = "",
        experiment_type: ExperimentType = ExperimentType.SIMULATION,
        priority: ExperimentPriority = ExperimentPriority.NORMAL,
        author: str = "QUANT_RESEARCHER",
        evidence_ids: list[str] | None = None,
        manifest_id: str = "",
        timestamp: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[ScientificExperiment, ExperimentLifecycle]:
        """Create a new scientific experiment container in PLANNED status."""
        if not hypothesis_id or not hypothesis_id.startswith("HYP_"):
            raise ValueError(f"Hypothesis ID '{hypothesis_id}' must start with 'HYP_'.")
        if not title or len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 non-whitespace characters.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        exp_id, canonical_hash = compute_experiment_id(
            hypothesis_id=hypothesis_id,
            title=title,
            experiment_type=experiment_type.value,
            author=author,
        )

        experiment = ScientificExperiment(
            experiment_id=exp_id,
            hypothesis_id=hypothesis_id.strip(),
            title=title.strip(),
            description=description.strip(),
            experiment_type=experiment_type,
            status=ExperimentStatus.PLANNED,
            priority=priority,
            author=author.strip(),
            evidence_ids=evidence_ids or [],
            manifest_id=manifest_id.strip(),
            created_timestamp=now_str,
            updated_timestamp=now_str,
            tags=tags or [],
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        lfc_id, lfc_hash = compute_lifecycle_id(
            experiment_id=exp_id,
            from_status=ExperimentStatus.PLANNED.value,
            to_status=ExperimentStatus.PLANNED.value,
            timestamp=now_str,
        )

        initial_lfc = ExperimentLifecycle(
            lifecycle_id=lfc_id,
            experiment_id=exp_id,
            from_status=ExperimentStatus.PLANNED,
            to_status=ExperimentStatus.PLANNED,
            actor=author.strip(),
            reason="Initial experiment creation.",
            timestamp=now_str,
            canonical_hash=lfc_hash,
        )

        self._experiments[exp_id] = experiment
        self._lifecycles[exp_id] = [initial_lfc]

        return experiment, initial_lfc

    def transition_status(
        self,
        experiment_id: str,
        target_status: ExperimentStatus,
        actor: str,
        reason: str = "",
        timestamp: str | None = None,
    ) -> tuple[ScientificExperiment, ExperimentLifecycle]:
        """Transition experiment to a target status, enforcing valid state transition graph."""
        if experiment_id not in self._experiments:
            raise KeyError(f"Experiment ID '{experiment_id}' not found.")

        current_exp = self._experiments[experiment_id]
        if target_status not in self.VALID_TRANSITIONS.get(current_exp.status, set()):
            raise ValueError(
                f"Illegal state transition from '{current_exp.status.value}' to '{target_status.value}' for experiment '{experiment_id}'."
            )

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        lfc_id, lfc_hash = compute_lifecycle_id(
            experiment_id=experiment_id,
            from_status=current_exp.status.value,
            to_status=target_status.value,
            timestamp=now_str,
        )

        lifecycle = ExperimentLifecycle(
            lifecycle_id=lfc_id,
            experiment_id=experiment_id,
            from_status=current_exp.status,
            to_status=target_status,
            actor=actor.strip(),
            reason=reason.strip(),
            timestamp=now_str,
            canonical_hash=lfc_hash,
        )

        updated_exp = ScientificExperiment(
            experiment_id=current_exp.experiment_id,
            hypothesis_id=current_exp.hypothesis_id,
            title=current_exp.title,
            description=current_exp.description,
            experiment_type=current_exp.experiment_type,
            status=target_status,
            priority=current_exp.priority,
            author=current_exp.author,
            evidence_ids=current_exp.evidence_ids,
            manifest_id=current_exp.manifest_id,
            created_timestamp=current_exp.created_timestamp,
            updated_timestamp=now_str,
            tags=current_exp.tags,
            metadata=current_exp.metadata,
            canonical_hash=current_exp.canonical_hash,
        )

        self._experiments[experiment_id] = updated_exp
        self._lifecycles[experiment_id].append(lifecycle)

        return updated_exp, lifecycle

    def approve_experiment(self, experiment_id: str, actor: str, reason: str = "") -> tuple[ScientificExperiment, ExperimentLifecycle]:
        return self.transition_status(experiment_id, ExperimentStatus.APPROVED, actor, reason)

    def start_experiment(self, experiment_id: str, actor: str, reason: str = "") -> tuple[ScientificExperiment, ExperimentLifecycle]:
        return self.transition_status(experiment_id, ExperimentStatus.RUNNING, actor, reason)

    def pause_experiment(self, experiment_id: str, actor: str, reason: str = "") -> tuple[ScientificExperiment, ExperimentLifecycle]:
        return self.transition_status(experiment_id, ExperimentStatus.PAUSED, actor, reason)

    def resume_experiment(self, experiment_id: str, actor: str, reason: str = "") -> tuple[ScientificExperiment, ExperimentLifecycle]:
        return self.transition_status(experiment_id, ExperimentStatus.RUNNING, actor, reason)

    def complete_experiment(self, experiment_id: str, actor: str, reason: str = "") -> tuple[ScientificExperiment, ExperimentLifecycle]:
        return self.transition_status(experiment_id, ExperimentStatus.COMPLETED, actor, reason)

    def fail_experiment(self, experiment_id: str, actor: str, reason: str = "") -> tuple[ScientificExperiment, ExperimentLifecycle]:
        return self.transition_status(experiment_id, ExperimentStatus.FAILED, actor, reason)

    def archive_experiment(self, experiment_id: str, actor: str, reason: str = "") -> tuple[ScientificExperiment, ExperimentLifecycle]:
        return self.transition_status(experiment_id, ExperimentStatus.ARCHIVED, actor, reason)

    def get_experiment(self, experiment_id: str) -> ScientificExperiment | None:
        return self._experiments.get(experiment_id)

    def get_lifecycle_history(self, experiment_id: str) -> list[ExperimentLifecycle]:
        return self._lifecycles.get(experiment_id, [])

    def list_all_experiments(self) -> list[ScientificExperiment]:
        return sorted(self._experiments.values(), key=lambda e: e.created_timestamp)
