"""
Project GOAT v0.9 — Master Scientific Experiment Engine Facade
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.experiments.core.canonical import compute_summary_id
from goat.experiments.core.enums import (
    ExperimentPriority,
    ExperimentStatus,
    ExperimentType,
)
from goat.experiments.core.models import (
    ExperimentLifecycle,
    ExperimentManifest,
    ExperimentReplay,
    ExperimentSchedule,
    ExperimentSummary,
    ScientificExperiment,
)
from goat.experiments.lifecycle.engine import ScientificExperimentLifecycleEngine
from goat.experiments.manifests.engine import ExperimentManifestEngine
from goat.experiments.persistence.sqlite import ExperimentPersistenceContext
from goat.experiments.replay.engine import ExperimentReplayEngine
from goat.experiments.reporting.reports import (
    generate_executive_summary,
    generate_experiment_report,
    generate_json_report,
    generate_lifecycle_report,
    generate_manifest_report,
    generate_replay_report,
)
from goat.experiments.scheduling.engine import ExperimentSchedulingEngine


class ScientificExperimentEngine:
    """Master Facade Engine orchestrating experiment creation, lifecycle transitions, scheduling,

    manifest generation, replay verification, reporting, and optional SQLite persistence.
    """

    def __init__(
        self,
        persistence_context: ExperimentPersistenceContext | None = None,
        lifecycle_engine: ScientificExperimentLifecycleEngine | None = None,
        scheduling_engine: ExperimentSchedulingEngine | None = None,
        manifest_engine: ExperimentManifestEngine | None = None,
        replay_engine: ExperimentReplayEngine | None = None,
    ) -> None:
        self._lifecycle_engine = lifecycle_engine or ScientificExperimentLifecycleEngine()
        self._scheduling_engine = scheduling_engine or ExperimentSchedulingEngine()
        self._manifest_engine = manifest_engine or ExperimentManifestEngine()
        self._replay_engine = replay_engine or ExperimentReplayEngine()
        self._persistence = persistence_context

        # Sync existing database entities if persistence context provided
        if self._persistence:
            for exp in self._persistence.experiments.list_all():
                self._lifecycle_engine._experiments[exp.experiment_id] = exp
            for lfc in self._persistence.lifecycles.list_all():
                self._lifecycle_engine._lifecycles.setdefault(lfc.experiment_id, []).append(lfc)
            for sch in self._persistence.schedules.list_all():
                self._scheduling_engine._schedules[sch.schedule_id] = sch
                self._scheduling_engine._experiment_schedule_map[sch.experiment_id] = sch.schedule_id
            for man in self._persistence.manifests.list_all():
                self._manifest_engine._manifests[man.manifest_id] = man
                self._manifest_engine._experiment_manifest_map[man.experiment_id] = man.manifest_id
            for rpl in self._persistence.replays.list_all():
                self._replay_engine._replays[rpl.replay_id] = rpl
                self._replay_engine._experiment_replay_map.setdefault(rpl.experiment_id, []).append(rpl.replay_id)

    @property
    def lifecycle_engine(self) -> ScientificExperimentLifecycleEngine:
        return self._lifecycle_engine

    @property
    def scheduling_engine(self) -> ExperimentSchedulingEngine:
        return self._scheduling_engine

    @property
    def manifest_engine(self) -> ExperimentManifestEngine:
        return self._manifest_engine

    @property
    def replay_engine(self) -> ExperimentReplayEngine:
        return self._replay_engine

    @property
    def persistence(self) -> ExperimentPersistenceContext | None:
        return self._persistence

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
        """Create and persist a new scientific experiment container."""
        exp, lfc = self._lifecycle_engine.create_experiment(
            hypothesis_id=hypothesis_id,
            title=title,
            description=description,
            experiment_type=experiment_type,
            priority=priority,
            author=author,
            evidence_ids=evidence_ids,
            manifest_id=manifest_id,
            timestamp=timestamp,
            tags=tags,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.experiments.save(exp)
            self._persistence.lifecycles.save(lfc)

        return exp, lfc

    def transition_status(
        self,
        experiment_id: str,
        target_status: ExperimentStatus,
        actor: str,
        reason: str = "",
        timestamp: str | None = None,
    ) -> tuple[ScientificExperiment, ExperimentLifecycle]:
        """Transition experiment lifecycle state."""
        exp, lfc = self._lifecycle_engine.transition_status(
            experiment_id=experiment_id,
            target_status=target_status,
            actor=actor,
            reason=reason,
            timestamp=timestamp,
        )

        if self._persistence:
            self._persistence.experiments.save(exp)
            self._persistence.lifecycles.save(lfc)

        return exp, lfc

    def generate_manifest(
        self,
        experiment: ScientificExperiment,
        dataset_fingerprint: str = "",
        configuration_params: dict[str, Any] | None = None,
        software_version: str = "1.0.0",
        author: str = "QUANT_RESEARCHER",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExperimentManifest:
        """Generate and persist an ExperimentManifest."""
        manifest = self._manifest_engine.generate_manifest(
            experiment=experiment,
            dataset_fingerprint=dataset_fingerprint,
            configuration_params=configuration_params,
            software_version=software_version,
            author=author,
            timestamp=timestamp,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.manifests.save(manifest)

        return manifest

    def schedule_experiment(
        self,
        experiment: ScientificExperiment,
        scheduled_timestamp: str | None = None,
        priority: ExperimentPriority | None = None,
        scheduler_id: str = "GOAT_SCHEDULER",
        metadata: dict[str, Any] | None = None,
    ) -> ExperimentSchedule:
        """Schedule an experiment in the execution queue."""
        schedule = self._scheduling_engine.schedule_experiment(
            experiment=experiment,
            scheduled_timestamp=scheduled_timestamp,
            priority=priority,
            scheduler_id=scheduler_id,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.schedules.save(schedule)

        return schedule

    def create_replay_spec(
        self,
        experiment: ScientificExperiment,
        manifest: ExperimentManifest,
        dataset_hash: str,
        random_seed: int = 42,
        expected_output_hash: str = "",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExperimentReplay:
        """Create and persist a replay specification."""
        replay = self._replay_engine.create_replay_spec(
            experiment=experiment,
            manifest=manifest,
            dataset_hash=dataset_hash,
            random_seed=random_seed,
            expected_output_hash=expected_output_hash,
            timestamp=timestamp,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.replays.save(replay)

        return replay

    def generate_summary(self, timestamp: str | None = None) -> ExperimentSummary:
        """Generate an ExperimentSummary snapshot of subsystem metrics."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        total_exp = len(self._lifecycle_engine._experiments)

        st_counts: dict[str, int] = {s.value: 0 for s in ExperimentStatus}
        tp_counts: dict[str, int] = {t.value: 0 for t in ExperimentType}
        pr_counts: dict[str, int] = {p.value: 0 for p in ExperimentPriority}

        for exp in self._lifecycle_engine._experiments.values():
            st_counts[exp.status.value] += 1
            tp_counts[exp.experiment_type.value] += 1
            pr_counts[exp.priority.value] += 1

        sum_id, canonical_hash = compute_summary_id(
            total_experiments=total_exp,
            timestamp=now_str,
        )

        summary = ExperimentSummary(
            summary_id=sum_id,
            total_experiments=total_exp,
            status_counts=st_counts,
            type_counts=tp_counts,
            priority_counts=pr_counts,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        if self._persistence:
            self._persistence.summaries.save(summary)

        return summary

    def generate_reports(self, experiment_id: str) -> dict[str, str]:
        """Generate Markdown and JSON reports for a given experiment ID."""
        exp = self._lifecycle_engine.get_experiment(experiment_id)
        if not exp:
            raise KeyError(f"Experiment ID '{experiment_id}' not found.")

        summary = self.generate_summary()
        recent_exps = self._lifecycle_engine.list_all_experiments()[:10]
        lifecycles = self._lifecycle_engine.get_lifecycle_history(experiment_id)
        manifest = self._manifest_engine.get_manifest_for_experiment(experiment_id)
        replays = self._replay_engine.get_replays_for_experiment(experiment_id)

        reports: dict[str, str] = {
            "experiment": generate_experiment_report(exp),
            "lifecycle": generate_lifecycle_report(experiment_id, lifecycles),
            "executive": generate_executive_summary(summary, recent_exps),
            "json": generate_json_report(exp),
        }

        if manifest:
            reports["manifest"] = generate_manifest_report(manifest)
        if replays:
            reports["replay"] = generate_replay_report(replays[0])

        return reports
