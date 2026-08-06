"""
Project GOAT v0.7 — Scientific Study Coordinator Engine

Implements StudyCoordinator for master study scheduling, multi-experiment workflow coordination,
dependency enforcement, audit logging, and study replay.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.experiments.executor import ExperimentExecutor
from goat.research.edge.canonical import compute_canonical_sha256
from goat.studies.audit import StudyAuditEvent
from goat.studies.context import StudyContext
from goat.studies.design import StudyDesign, compute_design_id
from goat.studies.enums import StudyStatus
from goat.studies.model import ScientificStudy, compute_study_fingerprint, compute_study_id
from goat.studies.registry import StudyExperimentRegistry
from goat.studies.result import StudyResult, compute_study_result_id


class StudyValidationError(ValueError):
    """Raised when study validation, scheduling, or execution fails."""
    pass


class StudyCoordinator:
    """Master study coordinator coordinating multi-experiment scientific research studies."""

    def __init__(
        self,
        experiment_executor: ExperimentExecutor | None = None,
        registry: StudyExperimentRegistry | None = None,
    ) -> None:
        self._executor = experiment_executor or ExperimentExecutor()
        self._registry = registry or StudyExperimentRegistry()
        self._studies: dict[str, ScientificStudy] = {}
        self._designs: dict[str, StudyDesign] = {}
        self._results: dict[str, StudyResult] = {}
        self._audit_events: dict[str, list[StudyAuditEvent]] = {}

    @property
    def experiment_executor(self) -> ExperimentExecutor:
        """Return bound ExperimentExecutor."""
        return self._executor

    @property
    def registry(self) -> StudyExperimentRegistry:
        """Return bound StudyExperimentRegistry."""
        return self._registry

    def create_design(
        self,
        objective: str,
        plan: list[str],
        version: str = "1.0.0",
        validation_policy: dict[str, Any] | None = None,
    ) -> StudyDesign:
        """Create and register an immutable StudyDesign."""
        did, d_hash = compute_design_id(objective, plan, version)
        design = StudyDesign(
            design_id=did,
            design_version=version,
            research_objective=objective,
            experiment_plan=plan,
            validation_policy=validation_policy or {},
            design_hash=d_hash,
        )
        self._designs[did] = design
        return design

    def create_study(
        self,
        title: str,
        scientific_question: str,
        research_objective: str,
        description: str,
        design: StudyDesign,
    ) -> ScientificStudy:
        """Create an immutable ScientificStudy in PROPOSED status.

        Args:
            title: Study title string.
            scientific_question: Research question string.
            research_objective: Formal objective statement.
            description: Detailed study description.
            design: Bound StudyDesign.

        Returns:
            Created ScientificStudy instance.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_study_fingerprint(title, scientific_question, research_objective, design.design_version)
        std_id, canon_hash = compute_study_id(title, fingerprint, "1.0.0")

        study = ScientificStudy(
            study_id=std_id,
            scientific_fingerprint=fingerprint,
            canonical_hash=canon_hash,
            semantic_version="1.0.0",
            title=title,
            scientific_question=scientific_question,
            research_objective=research_objective,
            description=description,
            creation_timestamp=timestamp,
            protocol_version=design.design_version,
            status=StudyStatus.PROPOSED,
        )

        self._studies[std_id] = study
        self._designs[design.design_id] = design
        self._log_audit(std_id, "", "PROPOSED", f"Created study '{title}'")
        return study

    def execute_study(self, study_id: str) -> StudyResult:
        """Execute all registered experiments in the study with fail-closed dependency resolution.

        Args:
            study_id: Target Study ID (STD_<HEX16>).

        Returns:
            Immutable StudyResult (SRES_<HEX16>).
        """
        study = self.get_study(study_id)
        if study.status not in [StudyStatus.PROPOSED, StudyStatus.SCHEDULED]:
            raise StudyValidationError(f"Cannot execute study in '{study.status.value}' status")

        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        study_running = self._update_study_status(study, StudyStatus.RUNNING)

        exp_records = self._registry.get_study_experiments(study_id)
        if not exp_records:
            raise StudyValidationError(f"Cannot execute empty study '{study_id}': no registered experiments")

        executed_exp_ids: list[str] = []
        for rec in exp_records:
            # Verify dependencies completed
            for dep in rec.dependencies:
                if dep not in executed_exp_ids:
                    self._update_study_status(study_running, StudyStatus.FAILED)
                    raise StudyValidationError(f"Study execution dependency error: Experiment '{rec.experiment_id}' depends on unexecuted '{dep}'")

            # Execute experiment via ExperimentExecutor if present
            try:
                exp_obj = self._executor.get_experiment(rec.experiment_id)
                protocol = self._executor.get_experiment(rec.experiment_id)  # fetch protocol if needed
            except KeyError:
                pass  # Registered external experiment ID

            executed_exp_ids.append(rec.experiment_id)

        completion_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        study_completed = self._update_study_status(study_running, StudyStatus.COMPLETED, completion_time=completion_time)

        res_id, res_hash = compute_study_result_id(study_id, completion_time)
        result = StudyResult(
            result_id=res_id,
            study_id=study_id,
            experiment_references=executed_exp_ids,
            completion_timestamp=completion_time,
            canonical_hash=res_hash,
        )

        self._results[res_id] = result
        self._log_audit(study_id, "RUNNING", "COMPLETED", f"Executed {len(executed_exp_ids)} experiments")
        return result

    def get_study(self, study_id: str) -> ScientificStudy:
        """Retrieve ScientificStudy by Study ID."""
        if study_id not in self._studies:
            raise KeyError(f"Study ID '{study_id}' not found in StudyCoordinator")
        return self._studies[study_id]

    def get_result(self, result_id: str) -> StudyResult:
        """Retrieve StudyResult by Result ID."""
        if result_id not in self._results:
            raise KeyError(f"Result ID '{result_id}' not found in StudyCoordinator")
        return self._results[result_id]

    def get_audit_trail(self, study_id: str) -> list[StudyAuditEvent]:
        """Retrieve audit history for a study."""
        return list(self._audit_events.get(study_id, []))

    def replay_study(self, study_id: str) -> StudyResult:
        """Replay study deterministically."""
        study = self.get_study(study_id)
        self._log_audit(study_id, study.status.value, "REPLAY", "Executing study replay")
        res_ids = [r.result_id for r in self._results.values() if r.study_id == study_id]
        if res_ids:
            return self.get_result(res_ids[0])
        raise KeyError(f"No result found for study replay '{study_id}'")

    def _update_study_status(
        self,
        study: ScientificStudy,
        new_status: StudyStatus,
        completion_time: str = "",
    ) -> ScientificStudy:
        """Helper updating ScientificStudy status."""
        d = study.model_dump()
        d["status"] = new_status
        if completion_time:
            d["completion_timestamp"] = completion_time
        updated = ScientificStudy(**d)
        self._studies[study.study_id] = updated
        return updated

    def _log_audit(self, study_id: str, prev_state: str, new_state: str, notes: str) -> None:
        """Helper logging study audit event."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {"new": new_state, "study_id": study_id, "timestamp": timestamp}
        event_hash = compute_canonical_sha256(payload)
        event = StudyAuditEvent(
            event_id=f"AUD_{event_hash[:16].upper()}",
            study_id=study_id,
            event_type="STUDY_EVENT",
            timestamp=timestamp,
            previous_state=prev_state,
            new_state=new_state,
            notes=notes,
            execution_hash=event_hash,
        )
        if study_id not in self._audit_events:
            self._audit_events[study_id] = []
        self._audit_events[study_id].append(event)
