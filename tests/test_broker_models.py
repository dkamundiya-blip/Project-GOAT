"""
Project GOAT v0.8 — Test Suite: Broker Core Models & Canonical IDs (Exhaustive Matrix)
"""

import pytest
from pydantic import ValidationError

from goat.brokers.core.canonical import (
    compute_account_id,
    compute_broker_profile_id,
    compute_connection_id,
    compute_order_intent_id,
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
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
BROKER_TYPES = [b.value for b in BrokerType]
CONNECTION_STATUSES = [c.value for c in ConnectionStatus]
ORDER_TYPES = [o.value for o in OrderType]
ORDER_SIDES = [s.value for s in OrderSide]
ACCOUNT_TYPES = ["REAL", "DEMO", "VIRTUAL", "PROP"]
TIMEFRAMES = ["GTC", "IOC", "FOK"]


@pytest.mark.parametrize("b_type", BROKER_TYPES)
@pytest.mark.parametrize("b_name", ["Deriv", "Weltrade", "MT5", "Generic"])
@pytest.mark.parametrize("api_ver", ["v1", "v2", "v3"])
def test_broker_profile_immutability_matrix(b_type, b_name, api_ver):
    broker_id, canonical_hash = compute_broker_profile_id(b_name, b_type, api_ver)
    profile = BrokerProfile(
        broker_id=broker_id,
        broker_name=b_name,
        broker_type=BrokerType(b_type),
        api_version=api_ver,
        supported_assets=SYMBOLS,
        supported_order_types=[OrderType.MARKET, OrderType.LIMIT],
        supports_streaming=True,
        supports_positions=True,
        supports_history=True,
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert profile.broker_id.startswith("BRK_")
    assert profile.broker_type.value == b_type

    with pytest.raises(ValidationError):
        profile.api_version = "v4"


@pytest.mark.parametrize("status", CONNECTION_STATUSES)
@pytest.mark.parametrize("latency", [1.0, 10.0, 100.0, 1500.0])
@pytest.mark.parametrize("reconnects", [0, 1, 5])
def test_broker_connection_immutability_matrix(status, latency, reconnects):
    conn_id, canonical_hash = compute_connection_id("BRK_TEST1234567890", "2026-07-31T12:00:00Z")
    conn = BrokerConnection(
        connection_id=conn_id,
        broker_id="BRK_TEST1234567890",
        status=ConnectionStatus(status),
        connected_at="2026-07-31T12:00:00Z",
        heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=latency,
        reconnect_attempts=reconnects,
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert conn.connection_id.startswith("BCN_")
    assert conn.status.value == status
    assert conn.reconnect_attempts == reconnects


@pytest.mark.parametrize("balance", [100.0, 1000.0, 50000.0])
@pytest.mark.parametrize("currency", ["USD", "EUR", "GBP"])
@pytest.mark.parametrize("acc_type", ACCOUNT_TYPES)
def test_broker_account_immutability_matrix(balance, currency, acc_type):
    acc_id, canonical_hash = compute_account_id("BRK_TEST1234567890", acc_type, currency)
    account = BrokerAccount(
        account_id=acc_id,
        broker_id="BRK_TEST1234567890",
        account_type=acc_type,
        account_currency=currency,
        balance=balance,
        equity=balance,
        margin=0.0,
        free_margin=balance,
        leverage=100.0,
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert account.account_id.startswith("BAC_")
    assert account.balance == balance
    assert account.account_type == acc_type


@pytest.mark.parametrize("symbol", SYMBOLS[:6])
@pytest.mark.parametrize("side", ORDER_SIDES)
@pytest.mark.parametrize("o_type", ORDER_TYPES)
@pytest.mark.parametrize("tif", TIMEFRAMES)
def test_broker_order_intent_immutability_matrix(symbol, side, o_type, tif):
    intent_id, canonical_hash = compute_order_intent_id(
        "BRK_TEST1234567890", symbol, side, 1.0, o_type, "2026-07-31T12:00:00Z"
    )
    intent = BrokerOrderIntent(
        intent_id=intent_id,
        broker_id="BRK_TEST1234567890",
        symbol=symbol,
        side=OrderSide(side),
        quantity=1.0,
        order_type=OrderType(o_type),
        time_in_force=TimeInForce(tif),
        stop_loss=10.0,
        take_profit=15.0,
        comment="Test Intent",
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert intent.intent_id.startswith("BOI_")
    assert intent.symbol == symbol
    assert intent.side.value == side
    assert intent.order_type.value == o_type
    assert intent.time_in_force.value == tif
