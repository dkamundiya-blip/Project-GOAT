"""
Project GOAT v0.9 — Statistical Evaluation Subsystem Public API
"""

from goat.statistics.confidence.engine import ConfidenceAssessmentEngine
from goat.statistics.core.canonical import (
    compute_canonical_sha256,
    compute_confidence_id,
    compute_decision_id,
    compute_expectancy_id,
    compute_significance_id,
    compute_statistical_evaluation_id,
    compute_summary_id,
    serialize_canonical_json,
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
from goat.statistics.engine import MasterStatisticalEngine
from goat.statistics.evaluation.engine import StatisticalEvaluationEngine
from goat.statistics.expectancy.engine import ExpectancyAssessmentEngine
from goat.statistics.persistence.sqlite import (
    ConfidenceRepository,
    DecisionRepository,
    ExpectancyRepository,
    SignificanceRepository,
    StatisticalPersistenceContext,
    StatisticalRepository,
    SummaryRepository,
    init_statistics_db,
)
from goat.statistics.reporting.reports import (
    generate_confidence_report,
    generate_executive_report,
    generate_expectancy_report,
    generate_json_report,
    generate_significance_report,
    generate_statistical_report,
)
from goat.statistics.significance.engine import SignificanceAssessmentEngine

__all__ = [
    "ConfidenceAssessment",
    "ConfidenceAssessmentEngine",
    "ConfidenceRepository",
    "DecisionRepository",
    "EvaluationConfidence",
    "EvaluationDecision",
    "EvaluationStatus",
    "EvaluationSummary",
    "ExpectancyAssessment",
    "ExpectancyAssessmentEngine",
    "ExpectancyRepository",
    "MasterStatisticalEngine",
    "ScientificDecision",
    "SignificanceAssessment",
    "SignificanceAssessmentEngine",
    "SignificanceRepository",
    "StatisticalEvaluation",
    "StatisticalEvaluationEngine",
    "StatisticalPersistenceContext",
    "StatisticalRepository",
    "SummaryRepository",
    "compute_canonical_sha256",
    "compute_confidence_id",
    "compute_decision_id",
    "compute_expectancy_id",
    "compute_significance_id",
    "compute_statistical_evaluation_id",
    "compute_summary_id",
    "generate_confidence_report",
    "generate_executive_report",
    "generate_expectancy_report",
    "generate_json_report",
    "generate_significance_report",
    "generate_statistical_report",
    "init_statistics_db",
    "serialize_canonical_json",
]
