"""
Project GOAT v0.7 — Validation Rule Engine

Deterministic rule evaluation engine for scientific hypothesis validation.
Supports configurable thresholds with fail-closed evaluation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.validation.core.enums import DecisionType
from goat.validation.statistics.scores import ValidationScores


class ValidationThresholds(BaseModel):
    """Immutable configuration for validation decision thresholds."""

    min_evidence_count: int = Field(default=3, ge=1, description="Minimum required evidence count")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence score")
    min_reproducibility: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum reproducibility score")
    min_agreement: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum agreement score")
    min_robustness: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum robustness score")
    min_execution_quality: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum execution quality score")
    acceptance_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Overall confidence for acceptance")
    rejection_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Overall confidence below which to reject")

    class Config:
        frozen = True
        extra = "forbid"


class ValidationRuleEngine:
    """Deterministic rule engine evaluating validation scores against configurable thresholds.

    No ML, no Bayesian methods, no probabilistic logic. Pure deterministic rule evaluation.
    """

    def __init__(self, thresholds: ValidationThresholds | None = None) -> None:
        self._thresholds = thresholds or ValidationThresholds()

    @property
    def thresholds(self) -> ValidationThresholds:
        """Active threshold configuration."""
        return self._thresholds

    def evaluate(
        self,
        scores: ValidationScores,
        evidence_count: int,
        evidence_summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate validation scores against thresholds and determine decision type.

        Args:
            scores: Computed ValidationScores.
            evidence_count: Total evidence count.
            evidence_summary: Optional evidence summary dict.

        Returns:
            Dictionary with 'decision_type', 'reasoning', 'threshold_results',
            'passed_count', 'total_thresholds'.
        """
        t = self._thresholds
        results: dict[str, dict[str, Any]] = {}

        # Evaluate each threshold
        results["evidence_count"] = {
            "passed": evidence_count >= t.min_evidence_count,
            "actual": evidence_count,
            "threshold": t.min_evidence_count,
        }
        results["confidence"] = {
            "passed": scores.confidence_score >= t.min_confidence,
            "actual": scores.confidence_score,
            "threshold": t.min_confidence,
        }
        results["reproducibility"] = {
            "passed": scores.reproducibility_score >= t.min_reproducibility,
            "actual": scores.reproducibility_score,
            "threshold": t.min_reproducibility,
        }
        results["agreement"] = {
            "passed": scores.agreement_score >= t.min_agreement,
            "actual": scores.agreement_score,
            "threshold": t.min_agreement,
        }
        results["robustness"] = {
            "passed": scores.robustness_score >= t.min_robustness,
            "actual": scores.robustness_score,
            "threshold": t.min_robustness,
        }

        # Execution quality uses weighted_confidence from evidence summary
        weighted_conf = 0.0
        if evidence_summary:
            overall = evidence_summary.get("overall", evidence_summary)
            weighted_conf = overall.get("weighted_confidence", 0.0)
        results["execution_quality"] = {
            "passed": weighted_conf >= t.min_execution_quality,
            "actual": weighted_conf,
            "threshold": t.min_execution_quality,
        }

        passed = sum(1 for r in results.values() if r["passed"])
        total = len(results)

        # Determine decision type
        decision_type, reasoning = self._determine_decision(
            scores=scores,
            evidence_count=evidence_count,
            passed_count=passed,
            total_thresholds=total,
            threshold_results=results,
        )

        return {
            "decision_type": decision_type,
            "reasoning": reasoning,
            "threshold_results": results,
            "passed_count": passed,
            "total_thresholds": total,
        }

    def _determine_decision(
        self,
        scores: ValidationScores,
        evidence_count: int,
        passed_count: int,
        total_thresholds: int,
        threshold_results: dict[str, Any],
    ) -> tuple[DecisionType, str]:
        """Determine decision type from scores and threshold pass results.

        Returns:
            Tuple of (DecisionType, reasoning_string).
        """
        t = self._thresholds

        # Invalid hypothesis: zero evidence
        if evidence_count == 0:
            return (
                DecisionType.INVALID_HYPOTHESIS,
                "No evidence provided for validation",
            )

        # Needs more data: insufficient evidence count
        if evidence_count < t.min_evidence_count:
            return (
                DecisionType.NEEDS_MORE_DATA,
                f"Insufficient evidence count ({evidence_count} < {t.min_evidence_count})",
            )

        # Accepted: overall confidence above acceptance threshold and majority thresholds pass
        if (
            scores.overall_confidence >= t.acceptance_threshold
            and passed_count >= (total_thresholds * 2 // 3)
        ):
            return (
                DecisionType.ACCEPTED,
                f"Overall confidence {scores.overall_confidence:.4f} >= {t.acceptance_threshold} "
                f"with {passed_count}/{total_thresholds} thresholds passed",
            )

        # Rejected: overall confidence below rejection threshold
        if scores.overall_confidence < t.rejection_threshold:
            return (
                DecisionType.REJECTED,
                f"Overall confidence {scores.overall_confidence:.4f} < {t.rejection_threshold} "
                f"with {passed_count}/{total_thresholds} thresholds passed",
            )

        # Inconclusive: in between
        return (
            DecisionType.INCONCLUSIVE,
            f"Overall confidence {scores.overall_confidence:.4f} between "
            f"rejection ({t.rejection_threshold}) and acceptance ({t.acceptance_threshold}) "
            f"with {passed_count}/{total_thresholds} thresholds passed",
        )
