"""
Project GOAT v0.7 — Scientific Hypothesis Validation Engine Package

Foundational v0.7 domain models, enums, statistical scoring, rule engine,
evidence collection, deterministic scientific identity layer, reporting,
and persistence backend for the Scientific Hypothesis Validation Engine.
"""

from __future__ import annotations

# Core
from goat.validation.core.context import ValidationContext
from goat.validation.core.enums import DecisionType, ValidationState
from goat.validation.core.hypothesis import (
    ScientificHypothesis,
    compute_hypothesis_fingerprint,
    compute_hypothesis_id,
)
from goat.validation.core.run import (
    ValidationRun,
    compute_run_fingerprint,
    compute_run_id,
)

# Evidence
from goat.validation.evidence.aggregator import EvidenceAggregator
from goat.validation.evidence.collector import EvidenceCollector
from goat.validation.evidence.models import ValidationEvidence, compute_evidence_id

# Statistics
from goat.validation.statistics.calculator import StatisticalCalculator
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

# Decisions
from goat.validation.decisions.generator import DecisionGenerator
from goat.validation.decisions.models import ValidationDecision, compute_decision_id
from goat.validation.decisions.rules import ValidationRuleEngine, ValidationThresholds

# Reporting
from goat.validation.reporting.generator import (
    generate_audit_report,
    generate_evidence_report,
    generate_statistics_report,
    generate_validation_report,
    generate_validation_summary,
    render_validation_markdown,
    serialize_validation_to_json,
)
from goat.validation.reporting.models import (
    ValidationAuditReport,
    ValidationEvidenceReport,
    ValidationReport,
    ValidationStatisticsReport,
    ValidationSummary,
)

# Persistence
from goat.validation.persistence.sqlite import (
    VALIDATION_SCHEMA_VERSION,
    SQLiteValidationRepository,
)

# Engine
from goat.validation.engine import (
    ScientificHypothesisValidationEngine,
    ValidationEngineError,
)

__all__ = [
    # Core — Enums
    "ValidationState",
    "DecisionType",
    # Core — Models
    "ScientificHypothesis",
    "compute_hypothesis_fingerprint",
    "compute_hypothesis_id",
    "ValidationRun",
    "compute_run_fingerprint",
    "compute_run_id",
    "ValidationContext",
    # Evidence
    "ValidationEvidence",
    "compute_evidence_id",
    "EvidenceCollector",
    "EvidenceAggregator",
    # Statistics
    "ValidationScores",
    "compute_confidence_score",
    "compute_evidence_score",
    "compute_agreement_score",
    "compute_reproducibility_score",
    "compute_robustness_score",
    "compute_stability_score",
    "compute_validation_score",
    "compute_overall_confidence",
    "StatisticalCalculator",
    # Decisions
    "ValidationDecision",
    "compute_decision_id",
    "ValidationThresholds",
    "ValidationRuleEngine",
    "DecisionGenerator",
    # Reporting
    "ValidationReport",
    "ValidationSummary",
    "ValidationAuditReport",
    "ValidationEvidenceReport",
    "ValidationStatisticsReport",
    "generate_validation_report",
    "generate_validation_summary",
    "generate_audit_report",
    "generate_evidence_report",
    "generate_statistics_report",
    "render_validation_markdown",
    "serialize_validation_to_json",
    # Persistence
    "VALIDATION_SCHEMA_VERSION",
    "SQLiteValidationRepository",
    # Engine
    "ScientificHypothesisValidationEngine",
    "ValidationEngineError",
]
