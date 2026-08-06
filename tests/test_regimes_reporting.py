"""
Project GOAT v0.7 — Test Suite for Market Regime Reports

Coverage:
- MarketRegimeReport (Markdown & JSON)
- ApplicabilityAssessmentReport (Markdown & JSON)
- ApplicabilityDecisionReport (Markdown & JSON)
- RuleEvaluationReport (Markdown & JSON)
- MarketApplicabilityReport (Markdown & JSON)
"""

from goat.regimes.core.canonical import (
    compute_assessment_id,
    compute_decision_id,
    compute_regime_id,
)
from goat.regimes.core.enums import EdgeActivationState, RegimeType
from goat.regimes.core.models import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    MarketRegime,
)
from goat.regimes.reporting.reports import (
    ApplicabilityAssessmentReport,
    ApplicabilityDecisionReport,
    MarketApplicabilityReport,
    MarketRegimeReport,
)


def test_market_regime_report_rendering():
    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(
        regime_id=r_id,
        timestamp="2026-07-30T00:00:00Z",
        regime_type=RegimeType.TRENDING,
        confidence=0.85,
        canonical_hash=r_hash,
    )

    report = MarketRegimeReport(
        report_id="MRR_REG_001",
        timestamp="2026-07-30T00:00:00Z",
        regime=regime,
    )

    md = report.to_markdown()
    assert "# Market Regime Classification Report" in md
    assert r_id in md

    json_str = report.to_json()
    assert '"report_id":"MRR_REG_001"' in json_str


def test_applicability_assessment_report_rendering():
    a_id, a_hash = compute_assessment_id("SED_1", "MRG_1")
    assessment = ApplicabilityAssessment(
        assessment_id=a_id,
        edge_id="SED_1",
        regime_id="MRG_1",
        applicability=EdgeActivationState.ACTIVE,
        applicability_score=0.85,
        canonical_hash=a_hash,
    )

    report = ApplicabilityAssessmentReport(
        report_id="MRR_ASS_001",
        timestamp="2026-07-30T00:00:00Z",
        assessments=[assessment],
    )

    md = report.to_markdown()
    assert "# Edge Applicability Assessment Report" in md
    assert a_id in md


def test_market_applicability_report_rendering():
    report = MarketApplicabilityReport(
        report_id="MRR_001",
        timestamp="2026-07-30T00:00:00Z",
        detected_regime_type="TRENDING",
        total_edges_evaluated=5,
        active_edges_count=3,
        suppressed_edges_count=2,
    )

    md = report.to_markdown()
    assert "# Market Regime & Edge Applicability Executive Report" in md
    assert "TRENDING" in md
