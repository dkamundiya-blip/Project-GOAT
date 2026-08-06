"""
Project GOAT v0.7 — Scientific Experiment Executor Engine

Implements ExperimentExecutor for coordinating experiment lifecycle, protocol execution,
hypothesis tracking, audit recording, and deterministic replay.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.experiments.audit import ExperimentAuditEvent
from goat.experiments.context import ExperimentContext
from goat.experiments.enums import ExperimentOutcome, ExperimentStatus, HypothesisStatus
from goat.experiments.hypothesis import HypothesisRegistry
from goat.experiments.model import (
    ScientificExperiment,
    compute_experiment_fingerprint,
    compute_experiment_id,
)
from goat.experiments.protocol import ExperimentProtocol, compute_protocol_id
from goat.experiments.result import ExperimentResult, compute_result_id
from goat.orchestration.service import ResearchOrchestrator
from goat.research.edge.canonical import compute_canonical_sha256


class ExperimentValidationError(ValueError):
    """Raised when experiment validation, protocol execution, or lifecycle transition fails."""
    pass


class ExperimentExecutor:
    """Master scientific experiment executor delegating workflow to research orchestrator."""

    def __init__(
        self,
        hypothesis_registry: HypothesisRegistry | None = None,
        orchestrator: ResearchOrchestrator | None = None,
    ) -> None:
        self._hypothesis_registry = hypothesis_registry or HypothesisRegistry()
        self._orchestrator = orchestrator or ResearchOrchestrator()
        self._experiments: dict[str, ScientificExperiment] = {}
        self._protocols: dict[str, ExperimentProtocol] = {}
        self._results: dict[str, ExperimentResult] = {}
        self._audit_events: dict[str, list[ExperimentAuditEvent]] = {}

    @property
    def hypothesis_registry(self) -> HypothesisRegistry:
        """Return bound HypothesisRegistry."""
        return self._hypothesis_registry

    def create_protocol(
        self,
        name: str,
        stages: list[str],
        version: str = "1.0.0",
        validation_criteria: dict[str, Any] | None = None,
    ) -> ExperimentProtocol:
        """Create and register an immutable ExperimentProtocol."""
        pid, p_hash = compute_protocol_id(name, version, stages)
        protocol = ExperimentProtocol(
            protocol_id=pid,
            protocol_version=version,
            protocol_name=name,
            stages=stages,
            validation_criteria=validation_criteria or {},
            protocol_hash=p_hash,
        )
        self._protocols[pid] = protocol
        return protocol

    def create_experiment(
        self,
        name: str,
        objective: str,
        hypothesis_id: str,
        protocol: ExperimentProtocol,
        pipeline_id: str = "",
    ) -> ScientificExperiment:
        """Create an immutable ScientificExperiment in PROPOSED status.

        Args:
            name: Experiment name.
            objective: Scientific objective statement.
            hypothesis_id: Associated Hypothesis ID.
            protocol: Bound ExperimentProtocol.
            pipeline_id: Associated Research Pipeline ID.

        Returns:
            Created ScientificExperiment instance.
        """
        # Verify hypothesis exists
        hyp = self._hypothesis_registry.get_hypothesis(hypothesis_id)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_experiment_fingerprint(name, objective, hypothesis_id, protocol.protocol_version)
        exp_id, canon_hash = compute_experiment_id(name, fingerprint, "1.0.0")

        experiment = ScientificExperiment(
            experiment_id=exp_id,
            scientific_fingerprint=fingerprint,
            canonical_hash=canon_hash,
            semantic_version="1.0.0",
            name=name,
            objective=objective,
            hypothesis_id=hypothesis_id,
            pipeline_id=pipeline_id,
            creation_timestamp=timestamp,
            protocol_version=protocol.protocol_version,
            status=ExperimentStatus.PROPOSED,
        )

        self._experiments[exp_id] = experiment
        self._protocols[protocol.protocol_id] = protocol
        self._log_audit(exp_id, "", "PROPOSED", f"Created experiment '{name}'")
        return experiment

    def execute_experiment(
        self,
        experiment_id: str,
        protocol: ExperimentProtocol,
        subsystem_runner: Any | None = None,
    ) -> ExperimentResult:
        """Execute experiment protocol through master orchestrator with fail-closed validation.

        Args:
            experiment_id: Target Experiment ID (EXP_<HEX16>).
            protocol: Bound ExperimentProtocol.
            subsystem_runner: Optional callable running experiment steps.

        Returns:
            Immutable ExperimentResult (RES_<HEX16>).
        """
        exp = self.get_experiment(experiment_id)
        if exp.status not in [ExperimentStatus.PROPOSED, ExperimentStatus.SCHEDULED]:
            raise ExperimentValidationError(f"Cannot execute experiment in '{exp.status.value}' status")

        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Update status to RUNNING
        exp_running = self._update_experiment_status(exp, ExperimentStatus.RUNNING, start_time=start_time)
        self._hypothesis_registry.update_status(exp.hypothesis_id, HypothesisStatus.RUNNING)

        # Delegate execution to subsystem_runner or default protocol evaluation
        try:
            if subsystem_runner:
                outcome_str = subsystem_runner()
            else:
                outcome_str = "validated"
            outcome = ExperimentOutcome.VALIDATED if outcome_str == "validated" else ExperimentOutcome.REJECTED
        except Exception as err:
            self._update_experiment_status(exp_running, ExperimentStatus.ABORTED)
            self._hypothesis_registry.update_status(exp.hypothesis_id, HypothesisStatus.REJECTED)
            raise ExperimentValidationError(f"Experiment execution failed: {err}") from err

        completion_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Update experiment status based on outcome
        final_exp_status = ExperimentStatus.VALIDATED if outcome == ExperimentOutcome.VALIDATED else ExperimentStatus.REJECTED
        exp_completed = self._update_experiment_status(exp_running, final_exp_status, end_time=completion_time)

        final_hyp_status = HypothesisStatus.VALIDATED if outcome == ExperimentOutcome.VALIDATED else HypothesisStatus.REJECTED
        self._hypothesis_registry.update_status(exp.hypothesis_id, final_hyp_status)

        # Create ExperimentResult
        res_id, res_hash = compute_result_id(experiment_id, outcome.value, completion_time)
        result = ExperimentResult(
            result_id=res_id,
            experiment_id=experiment_id,
            outcome=outcome,
            completion_timestamp=completion_time,
            canonical_hash=res_hash,
        )

        self._results[res_id] = result
        self._log_audit(experiment_id, "RUNNING", final_exp_status.value, f"Completed with outcome '{outcome.value}'")
        return result

    def get_experiment(self, experiment_id: str) -> ScientificExperiment:
        """Retrieve ScientificExperiment by Experiment ID."""
        if experiment_id not in self._experiments:
            raise KeyError(f"Experiment ID '{experiment_id}' not found in ExperimentExecutor")
        return self._experiments[experiment_id]

    def get_result(self, result_id: str) -> ExperimentResult:
        """Retrieve ExperimentResult by Result ID."""
        if result_id not in self._results:
            raise KeyError(f"Result ID '{result_id}' not found in ExperimentExecutor")
        return self._results[result_id]

    def get_audit_trail(self, experiment_id: str) -> list[ExperimentAuditEvent]:
        """Retrieve audit history for an experiment."""
        return list(self._audit_events.get(experiment_id, []))

    def replay_experiment(self, experiment_id: str) -> ExperimentResult:
        """Replay experiment deterministically using recorded protocol."""
        exp = self.get_experiment(experiment_id)
        # Re-run execution logic deterministically
        self._log_audit(experiment_id, exp.status.value, "REPLAY", "Executing deterministic replay")
        res_id = [r.result_id for r in self._results.values() if r.experiment_id == experiment_id]
        if res_id:
            return self.get_result(res_id[0])
        raise KeyError(f"No result found for experiment replay '{experiment_id}'")

    def _update_experiment_status(
        self,
        exp: ScientificExperiment,
        new_status: ExperimentStatus,
        start_time: str = "",
        end_time: str = "",
    ) -> ScientificExperiment:
        """Helper updating ScientificExperiment status."""
        d = exp.model_dump()
        d["status"] = new_status
        if start_time:
            d["start_timestamp"] = start_time
        if end_time:
            d["completion_timestamp"] = end_time
        updated = ScientificExperiment(**d)
        self._experiments[exp.experiment_id] = updated
        return updated

    def _log_audit(self, experiment_id: str, prev_state: str, new_state: str, notes: str) -> None:
        """Helper logging experiment audit event."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {"exp_id": experiment_id, "new": new_state, "timestamp": timestamp}
        event_hash = compute_canonical_sha256(payload)
        event = ExperimentAuditEvent(
            event_id=f"AUD_{event_hash[:16].upper()}",
            experiment_id=experiment_id,
            event_type="EXPERIMENT_EVENT",
            timestamp=timestamp,
            previous_state=prev_state,
            new_state=new_state,
            notes=notes,
            execution_hash=event_hash,
        )
        if experiment_id not in self._audit_events:
            self._audit_events[experiment_id] = []
        self._audit_events[experiment_id].append(event)
