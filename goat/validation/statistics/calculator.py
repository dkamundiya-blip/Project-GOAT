"""
Project GOAT v0.7 — Statistical Calculator

Orchestrates all deterministic score computations for hypothesis validation.
"""

from __future__ import annotations

from typing import Any

from goat.validation.evidence.models import ValidationEvidence
from goat.validation.statistics.scores import (
    ValidationScores,
    compute_agreement_score,
    compute_confidence_score,
    compute_evidence_score,
    compute_overall_confidence,
    compute_reproducibility_score,
    compute_robustness_score,
    compute_stability_score,
    compute_validation_score,
)


class StatisticalCalculator:
    """Orchestrator computing all validation scores deterministically.

    No random sampling. No probabilistic simulation. Pure deterministic computation.
    """

    def calculate_all_scores(
        self,
        evidence_list: list[ValidationEvidence],
        evidence_summary: dict[str, Any],
        thresholds: dict[str, float] | None = None,
        replication_count: int = 0,
        cross_context_count: int = 0,
        consistent_periods: int = 0,
        total_periods: int = 0,
        score_weights: dict[str, float] | None = None,
    ) -> ValidationScores:
        """Calculate all validation scores from evidence and metrics.

        Args:
            evidence_list: List of ValidationEvidence instances.
            evidence_summary: Aggregated evidence summary dict.
            thresholds: Optional threshold configuration for threshold pass counting.
            replication_count: Number of independent replications.
            cross_context_count: Number of independent confirming contexts.
            consistent_periods: Number of temporally consistent periods.
            total_periods: Total temporal periods evaluated.
            score_weights: Optional custom weights for overall confidence.

        Returns:
            Immutable ValidationScores instance.
        """
        overall = evidence_summary.get("overall", evidence_summary)
        total_count = overall.get("total_count", len(evidence_list))
        supporting = overall.get("supporting_count", 0)
        contradicting = overall.get("contradicting_count", 0)
        total_weight = overall.get("total_weight", 0.0)

        # Compute individual scores
        conf = compute_confidence_score(
            total_evidence=total_count,
            validated_count=supporting,
        )
        evid = compute_evidence_score(total_weight=total_weight)
        agree = compute_agreement_score(
            supporting_count=supporting,
            contradicting_count=contradicting,
        )
        repro = compute_reproducibility_score(replication_count=replication_count)
        robust = compute_robustness_score(cross_context_count=cross_context_count)
        stab = compute_stability_score(
            consistent_periods=consistent_periods,
            total_periods=total_periods,
        )

        # Compute threshold pass count
        default_thresholds = thresholds or {
            "min_evidence_count": 3,
            "min_confidence": 0.5,
            "min_reproducibility": 0.3,
            "min_agreement": 0.6,
            "min_robustness": 0.3,
            "min_execution_quality": 0.5,
        }

        passed = 0
        total_thresh = len(default_thresholds)
        if total_count >= default_thresholds.get("min_evidence_count", 3):
            passed += 1
        if conf >= default_thresholds.get("min_confidence", 0.5):
            passed += 1
        if repro >= default_thresholds.get("min_reproducibility", 0.3):
            passed += 1
        if agree >= default_thresholds.get("min_agreement", 0.6):
            passed += 1
        if robust >= default_thresholds.get("min_robustness", 0.3):
            passed += 1
        weighted_conf = overall.get("weighted_confidence", 0.0)
        if weighted_conf >= default_thresholds.get("min_execution_quality", 0.5):
            passed += 1

        val = compute_validation_score(
            thresholds_passed=passed,
            total_thresholds=total_thresh,
        )

        overall_conf = compute_overall_confidence(
            confidence=conf,
            evidence=evid,
            agreement=agree,
            reproducibility=repro,
            robustness=robust,
            stability=stab,
            validation=val,
            weights=score_weights,
        )

        return ValidationScores(
            confidence_score=conf,
            evidence_score=evid,
            agreement_score=agree,
            reproducibility_score=repro,
            robustness_score=robust,
            stability_score=stab,
            validation_score=val,
            overall_confidence=overall_conf,
        )
