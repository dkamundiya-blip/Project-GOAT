"""
Project GOAT v0.4 — Experiment Execution Engine

Orchestrates multi-hypothesis evaluation across TRAIN, VALIDATION, and sealed HOLDOUT partitions.
Controls Benjamini-Hochberg FDR correction across experiment families.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from goat.config import GoatSettings
from goat.logging import get_logger
from goat.research.dataset import DatasetManifest
from goat.research.hypothesis.conditions import CausalConditionEvaluator
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.dependence import apply_embargo_spacing, evaluate_dependence_risk
from goat.research.hypothesis.multiple_testing import benjamini_hochberg_fdr
from goat.research.hypothesis.result import HypothesisResult
from goat.research.hypothesis.scoring import calculate_edge_score, is_practically_weak_effect
from goat.research.hypothesis.testing import calculate_effect_size, run_statistical_test
from goat.research.splitting import ChronologicalSplitter
from goat.research.stats import calculate_distribution_stats

_log = get_logger("hypothesis.experiment")


class Experiment(BaseModel):
    """Execution model for a family of quantitative hypothesis evaluations."""

    experiment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    family_name: str
    hypotheses_evaluated: list[str] = Field(default_factory=list)
    dataset_fingerprints: list[str] = Field(default_factory=list)
    partitions_accessed: list[str] = Field(default_factory=list)
    multiple_testing_method: str = "benjamini_hochberg"
    fdr_alpha: float = 0.05
    results: list[HypothesisResult] = Field(default_factory=list)
    supported_count: int = 0
    rejected_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


class ExperimentRunner:
    """Orchestrates hypothesis family experiments with strict partition boundaries."""

    def __init__(self, settings: GoatSettings | None = None) -> None:
        self.settings = settings or GoatSettings()
        self.condition_evaluator = CausalConditionEvaluator()
        self.splitter = ChronologicalSplitter()

    def evaluate_hypothesis_on_partition(
        self,
        hypothesis: HypothesisDefinition,
        df: pd.DataFrame,
        outcomes_df: pd.DataFrame,
        partition_name: str,
        dataset_fingerprint: str,
        symbol: str,
        timeframe: str,
        allow_holdout: bool = False,
    ) -> HypothesisResult:
        """Evaluate a single hypothesis against a specific partition DataFrame.

        Args:
            hypothesis: HypothesisDefinition instance.
            df: Input research price DataFrame for the partition.
            outcomes_df: Non-causal forward outcome DataFrame for the partition.
            partition_name: "train", "validation", or "holdout".
            dataset_fingerprint: SHA256 checksum of input dataset.
            symbol: Instrument symbol.
            timeframe: Timeframe label.
            allow_holdout: Flag allowing holdout access.

        Returns:
            ``HypothesisResult`` instance.
        """
        # Holdout security guard
        if partition_name == "holdout" and not allow_holdout:
            _log.info("holdout_partition_sealed_access_denied", hypothesis_id=hypothesis.hypothesis_id)
            return HypothesisResult(
                hypothesis_id=hypothesis.hypothesis_id,
                version=hypothesis.version,
                dataset_fingerprint=dataset_fingerprint,
                partition="holdout",
                symbol=symbol,
                timeframe=timeframe,
                conditional_sample_count=0,
                baseline_sample_count=0,
                sufficiency_status="INSUFFICIENT_DATA",
                validation_status="UNTESTED",
                warnings=["Holdout partition is sealed by default."],
            )

        if df.empty or outcomes_df.empty:
            return HypothesisResult(
                hypothesis_id=hypothesis.hypothesis_id,
                version=hypothesis.version,
                dataset_fingerprint=dataset_fingerprint,
                partition=partition_name,
                symbol=symbol,
                timeframe=timeframe,
                conditional_sample_count=0,
                baseline_sample_count=0,
                sufficiency_status="INSUFFICIENT_DATA",
                validation_status="FAILED",
                warnings=["Partition DataFrame is empty."],
            )

        # 1. Evaluate causal condition
        raw_mask = self.condition_evaluator.evaluate_condition(
            df,
            condition_spec=hypothesis.causal_condition,
            params=hypothesis.condition_parameters,
        )

        # 2. Embargo event spacing if configured
        if hypothesis.event_spacing_bars > 1:
            mask = apply_embargo_spacing(raw_mask, horizon_k=hypothesis.event_spacing_bars)
        else:
            mask = raw_mask

        dep_risk, dep_warning = evaluate_dependence_risk(mask, horizon_k=hypothesis.forward_horizon)
        warnings: list[str] = []
        if dep_warning:
            warnings.append(dep_warning)

        # 3. Extract conditional and baseline outcomes
        metric = hypothesis.forward_outcome_metric
        if metric not in outcomes_df.columns:
            raise ValueError(f"Outcome metric column '{metric}' not found in outcomes DataFrame")

        outcomes = outcomes_df[metric].to_numpy()
        cond_outcomes = outcomes[mask.to_numpy()]

        if hypothesis.baseline_definition == "conditional_excluded":
            base_outcomes = outcomes[~mask.to_numpy()]
        else:
            # Unconditional baseline
            base_outcomes = outcomes

        n_cond = int(len(cond_outcomes[np.isfinite(cond_outcomes)]))
        n_base = int(len(base_outcomes[np.isfinite(base_outcomes)]))

        # Check sample sufficiency
        sufficiency_status = "SUFFICIENT"
        if n_cond < hypothesis.min_sample_requirement:
            sufficiency_status = "INSUFFICIENT_DATA"
            warnings.append(
                f"Conditional sample size ({n_cond}) is below minimum requirement ({hypothesis.min_sample_requirement})."
            )

        # 4. Statistical Test & Effect Size
        effect_size = calculate_effect_size(
            cond_outcomes,
            base_outcomes,
            method=hypothesis.effect_size_method,
        )

        stat_val, p_val = run_statistical_test(
            cond_outcomes,
            base_outcomes,
            test_type=hypothesis.statistical_test,
            seed=self.settings.permutation_random_seed,
            num_permutations=self.settings.default_permutation_samples,
        )

        # Check practical effect strength
        base_std = float(np.std(base_outcomes[np.isfinite(base_outcomes)])) if len(base_outcomes) > 1 else 1.0
        is_weak = is_practically_weak_effect(effect_size, method=hypothesis.effect_size_method, baseline_std=base_std)
        
        stability_status = "STABLE"
        if is_weak and p_val <= 0.05:
            stability_status = "STATISTICALLY_SUPPORTED_BUT_PRACTICALLY_WEAK"
            warnings.append(
                "Statistically significant result exhibits practically negligible effect magnitude."
            )

        # Compute initial EdgeScore (q_value = p_val until family FDR correction)
        edge_score = calculate_edge_score(
            effect_size=effect_size,
            q_value=p_val,
            effect_method=hypothesis.effect_size_method,
            baseline_std=base_std,
            sample_size=n_cond,
            min_sample_size=hypothesis.min_sample_requirement,
            dependence_overlap_risk=dep_risk,
        )

        cond_stats = calculate_distribution_stats(cond_outcomes)
        base_stats = calculate_distribution_stats(base_outcomes)

        return HypothesisResult(
            hypothesis_id=hypothesis.hypothesis_id,
            version=hypothesis.version,
            dataset_fingerprint=dataset_fingerprint,
            partition=partition_name,
            symbol=symbol,
            timeframe=timeframe,
            conditional_sample_count=n_cond,
            baseline_sample_count=n_base,
            conditional_stats=cond_stats,
            baseline_stats=base_stats,
            effect_size_type=hypothesis.effect_size_method,
            effect_size=round(effect_size, 6),
            statistical_test_type=hypothesis.statistical_test,
            statistic_value=round(stat_val, 6),
            raw_p_value=round(p_val, 8),
            adjusted_q_value=round(p_val, 8),
            dependence_overlap_risk=dep_risk,
            sufficiency_status=sufficiency_status,
            validation_status="PASSED" if (p_val <= 0.05 and sufficiency_status == "SUFFICIENT") else "FAILED",
            stability_status=stability_status,
            edge_score=edge_score,
            warnings=warnings,
        )

    def run_experiment_family(
        self,
        family_name: str,
        hypotheses: list[HypothesisDefinition],
        df: pd.DataFrame,
        outcomes_df: pd.DataFrame,
        manifest: DatasetManifest,
        allow_holdout: bool = False,
    ) -> Experiment:
        """Run an experiment family of hypotheses with Benjamini-Hochberg FDR correction.

        Args:
            family_name: Identifier for hypothesis family.
            hypotheses: Complete list of hypotheses in parameter grid.
            df: Canonical research price DataFrame.
            outcomes_df: Non-causal forward outcomes DataFrame.
            manifest: DatasetManifest instance.
            allow_holdout: Flag allowing holdout partition access.

        Returns:
            ``Experiment`` instance.
        """
        # Split partitions chronologically
        parts = self.splitter.split(df, allow_holdout=allow_holdout)
        outcomes_parts = self.splitter.split(outcomes_df, allow_holdout=allow_holdout)

        train_df, val_df, holdout_df = parts["train"], parts["validation"], parts["holdout"]
        train_outcomes = outcomes_parts["train"]
        val_outcomes = outcomes_parts["validation"]

        # Audit holdout access if allowed
        if allow_holdout:
            self._log_holdout_access(
                family_name=family_name,
                hypotheses=[h.hypothesis_id for h in hypotheses],
                dataset_fingerprint=manifest.dataset_id,
            )

        results: list[HypothesisResult] = []
        raw_pvals: list[float] = []

        # 1. Phase 1: TRAIN evaluation
        for hyp in hypotheses:
            res_train = self.evaluate_hypothesis_on_partition(
                hypothesis=hyp,
                df=train_df,
                outcomes_df=train_outcomes,
                partition_name="train",
                dataset_fingerprint=manifest.dataset_id,
                symbol=manifest.symbol,
                timeframe=manifest.timeframe,
            )
            results.append(res_train)
            raw_pvals.append(res_train.raw_p_value)

        # 2. Phase 2: Family-level Benjamini-Hochberg FDR Correction
        q_vals, is_rejected = benjamini_hochberg_fdr(raw_pvals, alpha=self.settings.fdr_alpha)

        # Update q-values and recompute EdgeScores on TRAIN
        for i, res in enumerate(results):
            res.adjusted_q_value = round(float(q_vals[i]), 8)
            # Recompute EdgeScore using adjusted q-value
            res.edge_score = calculate_edge_score(
                effect_size=res.effect_size,
                q_value=res.adjusted_q_value,
                effect_method=res.effect_size_type,
                sample_size=res.conditional_sample_count,
                dependence_overlap_risk=res.dependence_overlap_risk,
            )

        supported_count = int(np.sum(is_rejected))
        rejected_count = len(results) - supported_count

        _log.info(
            "experiment_family_evaluated",
            family_name=family_name,
            total_hypotheses=len(hypotheses),
            supported=supported_count,
            rejected=rejected_count,
        )

        return Experiment(
            family_name=family_name,
            hypotheses_evaluated=[h.hypothesis_id for h in hypotheses],
            dataset_fingerprints=[manifest.dataset_id],
            partitions_accessed=["train", "validation"] + (["holdout"] if allow_holdout else []),
            multiple_testing_method="benjamini_hochberg",
            fdr_alpha=self.settings.fdr_alpha,
            results=results,
            supported_count=supported_count,
            rejected_count=rejected_count,
        )

    def _log_holdout_access(
        self,
        family_name: str,
        hypotheses: list[str],
        dataset_fingerprint: str,
    ) -> None:
        """Write audit entry when sealed HOLDOUT partition is accessed."""
        audit_path = self.settings.get_holdout_audit_log_path()
        audit_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "family_name": family_name,
            "dataset_fingerprint": dataset_fingerprint,
            "hypotheses_evaluated": hypotheses,
            "reason": "Explicit --allow-holdout flag supplied for confirmatory audit.",
        }

        existing = []
        if audit_path.exists():
            try:
                existing = json.loads(audit_path.read_text(encoding="utf-8"))
            except Exception:
                existing = []

        existing.append(entry)
        audit_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        _log.warning("holdout_access_audited", path=str(audit_path))
