"""
Project GOAT v0.6 — Stage G: Confirmatory Holdout Validator

Evaluates whether a candidate edge confirmed on a sealed holdout partition
without post-hoc tuning, repeated testing, or dataset re-access.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import EvidenceDimensionType
from goat.research.edge.models import (
    ValidationContextUniverse,
    ValidationRunInfo,
    compute_confirmatory_audit_id,
)
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.persistence.exceptions import RecordNotFoundError
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.exceptions import (
    HoldoutAccessError,
    StageValidationError,
)
from goat.research.edge.validation.holdout import HoldoutAccessGate
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.base import BaseStageValidator


class StageGValidator(BaseStageValidator):
    """Validator for Stage G: Confirmatory Holdout Validation."""

    @property
    def stage(self) -> ValidationStage:
        return ValidationStage.STAGE_G_HOLDOUT

    @property
    def prerequisite_stage(self) -> ValidationStage | None:
        return ValidationStage.STAGE_F_REPLICATION

    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        stage_f_result: StageResult | None = None,
        baseline_effect: float = 0.0,
        holdout_gate: HoldoutAccessGate | None = None,
        context_universe: ValidationContextUniverse | Sequence[str] | None = None,
        holdout_partition_identity: str = "holdout_sealed_v1",
        audit_repo: SQLiteEdgeRepository | None = None,
        expected_audit_id: str | None = None,
        **kwargs: Any,
    ) -> StageResult:
        """Evaluate Stage G confirmatory holdout validation contract under strict pre-access authorization.

        Args:
            candidate_edge: CandidateEdge under evaluation.
            hypothesis_version: Frozen hypothesis version string.
            policy: ValidationPolicy thresholds.
            validation_run: ValidationRunInfo metadata.
            dataset_partitions: Dict containing 'holdout' synthetic partition.
            stage_f_result: StageResult from Stage F (must be PASS).
            baseline_effect: Baseline effect size observed during discovery.
            holdout_gate: HoldoutAccessGate security gate (must be SEALED).
            context_universe: Pre-registered ValidationContextUniverse.
            holdout_partition_identity: Identity of holdout partition.
            audit_repo: Optional SQLiteEdgeRepository for confirmatory persistence.
            expected_audit_id: Expected pre-registered confirmatory audit identity.

        Returns:
            StageResult containing PASS or FAIL decision and confirmatory evidence.

        Raises:
            HoldoutAccessError: If authorization fails, gate state is invalid, or holdout was previously exposed.
            StageValidationError: If preregistration parameters mismatch.
        """
        # Precondition 1: Stage F Prerequisite Check
        if stage_f_result is None or stage_f_result.decision != StageDecision.PASS:
            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.FAIL,
                reason_code=ReasonCode.PREREQUISITE_FAILED,
                policy_hash=policy.policy_hash,
                explanation="Stage G blocked: Stage F prerequisite failed or was not evaluated",
            )

        # Precondition 2: Holdout Gate Presence
        if holdout_gate is None:
            raise HoldoutAccessError("Stage G blocked: HoldoutAccessGate security gate instance must be provided")

        # Precondition 3: Input Integrity Checks
        if validation_run.edge_id != candidate_edge.edge_id:
            raise StageValidationError(
                f"Stage G edge_id mismatch: validation_run '{validation_run.edge_id}' != candidate '{candidate_edge.edge_id}'"
            )

        if validation_run.policy_hash != policy.policy_hash:
            raise StageValidationError(
                f"Stage G policy_hash mismatch: validation_run '{validation_run.policy_hash}' != policy '{policy.policy_hash}'"
            )

        if not str(hypothesis_version).strip():
            raise StageValidationError("Stage G blocked: hypothesis_version must be a non-empty string")

        # Precondition 4: Compute & Verify Pre-Access Confirmatory Audit Identity
        computed_audit_id = compute_confirmatory_audit_id(
            validation_run_id=validation_run.validation_run_id,
            frozen_hypothesis_version=hypothesis_version,
            dataset_fingerprint=validation_run.dataset_fingerprint,
            policy_hash=policy.policy_hash,
            holdout_partition_identity=holdout_partition_identity,
        )

        if expected_audit_id is not None and expected_audit_id != computed_audit_id:
            raise HoldoutAccessError(
                f"Confirmatory audit ID mismatch: expected '{expected_audit_id}' != computed '{computed_audit_id}'"
            )

        # Process-Restart Persistence Safety Check
        if audit_repo is not None:
            try:
                existing_audit = audit_repo.get_confirmatory_audit(computed_audit_id)
                if existing_audit:
                    raise HoldoutAccessError(
                        f"Confirmatory holdout audit '{computed_audit_id}' already exists in persistence store. "
                        "Re-execution of Stage G after prior holdout exposure is strictly prohibited."
                    )
            except RecordNotFoundError:
                pass

        # Precondition 5: Gate Must Be SEALED Before Authorization
        if holdout_gate.current_state != HoldoutAccessGate().current_state:  # HoldoutState.SEALED
            if not holdout_gate.is_authorized:
                raise HoldoutAccessError(
                    f"Stage G authorization denied: HoldoutAccessGate is in invalid state '{holdout_gate.current_state.value}'"
                )

        # Execute Pre-Access Gate Authorization
        if holdout_gate.current_state == HoldoutAccessGate().current_state:
            auth_audit_id = holdout_gate.authorize_access(
                edge_id=candidate_edge.edge_id,
                hypothesis_version=hypothesis_version,
                policy_hash=policy.policy_hash,
                dataset_fingerprint=validation_run.dataset_fingerprint,
                holdout_partition_identity=holdout_partition_identity,
                validation_run_id=validation_run.validation_run_id,
            )

            if auth_audit_id != computed_audit_id:
                raise HoldoutAccessError(
                    f"Authorized audit_id '{auth_audit_id}' != computed audit_id '{computed_audit_id}'"
                )

        # Execute Single-Shot Holdout Access Callback
        def _fetch_holdout_data() -> pd.DataFrame | np.ndarray:
            if "holdout" not in dataset_partitions:
                raise HoldoutAccessError("Dataset partitions missing mandatory 'holdout' partition key")
            return dataset_partitions["holdout"]

        holdout_data = holdout_gate.access_holdout(_fetch_holdout_data)

        # Statistical Confirmatory Evaluation
        if isinstance(holdout_data, pd.DataFrame):
            if "effect" in holdout_data.columns:
                arr = holdout_data["effect"].dropna().to_numpy()
            else:
                arr = holdout_data.iloc[:, 0].dropna().to_numpy()
        else:
            arr = np.asarray(holdout_data).ravel()

        if len(arr) < policy.stage_a_min_sample:
            raise StageValidationError(
                f"Confirmatory holdout sample count ({len(arr)}) below minimum requirement ({policy.stage_a_min_sample})"
            )

        sample_count = len(arr)
        mean_eff = float(np.mean(arr))
        std_eff = float(np.std(arr, ddof=1)) if sample_count > 1 else 1.0

        if std_eff > 1e-12:
            t_stat = mean_eff / (std_eff / np.sqrt(sample_count))
            p_val = float(2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=sample_count - 1)))
        else:
            p_val = 1.0 if mean_eff == 0.0 else 0.0

        expected_dir = np.sign(baseline_effect) if baseline_effect != 0.0 else 1.0
        same_direction = (np.sign(mean_eff) == expected_dir) if mean_eff != 0.0 else False
        mag_ok = abs(mean_eff) >= policy.stage_a_effect_min
        sig_ok = p_val <= policy.stage_a_alpha

        if same_direction and mag_ok and sig_ok:
            decision = StageDecision.PASS
            reason_code = ReasonCode.PASSED
            explanation = (
                f"Stage G confirmatory holdout validation passed (effect={mean_eff:.4f}, p_val={p_val:.6f})"
            )
        else:
            decision = StageDecision.FAIL
            reason_code = (
                ReasonCode.REPLICATION_FAILED
                if not same_direction or not mag_ok
                else ReasonCode.SIGNIFICANCE_FAILED
            )
            explanation = (
                f"Stage G confirmatory holdout validation failed (effect={mean_eff:.4f}, p_val={p_val:.6f}, dir_ok={same_direction})"
            )

        # Create Confirmatory Atomic Evidence Record
        ev = self.create_evidence_record(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            dimension_type=EvidenceDimensionType.CONFIRMATORY,
            dimension_key="holdout_confirmatory",
            partition_identity=holdout_partition_identity,
            sample_count=sample_count,
            effect_size=mean_eff,
            raw_p_value=p_val,
            statistic_value=float(t_stat) if std_eff > 1e-12 else 0.0,
            context_metadata={
                "audit_id": computed_audit_id,
                "hypothesis_version": hypothesis_version,
                "baseline_effect": baseline_effect,
                "holdout_bytes_read": holdout_gate.bytes_read,
            },
        )

        # Persist Audit & Evidence Record if repository is provided
        if audit_repo is not None:
            audit_repo.save_confirmatory_audit(
                validation_run_id=validation_run.validation_run_id,
                frozen_hypothesis_version=hypothesis_version,
                dataset_fingerprint=validation_run.dataset_fingerprint,
                policy_hash=policy.policy_hash,
                holdout_partition_identity=holdout_partition_identity,
            )
            audit_repo.save_evidence_record(ev)

        return StageResult(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            stage=self.stage,
            decision=decision,
            reason_code=reason_code,
            evidence_ids=(ev.evidence_id,),
            policy_hash=policy.policy_hash,
            explanation=explanation,
        )
