"""
Project GOAT v0.7 — Market Regime Classification & Edge Applicability Engine Coordinator

Main coordinator executing the market regime classification and edge applicability workflow:
1. Classify market regime from observations (MarketRegimeClassificationEngine)
2. Evaluate rules (RegimeRuleEngine)
3. Evaluate edge applicability across candidate ScientificEdges (EdgeApplicabilityEngine)
4. Build ApplicabilityDecision & RegimeExplainabilityRecord models
5. Persist models to SQLite repositories
6. Generate reports
7. Replay past regime & applicability decisions
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.alpha.core.models import ScientificEdge
from goat.regimes.applicability.engine import EdgeApplicabilityEngine
from goat.regimes.classification.engine import MarketRegimeClassificationEngine
from goat.regimes.core.canonical import compute_regime_report_id
from goat.regimes.core.models import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    MarketRegime,
    RegimeExplainabilityRecord,
    RegimeRule,
)
from goat.regimes.persistence.sqlite import (
    ApplicabilityRepository,
    DecisionRepository,
    MarketRegimeRepository,
    RegimeRuleRepository,
    ReportRepository,
)
from goat.regimes.reporting.reports import (
    ApplicabilityAssessmentReport,
    ApplicabilityDecisionReport,
    MarketApplicabilityReport,
    MarketRegimeReport,
    RuleEvaluationReport,
)
from goat.regimes.rules.engine import RegimeRuleEngine


class MarketRegimeEngineCoordinator:
    """Main coordinator executing deterministic regime classification & edge applicability workflow."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.rule_engine = RegimeRuleEngine()
        self.classification_engine = MarketRegimeClassificationEngine(rule_engine=self.rule_engine)
        self.applicability_engine = EdgeApplicabilityEngine()

        # Repositories
        self.regime_repo = MarketRegimeRepository(self.conn)
        self.rule_repo = RegimeRuleRepository(self.conn)
        self.applicability_repo = ApplicabilityRepository(self.conn)
        self.decision_repo = DecisionRepository(self.conn)
        self.report_repo = ReportRepository(self.conn)

        # Persist default rules
        for rule in self.rule_engine.list_rules():
            self.rule_repo.save_rule(rule)

    def execute_regime_applicability_workflow(
        self,
        observations: dict[str, Any],
        candidate_edges: list[ScientificEdge],
        timestamp: str,
    ) -> tuple[MarketRegime, ApplicabilityDecision, MarketApplicabilityReport]:
        """Execute complete classification and edge applicability assessment deterministically.

        Args:
            observations: Market observation metrics dictionary.
            candidate_edges: List of candidate ScientificEdge models.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (MarketRegime, ApplicabilityDecision, MarketApplicabilityReport).
        """
        # 1. Classify Market Regime
        regime, matching_rules = self.classification_engine.classify_regime(observations, timestamp)
        self.regime_repo.save_regime(regime)

        # 2. Evaluate Edge Applicability
        decision, assessments, explainability_records = self.applicability_engine.evaluate_all_edges(
            edges=candidate_edges,
            regime=regime,
            matching_rules=matching_rules,
            timestamp=timestamp,
        )

        for ass in assessments:
            self.applicability_repo.save_assessment(ass)

        for exp in explainability_records:
            self.applicability_repo.save_explanation(exp)

        self.decision_repo.save_decision(decision)

        # 3. Generate Executive MarketApplicabilityReport
        r_type_str = regime.regime_type.value if hasattr(regime.regime_type, "value") else str(regime.regime_type)
        rep_id, _ = compute_regime_report_id("MarketApplicabilityReport", timestamp)

        report = MarketApplicabilityReport(
            report_id=rep_id,
            timestamp=timestamp,
            detected_regime_type=r_type_str,
            total_edges_evaluated=len(candidate_edges),
            active_edges_count=len(decision.active_edges),
            suppressed_edges_count=len(decision.suppressed_edges),
            summary_notes=f"Market classified as '{r_type_str}' (confidence {regime.confidence:.2f}). Activated {len(decision.active_edges)} edges.",
        )
        self.report_repo.save_report(rep_id, "MarketApplicabilityReport", timestamp, report)

        return regime, decision, report

    def generate_sub_reports(
        self,
        regime: MarketRegime,
        decision: ApplicabilityDecision,
        assessments: list[ApplicabilityAssessment],
        matching_rules: list[RegimeRule],
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate sub-reports (RegimeReport, AssessmentReport, DecisionReport, RuleReport)."""
        regime_report = MarketRegimeReport(
            report_id=f"MRR_REG_{timestamp[:10]}",
            timestamp=timestamp,
            regime=regime,
        )
        assessment_report = ApplicabilityAssessmentReport(
            report_id=f"MRR_ASS_{timestamp[:10]}",
            timestamp=timestamp,
            assessments=assessments,
        )
        decision_report = ApplicabilityDecisionReport(
            report_id=f"MRR_DEC_{timestamp[:10]}",
            timestamp=timestamp,
            decision=decision,
        )
        rule_report = RuleEvaluationReport(
            report_id=f"MRR_RUL_{timestamp[:10]}",
            timestamp=timestamp,
            evaluated_rules=self.rule_engine.list_rules(),
            matched_rules=matching_rules,
        )

        return {
            "regime_report": regime_report,
            "assessment_report": assessment_report,
            "decision_report": decision_report,
            "rule_report": rule_report,
        }

    def replay_decision(self, decision_id: str) -> ApplicabilityDecision:
        """Replay exact ApplicabilityDecision model from persistence repository."""
        dec = self.decision_repo.get_decision(decision_id)
        if not dec:
            raise KeyError(f"Decision ID '{decision_id}' not found in persistence repository.")
        return dec

    def replay_regime(self, regime_id: str) -> MarketRegime:
        """Replay exact MarketRegime model from persistence repository."""
        reg = self.regime_repo.get_regime(regime_id)
        if not reg:
            raise KeyError(f"Regime ID '{regime_id}' not found in persistence repository.")
        return reg
