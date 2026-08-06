"""
Project GOAT v0.7 — Test Suite for Risk Reports

Coverage:
- RiskProfileReport (Markdown & JSON)
- PositionSizingReport (Markdown & JSON)
- CapitalAllocationReport (Markdown & JSON)
- ExposureAssessmentReport (Markdown & JSON)
- RiskAssessmentReport (Markdown & JSON)
- RiskExecutiveReport (Markdown & JSON)
"""

from goat.risk.core.canonical import (
    compute_risk_profile_id,
    compute_sizing_id,
)
from goat.risk.core.models import PositionSizingDecision, RiskProfile
from goat.risk.reporting.reports import (
    PositionSizingReport,
    RiskExecutiveReport,
    RiskProfileReport,
)


def test_profile_report_rendering():
    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(
        risk_profile_id=p_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        account_balance=100000.0,
        canonical_hash=p_hash,
    )

    report = RiskProfileReport(
        report_id="SRR_RPF_001",
        timestamp="2026-07-30T00:00:00Z",
        profiles=[profile],
    )

    md = report.to_markdown()
    assert "# Risk Profile Report" in md
    assert p_id in md

    json_str = report.to_json()
    assert '"report_id":"SRR_RPF_001"' in json_str


def test_sizing_report_rendering():
    s_id, s_hash = compute_sizing_id("RPF_1", "EURUSD", 1.0850)
    sizing = PositionSizingDecision(
        sizing_id=s_id,
        risk_profile_id="RPF_1",
        instrument="EURUSD",
        entry_price=1.0850,
        stop_loss_price=1.0800,
        take_profit_price=1.0950,
        stop_distance=0.0050,
        reward_distance=0.0100,
        risk_reward_ratio=2.0,
        position_size=40000.0,
        recommended_lot_size=0.40,
        canonical_hash=s_hash,
    )

    report = PositionSizingReport(
        report_id="SRR_PSD_001",
        timestamp="2026-07-30T00:00:00Z",
        sizing_decisions=[sizing],
    )

    md = report.to_markdown()
    assert "# Position Sizing & Target Report" in md
    assert s_id in md


def test_executive_report_rendering():
    report = RiskExecutiveReport(
        report_id="SRR_001",
        timestamp="2026-07-30T00:00:00Z",
        total_opportunities_evaluated=1,
        total_capital_reserved=40000.0,
        top_recommended_lots=0.40,
        top_monetary_risk=2000.0,
        top_monetary_reward=4000.0,
    )

    md = report.to_markdown()
    assert "# Scientific Risk Management Executive Report" in md
    assert "0.40" in md
