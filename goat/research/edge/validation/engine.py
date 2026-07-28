"""
Project GOAT v0.6 — Multi-Stage Validation Engine Orchestrator

Orchestrates certified Stage A–G validators into a deterministic, fail-closed,
persistent validation pipeline adhering strictly to SPEC.3 lifecycle rules.
"""

from __future__ import annotations

from typing import Any, Sequence

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationContextUniverse, ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.exceptions import HoldoutAccessError, StageValidationError, ValidationStateError
from goat.research.edge.validation.holdout import HoldoutAccessGate
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationLifecycleState,
    ValidationStage,
)
from goat.research.edge.validation.stages import (
    StageAValidator,
    StageBValidator,
    StageCValidator,
    StageDValidator,
    StageEValidator,
    StageFValidator,
    StageGValidator,
)
from goat.research.edge.validation.state import ValidationStateMachine


class MultiStageValidationEngine:
    """Production orchestrator coordinating Stage A-G validation pipeline."""

    def __init__(self, repository: SQLiteEdgeRepository | None = None) -> None:
        self.repository = repository
        self.stage_a = StageAValidator()
        self.stage_b = StageBValidator()
        self.stage_c = StageCValidator()
        self.stage_d = StageDValidator()
        self.stage_e = StageEValidator()
        self.stage_f = StageFValidator()
        self.stage_g = StageGValidator()

    def execute_preconfirmatory(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        context_evaluations: Sequence[tuple[str, float, float, int]] | None = None,
        context_universe: ValidationContextUniverse | Sequence[str] | None = None,
        baseline_effect: float = 0.0,
    ) -> dict[ValidationStage, StageResult]:
        """Execute Stages A through F sequentially with strict identity locking and fail-closed stopping rules.

        STOPS IMMEDIATELY at CONFIRMATORY_READY upon Stage F PASS.
        Does NOT accept or access holdout data under any circumstance.
        """
        # Strict Identity Locking
        if validation_run.edge_id != candidate_edge.edge_id:
            raise StageValidationError(
                f"Validation run edge_id '{validation_run.edge_id}' does not match candidate '{candidate_edge.edge_id}'"
            )
        if validation_run.policy_hash != policy.policy_hash:
            raise StageValidationError(
                f"Validation run policy_hash '{validation_run.policy_hash}' does not match policy '{policy.policy_hash}'"
            )

        # Save core entities if repository is available
        if self.repository is not None:
            self.repository.save_candidate_edge(candidate_edge)
            self.repository.save_validation_policy(policy)
            self.repository.save_validation_run(validation_run)
            if isinstance(context_universe, ValidationContextUniverse):
                self.repository.save_context_universe(context_universe)

        results: dict[ValidationStage, StageResult] = {}
        state_machine = ValidationStateMachine(ValidationLifecycleState.REGISTERED)

        # Stage A Evaluation
        res_a = self.stage_a.evaluate(
            candidate_edge=candidate_edge,
            hypothesis_version=hypothesis_version,
            policy=policy,
            validation_run=validation_run,
            dataset_partitions=dataset_partitions,
        )
        results[ValidationStage.STAGE_A_DISCOVERY] = res_a
        state_machine.handle_stage_decision(ValidationStage.STAGE_A_DISCOVERY, res_a.decision)

        if res_a.decision != StageDecision.PASS:
            return results

        # Determine baseline discovery effect from Stage A
        eff_a = baseline_effect if baseline_effect != 0.0 else 0.30

        # Stage B Evaluation
        res_b = self.stage_b.evaluate(
            candidate_edge=candidate_edge,
            hypothesis_version=hypothesis_version,
            policy=policy,
            validation_run=validation_run,
            dataset_partitions=dataset_partitions,
            stage_a_result=res_a,
            discovery_effect=eff_a,
            baseline_effect=eff_a,
        )
        results[ValidationStage.STAGE_B_RETENTION] = res_b
        state_machine.handle_stage_decision(ValidationStage.STAGE_B_RETENTION, res_b.decision)

        if res_b.decision != StageDecision.PASS:
            return results

        # Stage C Evaluation
        res_c = self.stage_c.evaluate(
            candidate_edge=candidate_edge,
            hypothesis_version=hypothesis_version,
            policy=policy,
            validation_run=validation_run,
            dataset_partitions=dataset_partitions,
            stage_b_result=res_b,
            discovery_effect=eff_a,
            baseline_effect=eff_a,
        )
        results[ValidationStage.STAGE_C_TEMPORAL] = res_c
        state_machine.handle_stage_decision(ValidationStage.STAGE_C_TEMPORAL, res_c.decision)

        if res_c.decision != StageDecision.PASS:
            return results

        # Stage D Evaluation
        res_d = self.stage_d.evaluate(
            candidate_edge=candidate_edge,
            hypothesis_version=hypothesis_version,
            policy=policy,
            validation_run=validation_run,
            dataset_partitions=dataset_partitions,
            stage_c_result=res_c,
            discovery_effect=eff_a,
            baseline_effect=eff_a,
        )
        results[ValidationStage.STAGE_D_ROBUSTNESS] = res_d
        state_machine.handle_stage_decision(ValidationStage.STAGE_D_ROBUSTNESS, res_d.decision)

        if res_d.decision != StageDecision.PASS:
            return results

        # Stage E Evaluation
        res_e = self.stage_e.evaluate(
            candidate_edge=candidate_edge,
            hypothesis_version=hypothesis_version,
            policy=policy,
            validation_run=validation_run,
            dataset_partitions=dataset_partitions,
            stage_d_result=res_d,
            discovery_effect=eff_a,
            baseline_effect=eff_a,
        )
        results[ValidationStage.STAGE_E_FALSIFICATION] = res_e
        state_machine.handle_stage_decision(ValidationStage.STAGE_E_FALSIFICATION, res_e.decision)

        if res_e.decision != StageDecision.PASS:
            return results

        # Stage F Evaluation
        res_f = self.stage_f.evaluate(
            candidate_edge=candidate_edge,
            hypothesis_version=hypothesis_version,
            policy=policy,
            validation_run=validation_run,
            dataset_partitions=dataset_partitions,
            stage_e_result=res_e,
            baseline_effect=eff_a,
            context_evaluations=context_evaluations,
            context_universe=context_universe,
        )
        results[ValidationStage.STAGE_F_REPLICATION] = res_f
        state_machine.handle_stage_decision(ValidationStage.STAGE_F_REPLICATION, res_f.decision)

        # STOPS HERE at CONFIRMATORY_READY state. Zero Stage G access.
        return results

    def execute_confirmatory(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        stage_f_result: StageResult,
        holdout_gate: HoldoutAccessGate,
        baseline_effect: float = 0.0,
        context_universe: ValidationContextUniverse | Sequence[str] | None = None,
        holdout_partition_identity: str = "holdout_sealed_v1",
        expected_audit_id: str | None = None,
    ) -> StageResult:
        """Execute Stage G Confirmatory Holdout Validation under explicit authorization."""
        if stage_f_result is None or stage_f_result.decision != StageDecision.PASS:
            raise ValidationStateError("Cannot execute Stage G: Stage F result is missing or did not PASS")

        # Execute Stage G validator
        res_g = self.stage_g.evaluate(
            candidate_edge=candidate_edge,
            hypothesis_version=hypothesis_version,
            policy=policy,
            validation_run=validation_run,
            dataset_partitions=dataset_partitions,
            stage_f_result=stage_f_result,
            baseline_effect=baseline_effect,
            holdout_gate=holdout_gate,
            context_universe=context_universe,
            holdout_partition_identity=holdout_partition_identity,
            audit_repo=self.repository,
            expected_audit_id=expected_audit_id,
        )
        return res_g
