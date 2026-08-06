"""
Project GOAT v0.8 — Test Suite: Broker Reporting (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.canonical import (
    compute_account_id,
    compute_broker_profile_id,
    compute_connection_id,
    compute_order_intent_id,
    compute_report_id,
)
from goat.brokers.core.enums import (
    BrokerType,
    ConnectionStatus,
    OrderSide,
    OrderType,
    TimeInForce,
)
from goat.brokers.core.models import (
    BrokerAccount,
    BrokerConnection,
    BrokerOrderIntent,
    BrokerProfile,
)
from goat.brokers.reporting.reports import (
    AccountReport,
    BrokerCapabilityReport,
    BrokerExecutiveReport,
    BrokerProfileReport,
    ConnectionReport,
    OrderIntentReport,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
ORDER_SIDES = [OrderSide.BUY, OrderSide.SELL]
CONNECTION_STATUSES = [ConnectionStatus.CONNECTED, ConnectionStatus.DEGRADED, ConnectionStatus.RECONNECTING, ConnectionStatus.DISCONNECTED]
ACCOUNT_TYPES = ["REAL", "DEMO", "VIRTUAL", "PROP"]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("b_type", ["DERIV", "WELTRADE", "MT5"])
def test_broker_profile_report_matrix(symbol, b_type):
    b_id, p_hash = compute_broker_profile_id(f"Broker_{symbol}", b_type, "v3")
    profile = BrokerProfile(
        broker_id=b_id,
        broker_name=f"Broker_{symbol}",
        broker_type=BrokerType(b_type),
        api_version="v3",
        supported_assets=[symbol],
        supported_order_types=[OrderType.MARKET],
        supports_streaming=True,
        supports_positions=True,
        supports_history=True,
        metadata={},
        canonical_hash=p_hash,
    )

    rep_id, r_hash = compute_report_id("PROFILE", "2026-07-31T12:00:00Z")
    p_report = BrokerProfileReport(
        report_id=rep_id, profile=profile, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash
    )
    assert symbol in p_report.to_markdown()
    assert rep_id in p_report.to_json()


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("status", CONNECTION_STATUSES)
def test_connection_report_matrix(symbol, status):
    b_id, p_hash = compute_broker_profile_id(f"Broker_{symbol}", "DERIV", "v3")
    conn_id, c_hash = compute_connection_id(b_id, "2026-07-31T12:00:00Z")
    conn = BrokerConnection(
        connection_id=conn_id, broker_id=b_id, status=status,
        connected_at="2026-07-31T12:00:00Z", heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=10.0, reconnect_attempts=0, metadata={}, canonical_hash=c_hash,
    )
    rep_id, r_hash = compute_report_id("CONNECTION", "2026-07-31T12:00:00Z")
    c_report = ConnectionReport(report_id=rep_id, connection=conn, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert b_id in c_report.to_markdown()
    assert status.value in c_report.to_markdown()


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("acc_type", ACCOUNT_TYPES)
def test_account_report_matrix(symbol, acc_type):
    b_id, p_hash = compute_broker_profile_id(f"Broker_{symbol}", "DERIV", "v3")
    acc_id, a_hash = compute_account_id(b_id, acc_type, "USD")
    account = BrokerAccount(
        account_id=acc_id, broker_id=b_id, account_type=acc_type, account_currency="USD",
        balance=10000.0, equity=10000.0, margin=0.0, free_margin=10000.0, leverage=100.0, metadata={}, canonical_hash=a_hash,
    )
    rep_id, r_hash = compute_report_id("ACCOUNT", "2026-07-31T12:00:00Z")
    a_report = AccountReport(report_id=rep_id, account=account, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert acc_type in a_report.to_markdown()


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("side", ORDER_SIDES)
def test_order_intent_report_matrix(symbol, side):
    b_id, p_hash = compute_broker_profile_id(f"Broker_{symbol}", "DERIV", "v3")
    intent_id, i_hash = compute_order_intent_id(b_id, symbol, side.value, 1.0, "MARKET", "2026-07-31T12:00:00Z")
    intent = BrokerOrderIntent(
        intent_id=intent_id, broker_id=b_id, symbol=symbol, side=side, quantity=1.0, order_type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC, stop_loss=None, take_profit=None, comment="test", metadata={}, canonical_hash=i_hash,
    )
    rep_id, r_hash = compute_report_id("INTENT", "2026-07-31T12:00:00Z")
    i_report = OrderIntentReport(report_id=rep_id, intent=intent, timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash)
    assert symbol in i_report.to_markdown()
    assert side.value in i_report.to_markdown()


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
def test_executive_report_matrix(symbol):
    b_id, p_hash = compute_broker_profile_id(f"Broker_{symbol}", "DERIV", "v3")
    profile = BrokerProfile(
        broker_id=b_id, broker_name=f"Broker_{symbol}", broker_type=BrokerType.DERIV, api_version="v3",
        supported_assets=[symbol], supported_order_types=[OrderType.MARKET], supports_streaming=True,
        supports_positions=True, supports_history=True, metadata={}, canonical_hash=p_hash,
    )
    conn_id, c_hash = compute_connection_id(b_id, "2026-07-31T12:00:00Z")
    conn = BrokerConnection(
        connection_id=conn_id, broker_id=b_id, status=ConnectionStatus.CONNECTED,
        connected_at="2026-07-31T12:00:00Z", heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=10.0, reconnect_attempts=0, metadata={}, canonical_hash=c_hash,
    )
    acc_id, a_hash = compute_account_id(b_id, "REAL", "USD")
    account = BrokerAccount(
        account_id=acc_id, broker_id=b_id, account_type="REAL", account_currency="USD",
        balance=10000.0, equity=10000.0, margin=0.0, free_margin=10000.0, leverage=100.0, metadata={}, canonical_hash=a_hash,
    )

    rep_id, r_hash = compute_report_id("EXECUTIVE", "2026-07-31T12:00:00Z")
    exec_rep = BrokerExecutiveReport(
        report_id=rep_id, active_brokers_count=1, profiles=[profile], connections=[conn], accounts=[account],
        timestamp="2026-07-31T12:00:00Z", canonical_hash=r_hash,
    )
    assert "Step 7.2" in exec_rep.to_markdown()
