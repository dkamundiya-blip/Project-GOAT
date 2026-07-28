"""
Project GOAT v0.6 — Stage A: Discovery Significance & Multiplicity Validator

Evaluates initial discovery evidence, minimum sample size thresholds, effect size magnitudes,
and Benjamini-Hochberg FDR multiplicity-adjusted statistical significance on training data.
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
from goat.research.edge.validation.multiplicity import MultiplicityFamilyCoordinator
from goat.research.edge.validation.stages.base import BaseStageValidator
from goat.research.hypothesis.testing import calculate_effect_size, run_statistical_test


class StageAValidator(BaseStageValidator):
    """Validator for Stage A: Discovery Significance & Multiplicity."""

    @property
    def stage(self) -> ValidationStage:
        return ValidationStage.STAGE_A_DISCOVERY

    @property
    def prerequisite_stage(self) -> ValidationStage | None:
        return None

    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        multiplicity_coordinator: MultiplicityFamilyCoordinator | None = None,
        cond_arr: np.ndarray | None = None,
        base_arr: np.ndarray | None = None,
        **kwargs: Any,
    ) -> StageResult:
        """Evaluate Stage A discovery significance contract.

        Args:
            candidate_edge: CandidateEdge under evaluation.
            hypothesis_version: Frozen hypothesis version string.
            policy: ValidationPolicy thresholds.
            validation_run: ValidationRunInfo metadata.
            dataset_partitions: Dict containing "train" DataFrame partition.
            multiplicity_coordinator: Optional pre-registered MultiplicityFamilyCoordinator.
            cond_arr: Optional direct array of conditional outcome observations.
            base_arr: Optional direct array of baseline outcome observations.

        Returns:
            StageResult containing PASS/FAIL/INSUFFICIENT_EVIDENCE decision and evidence_ids.
        """
        # Extract observations if not passed directly
        if cond_arr is None or base_arr is None:
            train_df = dataset_partitions.get("train")
            if train_df is None or (isinstance(train_df, pd.DataFrame) and train_df.empty):
                cond_clean = np.array([])
                base_clean = np.array([])
            else:
                # If train_df has 'conditional_outcome' and 'baseline_outcome' columns
                if isinstance(train_df, pd.DataFrame):
                    c_col = train_df.get("conditional_outcome", pd.Series(dtype=float))
                    b_col = train_df.get("baseline_outcome", pd.Series(dtype=float))
                    cond_clean = np.asarray(c_col, dtype=np.float64)
                    base_clean = np.asarray(b_col, dtype=np.float64)
                else:
                    cond_clean = np.array([])
                    base_clean = np.array([])
        else:
            cond_clean = np.asarray(cond_arr, dtype=np.float64)
            base_clean = np.asarray(base_arr, dtype=np.float64)

        cond_clean = cond_clean[np.isfinite(cond_clean)]
        base_clean = base_clean[np.isfinite(base_clean)]

        sample_count = len(cond_clean)

        # 1. Sample Size Gate (Precedence #1)
        if sample_count < policy.stage_a_min_sample:
            effect_size = calculate_effect_size(cond_clean, base_clean, method="cohens_d") if sample_count > 0 else 0.0
            stat_val, raw_p = run_statistical_test(cond_clean, base_clean, test_type="welch_ttest") if sample_count > 1 else (0.0, 1.0)
            adj_q = raw_p

            ev = self.create_evidence_record(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                dimension_type=EvidenceDimensionType.DISCOVERY,
                dimension_key=f"{candidate_edge.causal_primitive}_{candidate_edge.target_feature}",
                partition_identity="train",
                sample_count=sample_count,
                effect_size=effect_size,
                raw_p_value=raw_p,
                adjusted_q_value=adj_q,
                statistic_value=stat_val,
            )

            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.INSUFFICIENT_EVIDENCE,
                reason_code=ReasonCode.SAMPLE_TOO_SMALL,
                evidence_ids=(ev.evidence_id,),
                policy_hash=policy.policy_hash,
                explanation=f"Sample count ({sample_count}) below minimum threshold ({policy.stage_a_min_sample})",
            )

        # Statistical calculations
        effect_size = calculate_effect_size(cond_clean, base_clean, method="cohens_d")
        stat_val, raw_p = run_statistical_test(cond_clean, base_clean, test_type="welch_ttest")

        # Multiplicity FDR correction
        if multiplicity_coordinator is not None:
            if not multiplicity_coordinator.is_frozen:
                multiplicity_coordinator.register_candidate(candidate_edge.edge_id, raw_p)
                multiplicity_coordinator.freeze_family()
            adj_q = multiplicity_coordinator.get_q_value(candidate_edge.edge_id)
        else:
            adj_q = raw_p

        # 2. Effect Size Gate (Precedence #2)
        if abs(effect_size) < policy.stage_a_effect_min:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.EFFECT_TOO_SMALL
            explanation = f"Absolute effect size ({abs(effect_size):.4f}) below minimum threshold ({policy.stage_a_effect_min:.4f})"

        # 3. Multiplicity Significance Gate (Precedence #3)
        elif adj_q > policy.stage_a_alpha:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.SIGNIFICANCE_FAILED
            explanation = f"FDR adjusted q-value ({adj_q:.4f}) exceeds alpha threshold ({policy.stage_a_alpha:.4f})"

        # 4. All Gates Satisfied
        else:
            decision = StageDecision.PASS
            reason_code = ReasonCode.PASSED
            explanation = f"Stage A discovery significance passed (N={sample_count}, d={effect_size:.4f}, q={adj_q:.4f})"

        ev = self.create_evidence_record(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            dimension_type=EvidenceDimensionType.DISCOVERY,
            dimension_key=f"{candidate_edge.causal_primitive}_{candidate_edge.target_feature}",
            partition_identity="train",
            sample_count=sample_count,
            effect_size=effect_size,
            raw_p_value=raw_p,
            adjusted_q_value=adj_q,
            statistic_value=stat_val,
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
