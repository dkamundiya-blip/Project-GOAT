"""
Project GOAT v0.7 — Validation Decision Generator

Generates deterministic ValidationDecision from scores and rule evaluation results.
"""

from __future__ import annotations

import datetime

from goat.validation.core.enums import DecisionType
from goat.validation.decisions.models import ValidationDecision, compute_decision_id
from goat.validation.statistics.scores import ValidationScores


class DecisionGenerator:
    """Generates deterministic ValidationDecision instances from rule evaluation results."""

    def generate_decision(
        self,
        validation_run_id: str,
        scores: ValidationScores,
        rule_result: dict,
        evidence_ids: list[str],
    ) -> ValidationDecision:
        """Generate a deterministic ValidationDecision.

        Args:
            validation_run_id: Parent Validation Run ID (VRN_<HEX16>).
            scores: Computed ValidationScores.
            rule_result: Rule engine evaluation result dict.
            evidence_ids: Evidence IDs used in validation.

        Returns:
            Immutable ValidationDecision.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        decision_type: DecisionType = rule_result["decision_type"]

        decision_id, decision_hash = compute_decision_id(
            validation_run_id=validation_run_id,
            decision_type=decision_type.value,
            timestamp=timestamp,
        )

        statistical_summary = {
            "confidence_score": scores.confidence_score,
            "evidence_score": scores.evidence_score,
            "agreement_score": scores.agreement_score,
            "reproducibility_score": scores.reproducibility_score,
            "robustness_score": scores.robustness_score,
            "stability_score": scores.stability_score,
            "validation_score": scores.validation_score,
            "overall_confidence": scores.overall_confidence,
        }

        return ValidationDecision(
            decision_id=decision_id,
            decision_hash=decision_hash,
            validation_run_id=validation_run_id,
            decision_type=decision_type,
            reasoning=rule_result.get("reasoning", ""),
            evidence_used=sorted(evidence_ids),
            statistical_summary=statistical_summary,
            threshold_results=rule_result.get("threshold_results", {}),
            confidence=scores.overall_confidence,
            timestamp=timestamp,
        )
