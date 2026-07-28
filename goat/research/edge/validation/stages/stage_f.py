"""
Project GOAT v0.6 — Stage F: Cross-Context Replication Validator

Evaluates whether a candidate edge replicates across a pre-registered universe of independent contexts
without context cherry-picking, parameter optimization, or post-hoc denominator manipulation.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from goat.research.edge.canonical import canonical_json
from goat.research.edge.definition import CandidateEdge
from goat.research.edge.enums import MetaAnalysisMethod
from goat.research.edge.evidence import EvidenceDimensionType
from goat.research.edge.models import ValidationContextUniverse, ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.exceptions import StageValidationError
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.base import BaseStageValidator


class StageFValidator(BaseStageValidator):
    """Validator for Stage F: Cross-Context Replication."""

    @property
    def stage(self) -> ValidationStage:
        return ValidationStage.STAGE_F_REPLICATION

    @property
    def prerequisite_stage(self) -> ValidationStage | None:
        return ValidationStage.STAGE_E_FALSIFICATION

    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        stage_e_result: StageResult | None = None,
        baseline_effect: float = 0.0,
        context_evaluations: Sequence[tuple[str, float, float, int]] | None = None,
        context_universe: ValidationContextUniverse | Sequence[str] | None = None,
        **kwargs: Any,
    ) -> StageResult:
        """Evaluate Stage F cross-context replication contract against pre-registered context universe.

        Args:
            candidate_edge: CandidateEdge under evaluation.
            hypothesis_version: Frozen hypothesis version string.
            policy: ValidationPolicy thresholds and meta_analysis_method.
            validation_run: ValidationRunInfo metadata.
            dataset_partitions: Dict containing validation research partition.
            stage_e_result: StageResult from Stage E (must be PASS).
            baseline_effect: Baseline effect size observed during Stage A/B.
            context_evaluations: Sequence of (context_key, effect_size, raw_p_value, sample_count) tuples.
            context_universe: Pre-registered ValidationContextUniverse or sequence of mandatory context keys.

        Returns:
            StageResult containing PASS/FAIL/INSUFFICIENT_EVIDENCE decision and evidence.

        Raises:
            StageValidationError: If context universe is missing, duplicate, mismatched, or unmanifested.
        """
        # Precondition Guard: Stage E must have passed
        if stage_e_result is not None and stage_e_result.decision != StageDecision.PASS:
            return StageResult(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                stage=self.stage,
                decision=StageDecision.FAIL,
                reason_code=ReasonCode.PREREQUISITE_FAILED,
                policy_hash=policy.policy_hash,
                explanation=f"Stage F blocked: Stage E prerequisite failed with decision '{stage_e_result.decision.value}'",
            )

        if not context_evaluations:
            ev = self.create_evidence_record(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                dimension_type=EvidenceDimensionType.REPLICATION,
                dimension_key="replication_summary",
                partition_identity="cross_context",
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
                reason_code=ReasonCode.INSUFFICIENT_CONTEXTS,
                evidence_ids=(ev.evidence_id,),
                policy_hash=policy.policy_hash,
                explanation="No replication context evaluations provided",
            )

        # Extract pre-registered expected universe
        expected_keys: set[str] = set()
        universe_id = ""

        if isinstance(context_universe, ValidationContextUniverse):
            expected_keys = {str(k).strip() for k in context_universe.contexts}
            universe_id = context_universe.universe_id
        elif context_universe is not None:
            expected_keys = {str(k).strip() for k in context_universe if str(k).strip()}

        # Strict duplicate context detection & universe validation
        seen_keys: set[str] = set()
        clean_evals: list[tuple[str, float, float, int]] = []

        for item in context_evaluations:
            ckey = str(item[0]).strip()
            eff = float(item[1])
            pval = float(item[2])
            n_samp = int(item[3])

            if ckey in seen_keys:
                raise StageValidationError(
                    f"Duplicate context key '{ckey}' detected in Stage F evaluation. "
                    "Context identity collisions and duplicate key manipulation are strictly prohibited."
                )

            seen_keys.add(ckey)
            clean_evals.append((ckey, eff, pval, n_samp))

        # Check exact universe membership equality if expected universe is bound
        if expected_keys and seen_keys != expected_keys:
            missing = expected_keys - seen_keys
            extra = seen_keys - expected_keys
            raise StageValidationError(
                f"Context universe mismatch in Stage F evaluation. "
                f"Missing expected contexts: {sorted(missing)}, Unexpected extra contexts: {sorted(extra)}."
            )

        # Sort contexts deterministically by context_key
        clean_evals.sort(key=lambda x: x[0])
        total_contexts = len(clean_evals)

        expected_dir = np.sign(baseline_effect) if baseline_effect != 0.0 else 1.0
        success_count = 0
        p_values: list[float] = []
        evidence_ids: list[str] = []

        for ckey, eff, pval, n_samp in clean_evals:
            # Validate numeric inputs
            if not (np.isfinite(eff) and np.isfinite(pval)):
                raise StageValidationError(
                    f"Non-finite evaluation metric (effect={eff}, pval={pval}) in context '{ckey}'."
                )

            pval_clipped = max(1e-15, min(1.0, pval))
            p_values.append(pval_clipped)

            is_succ = (
                (np.sign(eff) == expected_dir)
                and (pval <= policy.stage_a_alpha)
                and (abs(eff) >= policy.stage_a_effect_min)
            )

            if is_succ:
                success_count += 1

            ev = self.create_evidence_record(
                validation_run_id=validation_run.validation_run_id,
                edge_id=candidate_edge.edge_id,
                dimension_type=EvidenceDimensionType.REPLICATION,
                dimension_key=f"context_{ckey}",
                partition_identity="cross_context",
                sample_count=n_samp,
                effect_size=eff,
                raw_p_value=pval_clipped,
                statistic_value=0.0,
                context_metadata={
                    "context_key": ckey,
                    "universe_id": universe_id,
                    "baseline_effect": baseline_effect,
                    "is_replication_success": is_succ,
                },
            )
            evidence_ids.append(ev.evidence_id)

        replication_ratio = float(success_count / total_contexts)

        # Meta-Analysis p-value combination according to policy.meta_analysis_method
        if len(p_values) == 1:
            p_meta = p_values[0]
        else:
            if policy.meta_analysis_method == MetaAnalysisMethod.STOUFFER_Z_SCORE:
                chi2_stat, p_meta = stats.combine_pvalues(p_values, method="stouffer")
            else:
                # Default: FISHER_COMBINED_PROBABILITY
                chi2_stat, p_meta = stats.combine_pvalues(p_values, method="fisher")
            p_meta = float(p_meta)

        # Decision Precedence
        if replication_ratio < policy.stage_f_min_replication_pct:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.REPLICATION_FAILED
            explanation = (
                f"Replication ratio ({replication_ratio:.4f}) below minimum threshold ({policy.stage_f_min_replication_pct:.4f})"
            )
        elif p_meta > policy.stage_f_meta_alpha:
            decision = StageDecision.FAIL
            reason_code = ReasonCode.SIGNIFICANCE_FAILED
            explanation = (
                f"Meta-analysis p-value ({p_meta:.6f}) exceeds meta alpha threshold ({policy.stage_f_meta_alpha:.4f})"
            )
        else:
            decision = StageDecision.PASS
            reason_code = ReasonCode.PASSED
            explanation = (
                f"Stage F cross-context replication passed (ratio={replication_ratio:.4f}, p_meta={p_meta:.6f})"
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
