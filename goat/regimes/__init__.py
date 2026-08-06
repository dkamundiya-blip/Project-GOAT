"""
Project GOAT v0.7 — Market Regime Engine Package

Public API Exports for Step 6.1 (Phase VI).
"""

from goat.regimes.applicability import EdgeApplicabilityEngine
from goat.regimes.classification import MarketRegimeClassificationEngine
from goat.regimes.core import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    EdgeActivationState,
    LiquidityState,
    MarketRegime,
    ParticipationState,
    RegimeExplainabilityRecord,
    RegimeRule,
    RegimeType,
    StructuralState,
    TrendState,
    VolatilityState,
    compute_assessment_id,
    compute_decision_id,
    compute_regime_explanation_id,
    compute_regime_id,
    compute_regime_report_id,
    compute_rule_id,
    serialize_canonical_json,
)
from goat.regimes.engine import MarketRegimeEngineCoordinator
from goat.regimes.persistence import (
    ApplicabilityRepository,
    DecisionRepository,
    MarketRegimeRepository,
    RegimeRuleRepository,
    ReportRepository,
    init_regimes_db,
)
from goat.regimes.reporting import (
    ApplicabilityAssessmentReport,
    ApplicabilityDecisionReport,
    MarketApplicabilityReport,
    MarketRegimeReport,
    RuleEvaluationReport,
)
from goat.regimes.rules import RegimeRuleEngine

__all__ = [
    # Core Enums
    "RegimeType",
    "EdgeActivationState",
    "VolatilityState",
    "LiquidityState",
    "ParticipationState",
    "TrendState",
    "StructuralState",
    # Core Models
    "MarketRegime",
    "RegimeRule",
    "ApplicabilityAssessment",
    "ApplicabilityDecision",
    "RegimeExplainabilityRecord",
    # Deterministic Identifiers & Canonical Hashing
    "compute_regime_id",
    "compute_assessment_id",
    "compute_rule_id",
    "compute_decision_id",
    "compute_regime_explanation_id",
    "compute_regime_report_id",
    "serialize_canonical_json",
    # Engines & Coordinators
    "MarketRegimeEngineCoordinator",
    "MarketRegimeClassificationEngine",
    "RegimeRuleEngine",
    "EdgeApplicabilityEngine",
    # Reports
    "MarketRegimeReport",
    "ApplicabilityAssessmentReport",
    "ApplicabilityDecisionReport",
    "RuleEvaluationReport",
    "MarketApplicabilityReport",
    # Repositories & Database Initialization
    "init_regimes_db",
    "MarketRegimeRepository",
    "RegimeRuleRepository",
    "ApplicabilityRepository",
    "DecisionRepository",
    "ReportRepository",
]
