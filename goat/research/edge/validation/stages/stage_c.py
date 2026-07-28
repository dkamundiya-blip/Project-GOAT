"""
Project GOAT v0.6 — Stage C: Temporal Stability Validator

Evaluates walk-forward fold consistency, directional fold ratios, and fold coefficient of variation (CV).
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.exceptions import StageValidationError
from goat.research.edge.validation.leakage import TemporalLeakageGuard
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.base import BaseStageValidator
from goat.research.hypothesis.testing import calculate_effect_size, run_statistical_test


class StageCValidator(BaseStageValidator):
    """Validator for Stage C: Temporal Stability."""

    @property
    def stage(self) -> ValidationStage:
        return ValidationStage.STAGE_C_TEMPORAL

    @property
    def prerequisite_stage(self) -> ValidationStage | None:
        return ValidationStage.STAGE_B_RETENTION

    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        stage_b_result: StageResult | None = None,
        discovery_effect: float = 0.0,
        fold_observations: Sequence[tuple[np.ndarray, np.ndarray]] | None = None,
        embargo_horizon_bars: int = 5,
        **kwargs: Any,
    ) -> StageResult:
        """Evaluate Stage C walk-forward temporal stability contract.

        Args:
            candidate_edge: CandidateEdge under evaluation.
            hypothesis_version: Frozen hypothesis version string.
            policy: ValidationPolicy thresholds.
            validation_run: ValidationRunInfo metadata.
            dataset_partitions: Dict containing research partitions.
            stage_b_result: StageResult from Stage B (must be PASS).
            discovery_effect: Effect size observed during Stage A discovery.
            fold_observations: List of (cond_arr, base_arr) tuples for each walk-forward fold.
            embargo_horizon_bars: Minimum embargo gap bars between adjacent folds.

        Returns:
            StageResult containing PASS/FAIL/INSUFFICIENT_EVIDENCE decision and fold evidence.
        """
        # Precondition Guard: Stage B must have passed
        if stage_b_result is not None and stage_b_result.decision != StageDecision.PASS:
            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.FAIL,
                reason_code=ReasonCode.PREREQUISITE_FAILED,
                policy_hash=policy.policy_hash,
                explanation=f"Stage C blocked: Stage B prerequisite failed with decision '{stage_b_result.decision.value}'",
            )

        if fold_observations is None:
            raw_folds = dataset_partitions.get("walk_forward_folds", [])
            parsed_folds = []
            for item in raw_folds:
                if isinstance(item, tuple):
                    parsed_folds.append(item)
                elif isinstance(item, pd.DataFrame):
                    c_col = item.get("conditional_outcome", item.get("effect", item.iloc[:, 0]))
                    b_col = item.get("baseline_outcome", pd.Series(0.0, index=item.index))
                    parsed_folds.append((c_col.dropna().to_numpy(), b_col.dropna().to_numpy()))
            fold_observations = parsed_folds

        folds = list(fold_observations or [])
        num_folds = len(folds)

        # 1. Minimum Fold Count Gate
        if num_folds < policy.stage_c_min_folds:
            ev = self.create_evidence_record(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                dimension_type=EvidenceDimensionType.WALK_FORWARD_FOLD,
                dimension_key="fold_summary",
                partition_identity="walk_forward",
                sample_count=0,
                effect_size=0.0,
                raw_p_value=1.0,
                statistic_value=0.0,
                context_metadata={"num_folds": num_folds, "min_folds": policy.stage_c_min_folds},
            )
            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.INSUFFICIENT_EVIDENCE,
                reason_code=ReasonCode.SAMPLE_TOO_SMALL,
                evidence_ids=(ev.evidence_id,),
                policy_hash=policy.policy_hash,
                explanation=f"Number of valid folds ({num_folds}) below minimum required ({policy.stage_c_min_folds})",
            )

        # Compute fold effect sizes and evidence records
        fold_effects: list[float] = []
        evidence_ids: list[str] = []

        expected_dir = np.sign(discovery_effect) if discovery_effect != 0.0 else 1.0

        for idx, (c_arr, b_arr) in enumerate(folds):
            c_clean = np.asarray(c_arr, dtype=np.float64)
            b_clean = np.asarray(b_arr, dtype=np.float64)
            c_clean = c_clean[np.isfinite(c_clean)]
            b_clean = b_clean[np.isfinite(b_clean)]

            n_fold = len(c_clean)
            if n_fold < 2 or len(b_clean) < 2:
                f_effect = 0.0
                stat_val, raw_p = 0.0, 1.0
            else:
                f_effect = calculate_effect_size(c_clean, b_clean, method="cohens_d")
                stat_val, raw_p = run_statistical_test(c_clean, b_clean, test_type="welch_ttest")

            fold_effects.append(f_effect)

            ev = self.create_evidence_record(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                dimension_type=EvidenceDimensionType.WALK_FORWARD_FOLD,
                dimension_key=f"fold_{idx+1}",
                partition_identity=f"fold_{idx+1}",
                sample_count=n_fold,
                effect_size=f_effect,
                raw_p_value=raw_p,
                statistic_value=stat_val,
                context_metadata={"fold_index": idx + 1},
            )
            evidence_ids.append(ev.evidence_id)

        # 2. Directional Fold Consistency Ratio Gate
        consistent_count = sum(
            1 for eff in fold_effects if (np.sign(eff) == expected_dir or (discovery_effect == 0.0 and eff >= 0))
        )
        positive_ratio = float(consistent_count / num_folds)

        # 3. Fold Coefficient of Variation Gate
        mean_eff = float(np.mean(fold_effects))
        std_eff = float(np.std(fold_effects, ddof=1)) if num_folds > 1 else 0.0

        if abs(mean_eff) < 1e-9:
            fold_cv = float("inf") if std_eff > 0 else 0.0
        else:
            fold_cv = float(std_eff / abs(mean_eff))

        if positive_ratio < policy.stage_c_min_positive_ratio:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.TEMPORAL_INSTABILITY
            explanation = (
                f"Directionally consistent fold ratio ({positive_ratio:.4f}) below minimum threshold ({policy.stage_c_min_positive_ratio:.4f})"
            )
        elif fold_cv > policy.stage_c_max_fold_cv:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.TEMPORAL_INSTABILITY
            explanation = (
                f"Fold coefficient of variation ({fold_cv:.4f}) exceeds maximum threshold ({policy.stage_c_max_fold_cv:.4f})"
            )
        else:
            decision = StageDecision.PASS
            reason_code = ReasonCode.PASSED
            explanation = (
                f"Stage C temporal stability passed (folds={num_folds}, positive_ratio={positive_ratio:.4f}, CV={fold_cv:.4f})"
            )

        return StageResult(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            stage=self.stage,
            decision=decision,
            reason_code=reason_code,
            evidence_ids=tuple(evidence_ids),
            policy_hash=policy.policy_hash,
            explanation=explanation,
        )
