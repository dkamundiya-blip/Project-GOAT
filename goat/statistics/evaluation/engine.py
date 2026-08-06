"""
Project GOAT v0.9 — Statistical Evaluation Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.statistics.confidence.engine import ConfidenceAssessmentEngine
from goat.statistics.core.canonical import (
    compute_decision_id,
    compute_statistical_evaluation_id,
    compute_summary_id,
)
from goat.statistics.core.enums import (
    EvaluationConfidence,
    EvaluationStatus,
    ScientificDecision,
)
from goat.statistics.core.models import (
    ConfidenceAssessment,
    EvaluationDecision,
    EvaluationSummary,
    ExpectancyAssessment,
    SignificanceAssessment,
    StatisticalEvaluation,
)
from goat.statistics.expectancy.engine import ExpectancyAssessmentEngine
from goat.statistics.significance.engine import SignificanceAssessmentEngine


class StatisticalEvaluationEngine:
    """Statistical Evaluation Engine for producing objective statistical evaluations and decisions

    regarding scientific hypotheses without modifying underlying hypotheses, observations, or experiments.
    """

    def __init__(
        self,
        confidence_engine: ConfidenceAssessmentEngine | None = None,
        significance_engine: SignificanceAssessmentEngine | None = None,
        expectancy_engine: ExpectancyAssessmentEngine | None = None,
    ) -> None:
        self._confidence_engine = confidence_engine or ConfidenceAssessmentEngine()
        self._significance_engine = significance_engine or SignificanceAssessmentEngine()
        self._expectancy_engine = expectancy_engine or ExpectancyAssessmentEngine()

        self._evaluations: dict[str, StatisticalEvaluation] = {}
        self._decisions: dict[str, EvaluationDecision] = {}

    def evaluate_experiment(
        self,
        experiment_id: str,
        hypothesis_id: str,
        samples: Sequence[float],
        alpha_threshold: float = 0.01,
        null_mean: float = 0.0,
        evaluator: str = "STATISTICAL_ENGINE",
        timestamp: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[StatisticalEvaluation, EvaluationDecision, ConfidenceAssessment, SignificanceAssessment, ExpectancyAssessment]:
        """Evaluate a completed experiment and append immutable statistical findings and decision."""
        if not experiment_id or not experiment_id.startswith("EXP_"):
            raise ValueError(f"Experiment ID '{experiment_id}' must start with 'EXP_'.")
        if not hypothesis_id or not hypothesis_id.startswith("HYP_"):
            raise ValueError(f"Hypothesis ID '{hypothesis_id}' must start with 'HYP_'.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        ste_id, canonical_hash = compute_statistical_evaluation_id(
            experiment_id=experiment_id,
            hypothesis_id=hypothesis_id,
            evaluator=evaluator,
        )

        # Run sub-assessments
        conf_assessment = self._confidence_engine.calculate_confidence(
            evaluation_id=ste_id,
            samples=samples,
            timestamp=now_str,
        )

        sig_assessment = self._significance_engine.evaluate_significance(
            evaluation_id=ste_id,
            samples=samples,
            null_hypothesis_mean=null_mean,
            alpha_threshold=alpha_threshold,
            timestamp=now_str,
        )

        exp_assessment = self._expectancy_engine.calculate_expectancy(
            evaluation_id=ste_id,
            returns_or_gains=samples,
            timestamp=now_str,
        )

        # Formulate deterministic scientific decision
        decision = self._derive_scientific_decision(
            sample_size=len(samples),
            p_value=sig_assessment.p_value,
            alpha_threshold=alpha_threshold,
            expected_value=exp_assessment.expected_value,
        )

        rationale = (
            f"Decision '{decision.value}' derived with sample size {len(samples)}, "
            f"p-value {sig_assessment.p_value:.6f} (alpha={alpha_threshold}), "
            f"expected value {exp_assessment.expected_value:.6f}."
        )

        evd_id, evd_hash = compute_decision_id(
            evaluation_id=ste_id,
            decision=decision.value,
            hypothesis_id=hypothesis_id,
        )

        decision_entity = EvaluationDecision(
            decision_id=evd_id,
            evaluation_id=ste_id,
            hypothesis_id=hypothesis_id,
            decision=decision,
            confidence_rating=conf_assessment.confidence_rating,
            decision_rationale=rationale,
            authorizer=evaluator,
            timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=evd_hash,
        )

        evaluation = StatisticalEvaluation(
            evaluation_id=ste_id,
            experiment_id=experiment_id.strip(),
            hypothesis_id=hypothesis_id.strip(),
            status=EvaluationStatus.COMPLETED,
            decision=decision,
            confidence_level=conf_assessment.confidence_level,
            confidence_rating=conf_assessment.confidence_rating,
            p_value=sig_assessment.p_value,
            effect_size=(exp_assessment.expected_value / (abs(conf_assessment.margin_of_error) + 1e-9)),
            expected_value=exp_assessment.expected_value,
            sample_size=len(samples),
            evaluator=evaluator.strip(),
            timestamp=now_str,
            tags=tags or [],
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._evaluations[ste_id] = evaluation
        self._decisions[evd_id] = decision_entity

        return evaluation, decision_entity, conf_assessment, sig_assessment, exp_assessment

    def _derive_scientific_decision(
        self,
        sample_size: int,
        p_value: float,
        alpha_threshold: float,
        expected_value: float,
    ) -> ScientificDecision:
        """Derive objective decision based on statistical rigor rules."""
        if sample_size < 30:
            return ScientificDecision.REQUIRES_MORE_DATA
        if p_value < alpha_threshold and expected_value > 0.0 and sample_size >= 100:
            return ScientificDecision.SUPPORTED
        if p_value >= 0.10 or expected_value < 0.0:
            return ScientificDecision.REJECTED
        return ScientificDecision.INCONCLUSIVE

    def get_evaluation(self, evaluation_id: str) -> StatisticalEvaluation | None:
        """Get evaluation by ID."""
        return self._evaluations.get(evaluation_id)

    def get_decision(self, decision_id: str) -> EvaluationDecision | None:
        """Get decision by ID."""
        return self._decisions.get(decision_id)

    def list_all_evaluations(self) -> list[StatisticalEvaluation]:
        """List all evaluations sorted by timestamp."""
        return sorted(self._evaluations.values(), key=lambda e: e.timestamp)

    def list_all_decisions(self) -> list[EvaluationDecision]:
        """List all decisions sorted by timestamp."""
        return sorted(self._decisions.values(), key=lambda d: d.timestamp)

    def generate_summary(self, timestamp: str | None = None) -> EvaluationSummary:
        """Generate summary snapshot of statistical subsystem."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        total_evals = len(self._evaluations)
        total_decs = len(self._decisions)

        dec_counts: dict[str, int] = {d.value: 0 for d in ScientificDecision}
        conf_counts: dict[str, int] = {c.value: 0 for c in EvaluationConfidence}
        st_counts: dict[str, int] = {s.value: 0 for s in EvaluationStatus}

        for ev in self._evaluations.values():
            dec_counts[ev.decision.value] += 1
            conf_counts[ev.confidence_rating.value] += 1
            st_counts[ev.status.value] += 1

        sum_id, canonical_hash = compute_summary_id(
            total_evaluations=total_evals,
            total_decisions=total_decs,
            timestamp=now_str,
        )

        return EvaluationSummary(
            summary_id=sum_id,
            total_evaluations=total_evals,
            total_decisions=total_decs,
            decision_counts=dec_counts,
            confidence_counts=conf_counts,
            status_counts=st_counts,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )
