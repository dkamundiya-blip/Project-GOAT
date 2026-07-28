"""
Project GOAT v0.6 — Stage B: Retention / Replication Validator

Evaluates effect retention ratio and direction consistency on validation/replication data.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.exceptions import StageValidationError
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.base import BaseStageValidator
from goat.research.hypothesis.testing import calculate_effect_size, run_statistical_test


class StageBValidator(BaseStageValidator):
    """Validator for Stage B: Retention / Replication."""

    @property
    def stage(self) -> ValidationStage:
        return ValidationStage.STAGE_B_RETENTION

    @property
    def prerequisite_stage(self) -> ValidationStage | None:
        return ValidationStage.STAGE_A_DISCOVERY

    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        stage_a_result: StageResult | None = None,
        discovery_effect: float = 0.0,
        val_cond_arr: np.ndarray | None = None,
        val_base_arr: np.ndarray | None = None,
        **kwargs: Any,
    ) -> StageResult:
        """Evaluate Stage B retention contract.

        Args:
            candidate_edge: CandidateEdge under evaluation.
            hypothesis_version: Frozen hypothesis version string.
            policy: ValidationPolicy thresholds.
            validation_run: ValidationRunInfo metadata.
            dataset_partitions: Dict containing "validation" DataFrame partition.
            stage_a_result: StageResult from Stage A (must be PASS).
            discovery_effect: Effect size observed during Stage A discovery.
            val_cond_arr: Optional direct array of validation conditional observations.
            val_base_arr: Optional direct array of validation baseline observations.

        Returns:
            StageResult containing PASS/FAIL decision and evidence.
        """
        # Precondition Guard: Stage A must have passed
        if stage_a_result is not None and stage_a_result.decision != StageDecision.PASS:
            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.FAIL,
                reason_code=ReasonCode.PREREQUISITE_FAILED,
                policy_hash=policy.policy_hash,
                explanation=f"Stage B blocked: Stage A prerequisite failed with decision '{stage_a_result.decision.value}'",
            )

        # Extract observations
        if val_cond_arr is None or val_base_arr is None:
            val_df = dataset_partitions.get("validation")
            if val_df is None or (isinstance(val_df, pd.DataFrame) and val_df.empty):
                cond_clean = np.array([])
                base_clean = np.array([])
            else:
                if isinstance(val_df, pd.DataFrame):
                    c_col = val_df.get("conditional_outcome", pd.Series(dtype=float))
                    b_col = val_df.get("baseline_outcome", pd.Series(dtype=float))
                    cond_clean = np.asarray(c_col, dtype=np.float64)
                    base_clean = np.asarray(b_col, dtype=np.float64)
                else:
                    cond_clean = np.array([])
                    base_clean = np.array([])
        else:
            cond_clean = np.asarray(val_cond_arr, dtype=np.float64)
            base_clean = np.asarray(val_base_arr, dtype=np.float64)

        cond_clean = cond_clean[np.isfinite(cond_clean)]
        base_clean = base_clean[np.isfinite(base_clean)]

        sample_count = len(cond_clean)

        if sample_count < 2 or len(base_clean) < 2:
            val_effect = 0.0
            stat_val, raw_p = 0.0, 1.0
        else:
            val_effect = calculate_effect_size(cond_clean, base_clean, method="cohens_d")
            stat_val, raw_p = run_statistical_test(cond_clean, base_clean, test_type="welch_ttest")

        # 1. Zero-Safety & Structurally Impossible Discovery Effect Check
        if discovery_effect == 0.0:
            retention_ratio = 0.0
        else:
            retention_ratio = float(abs(val_effect) / abs(discovery_effect))

        # 2. Direction Consistency Gate
        if discovery_effect != 0.0 and val_effect != 0.0:
            if np.sign(val_effect) != np.sign(discovery_effect):
                decision = StageDecision.FAIL
                reason_code = ReasonCode.DIRECTION_REVERSED
                explanation = (
                    f"Effect direction reversed in validation split: discovery sign={np.sign(discovery_effect)}, "
                    f"validation sign={np.sign(val_effect)}"
                )
            elif retention_ratio < policy.stage_b_min_retention_ratio:
                decision = StageDecision.FAIL
                reason_code = ReasonCode.RETENTION_FAILED
                explanation = (
                    f"Retention ratio ({retention_ratio:.4f}) below minimum threshold ({policy.stage_b_min_retention_ratio:.4f})"
                )
            else:
                decision = StageDecision.PASS
                reason_code = ReasonCode.PASSED
                explanation = (
                    f"Stage B retention passed (val_d={val_effect:.4f}, retention_ratio={retention_ratio:.4f})"
                )
        elif retention_ratio < policy.stage_b_min_retention_ratio:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.RETENTION_FAILED
            explanation = (
                f"Retention ratio ({retention_ratio:.4f}) below minimum threshold ({policy.stage_b_min_retention_ratio:.4f})"
            )
        else:
            decision = StageDecision.PASS
            reason_code = ReasonCode.PASSED
            explanation = f"Stage B retention passed (val_d={val_effect:.4f})"

        ev = self.create_evidence_record(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            dimension_type=EvidenceDimensionType.REPLICATION,
            dimension_key=f"{candidate_edge.causal_primitive}_{candidate_edge.target_feature}",
            partition_identity="validation",
            sample_count=sample_count,
            effect_size=val_effect,
            raw_p_value=raw_p,
            statistic_value=stat_val,
            context_metadata={
                "discovery_effect": discovery_effect,
                "retention_ratio": retention_ratio,
            },
        )

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
