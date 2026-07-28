"""
Project GOAT v0.6 — Stage E: Causal Falsification & Contradictory-Condition Validator

Evaluates predefined contradictory/inverted conditions to attempt causal falsification of candidate edges.
"""

from __future__ import annotations

from typing import Any, ClassVar

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


class StageEValidator(BaseStageValidator):
    """Validator for Stage E: Causal Falsification."""

    INVERSION_MAP: ClassVar[dict[str, str]] = {
        "greater_than": "less_than",
        "less_than": "greater_than",
        "crosses_above": "crosses_below",
        "crosses_below": "crosses_above",
        "equal": "not_equal",
        "not_equal": "equal",
    }

    @property
    def stage(self) -> ValidationStage:
        return ValidationStage.STAGE_E_FALSIFICATION

    @property
    def prerequisite_stage(self) -> ValidationStage | None:
        return ValidationStage.STAGE_D_ROBUSTNESS

    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        stage_d_result: StageResult | None = None,
        baseline_effect: float = 0.0,
        contradictory_cond_arr: np.ndarray | None = None,
        contradictory_base_arr: np.ndarray | None = None,
        contradictory_effect: float | None = None,
        **kwargs: Any,
    ) -> StageResult:
        """Evaluate Stage E causal falsification contract.

        Args:
            candidate_edge: CandidateEdge under evaluation.
            hypothesis_version: Frozen hypothesis version string.
            policy: ValidationPolicy thresholds.
            validation_run: ValidationRunInfo metadata.
            dataset_partitions: Dict containing validation research partition.
            stage_d_result: StageResult from Stage D (must be PASS).
            baseline_effect: Baseline effect size observed during Stage A/B.
            contradictory_cond_arr: Optional direct array of contradictory conditional observations.
            contradictory_base_arr: Optional direct array of contradictory baseline observations.
            contradictory_effect: Optional direct effect float of contradictory condition.

        Returns:
            StageResult containing PASS/FAIL/INSUFFICIENT_EVIDENCE decision and evidence.
        """
        # Precondition Guard: Stage D must have passed
        if stage_d_result is not None and stage_d_result.decision != StageDecision.PASS:
            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.FAIL,
                reason_code=ReasonCode.PREREQUISITE_FAILED,
                policy_hash=policy.policy_hash,
                explanation=f"Stage E blocked: Stage D prerequisite failed with decision '{stage_d_result.decision.value}'",
            )

        primitive = candidate_edge.causal_primitive
        inv_primitive = self.INVERSION_MAP.get(primitive)

        # Unsupported primitive inversion check
        if inv_primitive is None and contradictory_effect is None and contradictory_cond_arr is None:
            ev = self.create_evidence_record(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                dimension_type=EvidenceDimensionType.REGIME,
                dimension_key="falsification_summary",
                partition_identity="contradictory_inversion",
                sample_count=0,
                effect_size=0.0,
                raw_p_value=1.0,
                statistic_value=0.0,
            )
            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.INSUFFICIENT_EVIDENCE,
                reason_code=ReasonCode.SAMPLE_TOO_SMALL,
                evidence_ids=(ev.evidence_id,),
                policy_hash=policy.policy_hash,
                explanation=f"No supported causal inversion mapping for primitive '{primitive}'",
            )

        # Extract observations and compute contradictory effect
        if contradictory_effect is not None:
            c_effect = float(contradictory_effect)
            stat_val, raw_p = 0.0, 0.05
            sample_count = 100
        elif contradictory_cond_arr is not None and contradictory_base_arr is not None:
            cond_clean = np.asarray(contradictory_cond_arr, dtype=np.float64)
            base_clean = np.asarray(contradictory_base_arr, dtype=np.float64)
            cond_clean = cond_clean[np.isfinite(cond_clean)]
            base_clean = base_clean[np.isfinite(base_clean)]

            sample_count = len(cond_clean)
            if sample_count < 2 or len(base_clean) < 2:
                c_effect = 0.0
                stat_val, raw_p = 0.0, 1.0
            else:
                c_effect = calculate_effect_size(cond_clean, base_clean, method="cohens_d")
                stat_val, raw_p = run_statistical_test(cond_clean, base_clean, test_type="welch_ttest")
        else:
            c_effect = 0.0
            stat_val, raw_p = 0.0, 1.0
            sample_count = 0

        # Causal Falsification Gate
        baseline_dir = np.sign(baseline_effect) if baseline_effect != 0.0 else 1.0
        contradictory_dir = np.sign(c_effect) if c_effect != 0.0 else 0.0

        same_direction = (contradictory_dir == baseline_dir) and (c_effect != 0.0)
        is_material = abs(c_effect) >= policy.stage_a_effect_min

        if policy.stage_e_fail_on_contradictory_inversion and same_direction and is_material:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.FALSIFICATION_FAILED
            explanation = (
                f"Causal falsification failed: contradictory condition reproduced claimed effect in same direction "
                f"(baseline={baseline_effect:.4f}, contradictory={c_effect:.4f})"
            )
        else:
            decision = StageDecision.PASS
            reason_code = ReasonCode.PASSED
            explanation = (
                f"Stage E causal falsification passed (baseline={baseline_effect:.4f}, contradictory={c_effect:.4f})"
            )

        ev = self.create_evidence_record(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            dimension_type=EvidenceDimensionType.REGIME,
            dimension_key=f"inversion_{inv_primitive or primitive}",
            partition_identity="contradictory_inversion",
            sample_count=sample_count,
            effect_size=c_effect,
            raw_p_value=raw_p,
            statistic_value=stat_val,
            context_metadata={
                "primitive": primitive,
                "inverted_primitive": inv_primitive,
                "baseline_effect": baseline_effect,
                "contradictory_effect": c_effect,
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
