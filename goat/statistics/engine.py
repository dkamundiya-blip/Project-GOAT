"""
Project GOAT v0.9 — Master Statistical Evaluation Engine Facade
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.statistics.confidence.engine import ConfidenceAssessmentEngine
from goat.statistics.core.canonical import compute_summary_id
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
from goat.statistics.evaluation.engine import StatisticalEvaluationEngine
from goat.statistics.expectancy.engine import ExpectancyAssessmentEngine
from goat.statistics.persistence.sqlite import StatisticalPersistenceContext
from goat.statistics.reporting.reports import (
    generate_confidence_report,
    generate_executive_report,
    generate_expectancy_report,
    generate_json_report,
    generate_significance_report,
    generate_statistical_report,
)
from goat.statistics.significance.engine import SignificanceAssessmentEngine


class MasterStatisticalEngine:
    """Master Facade Engine orchestrating statistical evaluations, confidence assessments,

    significance hypothesis testing, expectancy analysis, reporting, and optional SQLite persistence.
    """

    def __init__(
        self,
        persistence_context: StatisticalPersistenceContext | None = None,
        evaluation_engine: StatisticalEvaluationEngine | None = None,
        confidence_engine: ConfidenceAssessmentEngine | None = None,
        significance_engine: SignificanceAssessmentEngine | None = None,
        expectancy_engine: ExpectancyAssessmentEngine | None = None,
    ) -> None:
        self._confidence_engine = confidence_engine or ConfidenceAssessmentEngine()
        self._significance_engine = significance_engine or SignificanceAssessmentEngine()
        self._expectancy_engine = expectancy_engine or ExpectancyAssessmentEngine()
        self._evaluation_engine = evaluation_engine or StatisticalEvaluationEngine(
            confidence_engine=self._confidence_engine,
            significance_engine=self._significance_engine,
            expectancy_engine=self._expectancy_engine,
        )
        self._persistence = persistence_context

        # Sync existing database entities if persistence context provided
        if self._persistence:
            for ev in self._persistence.evaluations.list_all():
                self._evaluation_engine._evaluations[ev.evaluation_id] = ev
            for dec in self._persistence.decisions.list_all():
                self._evaluation_engine._decisions[dec.decision_id] = dec

    @property
    def evaluation_engine(self) -> StatisticalEvaluationEngine:
        return self._evaluation_engine

    @property
    def confidence_engine(self) -> ConfidenceAssessmentEngine:
        return self._confidence_engine

    @property
    def significance_engine(self) -> SignificanceAssessmentEngine:
        return self._significance_engine

    @property
    def expectancy_engine(self) -> ExpectancyAssessmentEngine:
        return self._expectancy_engine

    @property
    def persistence(self) -> StatisticalPersistenceContext | None:
        return self._persistence

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
        """Evaluate a completed experiment and persist all statistical findings and decisions."""
        evaluation, decision, conf, sig, exp = self._evaluation_engine.evaluate_experiment(
            experiment_id=experiment_id,
            hypothesis_id=hypothesis_id,
            samples=samples,
            alpha_threshold=alpha_threshold,
            null_mean=null_mean,
            evaluator=evaluator,
            timestamp=timestamp,
            tags=tags,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.evaluations.save(evaluation)
            self._persistence.decisions.save(decision)
            self._persistence.confidence.save(conf)
            self._persistence.significance.save(sig)
            self._persistence.expectancy.save(exp)

        return evaluation, decision, conf, sig, exp

    def generate_summary(self, timestamp: str | None = None) -> EvaluationSummary:
        """Generate and persist an EvaluationSummary snapshot."""
        summary = self._evaluation_engine.generate_summary(timestamp=timestamp)
        if self._persistence:
            self._persistence.summaries.save(summary)
        return summary

    def generate_reports(self, evaluation_id: str) -> dict[str, str]:
        """Generate Markdown and JSON reports for a given evaluation ID."""
        evaluation = self._evaluation_engine.get_evaluation(evaluation_id)
        if not evaluation:
            raise KeyError(f"Evaluation ID '{evaluation_id}' not found.")

        summary = self.generate_summary()
        recent_evals = self._evaluation_engine.list_all_evaluations()[:10]

        reports: dict[str, str] = {
            "statistical": generate_statistical_report(evaluation),
            "executive": generate_executive_report(summary, recent_evals),
            "json": generate_json_report(evaluation),
        }

        for conf in self._confidence_engine.list_all():
            if conf.evaluation_id == evaluation_id:
                reports["confidence"] = generate_confidence_report(conf)
                break
        for sig in self._significance_engine.list_all():
            if sig.evaluation_id == evaluation_id:
                reports["significance"] = generate_significance_report(sig)
                break
        for exp in self._expectancy_engine.list_all():
            if exp.evaluation_id == evaluation_id:
                reports["expectancy"] = generate_expectancy_report(exp)
                break

        if self._persistence:
            if "confidence" not in reports:
                conf_p = self._persistence.confidence.get_by_evaluation_id(evaluation_id)
                if conf_p:
                    reports["confidence"] = generate_confidence_report(conf_p)
            if "significance" not in reports:
                sig_p = self._persistence.significance.get_by_evaluation_id(evaluation_id)
                if sig_p:
                    reports["significance"] = generate_significance_report(sig_p)
            if "expectancy" not in reports:
                exp_p = self._persistence.expectancy.get_by_evaluation_id(evaluation_id)
                if exp_p:
                    reports["expectancy"] = generate_expectancy_report(exp_p)

        return reports
