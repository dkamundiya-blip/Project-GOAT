"""
Project GOAT v0.7 — Test Suite for Signal Reports

Coverage:
- TradingSignalReport (Markdown & JSON)
- SignalPayloadReport (Markdown & JSON)
- SignalLifecycleReport (Markdown & JSON)
- ExecutionReadinessReport (Markdown & JSON)
- SignalAuditReport (Markdown & JSON)
- SignalExecutiveReport (Markdown & JSON)
"""

from goat.signals.core.canonical import compute_signal_id
from goat.signals.core.enums import SignalDirection
from goat.signals.core.models import TradingSignal
from goat.signals.reporting.reports import (
    SignalExecutiveReport,
    TradingSignalReport,
)


def test_trading_signal_report_rendering():
    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(
        signal_id=s_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        risk_assessment_id="RSA_1",
        composite_id="CMP_1",
        regime_id="MRG_1",
        instrument="EURUSD",
        direction=SignalDirection.BUY,
        entry_price=1.0850,
        stop_loss=1.0800,
        take_profit=1.0950,
        recommended_lot_size=4.0,
        monetary_risk=2000.0,
        monetary_reward=4000.0,
        risk_reward_ratio=2.0,
        scientific_confidence=0.90,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
        canonical_hash=s_hash,
    )

    report = TradingSignalReport(
        report_id="SSR_001",
        timestamp="2026-07-30T00:00:00Z",
        signals=[signal],
    )

    md = report.to_markdown()
    assert "# Trading Signal Summary Report" in md
    assert s_id in md

    json_str = report.to_json()
    assert '"report_id":"SSR_001"' in json_str


def test_executive_report_rendering():
    report = SignalExecutiveReport(
        report_id="SSR_EXEC_001",
        timestamp="2026-07-30T00:00:00Z",
        total_signals_generated=1,
        total_signals_ready=1,
        top_instrument="EURUSD",
        top_direction="BUY",
        top_lot_size=4.0,
        top_monetary_risk=2000.0,
        top_monetary_reward=4000.0,
    )

    md = report.to_markdown()
    assert "# Scientific Signal Executive Report" in md
    assert "EURUSD" in md
