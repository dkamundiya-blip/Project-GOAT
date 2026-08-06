"""
Project GOAT v0.8 — Test Suite: Production Execution Reporting (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import OrderSide
from goat.execution.core.canonical import (
    compute_execution_decision_id,
    compute_execution_failure_id,
    compute_execution_lifecycle_id,
    compute_execution_report_id,
    compute_execution_summary_id,
)
from goat.execution.core.enums import ExecutionFailureCategory, ExecutionState
from goat.execution.core.models import (
    ExecutionDecision,
    ExecutionFailure,
    ExecutionLifecycle,
    ExecutionSummary,
)
from goat.execution.intents.engine import ExecutionIntentEngine
from goat.execution.reporting.reports import (
    ExecutionDecisionReport,
    ExecutionExecutiveReport,
    ExecutionFailureReport,
    ExecutionIntentReport,
    ExecutionLifecycleReport,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
AMOUNTS = [1.0, 5.0, 10.0, 50.0, 100.0]


@pytest.mark.parametrize("symbol,side,amount", [(sym, s, a) for sym in SYMBOLS for s in SIDES for a in AMOUNTS])
def test_execution_intent_report_matrix(symbol, side, amount):
    intent_engine = ExecutionIntentEngine()
    intent = intent_engine.create_intent(
        signal_id=f"SIG_{symbol}",
        sizing_decision_id="SIZ_1",
        allocation_id="ALL_1",
        broker_id="BRK_DERIV",
        symbol=symbol,
        side=side,
        quantity=amount,
    )
    rep_id, r_hash = compute_execution_report_id("INTENT", "2026-07-31T12:00:00Z")
    report = ExecutionIntentReport(report_id=rep_id, intent=intent, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)

    assert intent.intent_id in report.to_markdown()
    assert symbol in report.to_markdown()
    assert rep_id in report.to_json()


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("side", SIDES)
def test_execution_all_reports_matrix(symbol, side):
    rep_id, r_hash = compute_execution_report_id("REPORT", "2026-07-31T12:00:00Z")
    intent_id = f"EXI_{symbol}_{side.value}"

    # Decision report
    d_id, d_hash = compute_execution_decision_id(intent_id, True, "2026-07-31T12:00:00Z")
    decision = ExecutionDecision(decision_id=d_id, intent_id=intent_id, approved=True, explanation="Approved", timestamp="2026-07-31T12:00:00Z", metadata={}, canonical_hash=d_hash)
    d_report = ExecutionDecisionReport(report_id=rep_id, decision=decision, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert intent_id in d_report.to_markdown()

    # Lifecycle report
    l_id, l_hash = compute_execution_lifecycle_id(intent_id, "FILLED", "2026-07-31T12:00:00Z")
    lc = ExecutionLifecycle(lifecycle_id=l_id, intent_id=intent_id, state=ExecutionState.FILLED, previous_state=ExecutionState.DISPATCHED, transition_timestamp="2026-07-31T12:00:00Z", explanation="Filled", metadata={}, canonical_hash=l_hash)
    l_report = ExecutionLifecycleReport(report_id=rep_id, lifecycle_history=[lc], timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert "FILLED" in l_report.to_markdown()

    # Failure report
    f_id, f_hash = compute_execution_failure_id(intent_id, "VALIDATION_FAILED", "ERR_1", "2026-07-31T12:00:00Z")
    failure = ExecutionFailure(failure_id=f_id, intent_id=intent_id, error_code="ERR_1", category=ExecutionFailureCategory.VALIDATION_FAILED, reason="Validation failed", timestamp="2026-07-31T12:00:00Z", metadata={}, canonical_hash=f_hash)
    f_report = ExecutionFailureReport(report_id=rep_id, failure=failure, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert "ERR_1" in f_report.to_markdown()

    # Executive report
    sum_id, s_hash = compute_execution_summary_id(10, "2026-07-31T12:00:00Z")
    summary = ExecutionSummary(summary_id=sum_id, total_intents=10, dispatched_count=8, filled_count=8, rejected_count=1, failed_count=1, timestamp="2026-07-31T12:00:00Z", metadata={}, canonical_hash=s_hash)
    exec_report = ExecutionExecutiveReport(report_id=rep_id, summary=summary, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert "Executive Report" in exec_report.to_markdown()
