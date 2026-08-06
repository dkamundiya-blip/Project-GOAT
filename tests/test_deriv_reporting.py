"""
Project GOAT v0.8 — Test Suite: Deriv Subsystem Reporting (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.deriv.core.canonical import (
    compute_deriv_auth_id,
    compute_deriv_execution_id,
    compute_deriv_order_payload_id,
    compute_deriv_report_id,
    compute_deriv_session_id,
    compute_deriv_subscription_id,
)
from goat.brokers.deriv.core.enums import DerivContractType, DerivDurationUnit
from goat.brokers.deriv.core.models import (
    DerivAuthentication,
    DerivExecutionResponse,
    DerivMarketSubscription,
    DerivOrderPayload,
    DerivSession,
)
from goat.brokers.deriv.reporting.reports import (
    AuthenticationReport,
    DerivExecutiveReport,
    DerivSessionReport,
    ExecutionTranslationReport,
    OrderTranslationReport,
    SubscriptionReport,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
LOGIN_IDS = ["CR100001", "CR200002", "CR300003"]
STATUSES = [ConnectionStatus.CONNECTED, ConnectionStatus.DEGRADED, ConnectionStatus.DISCONNECTED]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("status", STATUSES)
def test_deriv_session_report_matrix(symbol, status):
    sess_id, s_hash = compute_deriv_session_id(f"BRK_{symbol}", "2026-07-31T12:00:00Z")
    session = DerivSession(
        session_id=sess_id, broker_id=f"BRK_{symbol}", status=status,
        server_time="2026-07-31T12:00:00Z", ping_ms=15.0, metadata={}, canonical_hash=s_hash,
    )
    rep_id, r_hash = compute_deriv_report_id("SESSION", "2026-07-31T12:00:00Z")
    s_report = DerivSessionReport(report_id=rep_id, session=session, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert sess_id in s_report.to_markdown()
    assert status.value in s_report.to_markdown()
    assert rep_id in s_report.to_json()


@pytest.mark.parametrize("login_id", LOGIN_IDS)
@pytest.mark.parametrize("app_id", [1089, 9999, 12345])
def test_auth_report_matrix(login_id, app_id):
    auth_id, a_hash = compute_deriv_auth_id(app_id, login_id)
    auth = DerivAuthentication(
        auth_id=auth_id, app_id=app_id, token_hash="HASH", is_authenticated=True, user_id=login_id,
        email=f"{login_id}@deriv.com", currency="USD", metadata={}, canonical_hash=a_hash,
    )
    rep_id, r_hash = compute_deriv_report_id("AUTH", "2026-07-31T12:00:00Z")
    a_report = AuthenticationReport(report_id=rep_id, auth=auth, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert str(app_id) in a_report.to_markdown()
    assert login_id in a_report.to_markdown()


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_subscription_and_order_report_matrix(symbol):
    rep_id, r_hash = compute_deriv_report_id("REPORT", "2026-07-31T12:00:00Z")
    sub_id, sub_hash = compute_deriv_subscription_id(symbol, 1001)
    sub = DerivMarketSubscription(subscription_id=sub_id, symbol=symbol, request_id=1001, is_active=True, stream_id="STR", metadata={}, canonical_hash=sub_hash)
    sub_report = SubscriptionReport(report_id=rep_id, subscriptions=[sub], timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert symbol in sub_report.to_markdown()

    p_id, p_hash = compute_deriv_order_payload_id("BOI_1", symbol, 10.0)
    payload = DerivOrderPayload(payload_id=p_id, intent_id="BOI_1", symbol=symbol, amount=10.0, contract_type=DerivContractType.RISE, duration=5, duration_unit=DerivDurationUnit.TICKS, barrier=None, metadata={}, canonical_hash=p_hash)
    o_report = OrderTranslationReport(report_id=rep_id, payload=payload, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert symbol in o_report.to_markdown()

    exec_id, e_hash = compute_deriv_execution_id(f"CON_{symbol}", 10.0)
    execution = DerivExecutionResponse(execution_id=exec_id, contract_id=f"CON_{symbol}", buy_price=10.0, payout=19.5, status="PURCHASED", transaction_id="TX_1", metadata={}, canonical_hash=e_hash)
    e_report = ExecutionTranslationReport(report_id=rep_id, execution=execution, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert f"CON_{symbol}" in e_report.to_markdown()


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
def test_executive_report_matrix(symbol):
    sess_id, s_hash = compute_deriv_session_id(f"BRK_{symbol}", "2026-07-31T12:00:00Z")
    session = DerivSession(session_id=sess_id, broker_id=f"BRK_{symbol}", status=ConnectionStatus.CONNECTED, server_time="2026-07-31T12:00:00Z", ping_ms=15.0, metadata={}, canonical_hash=s_hash)
    auth_id, a_hash = compute_deriv_auth_id(1089, "CR100001")
    auth = DerivAuthentication(auth_id=auth_id, app_id=1089, token_hash="HASH", is_authenticated=True, user_id="CR100001", email="u@deriv.com", currency="USD", metadata={}, canonical_hash=a_hash)
    rep_id, r_hash = compute_deriv_report_id("EXECUTIVE", "2026-07-31T12:00:00Z")

    exec_report = DerivExecutiveReport(
        report_id=rep_id, session=session, auth=auth, active_subscriptions_count=1, total_orders_translated=1,
        timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash,
    )
    assert "Step 7.3" in exec_report.to_markdown()
