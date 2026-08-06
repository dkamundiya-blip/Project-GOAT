"""
Project GOAT v0.8 — Test Suite: Deriv Core Models & Canonical IDs (Exhaustive Matrix)
"""

import pytest
from pydantic import ValidationError

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.deriv.core.canonical import (
    compute_deriv_account_snapshot_id,
    compute_deriv_auth_id,
    compute_deriv_execution_id,
    compute_deriv_heartbeat_id,
    compute_deriv_order_payload_id,
    compute_deriv_session_id,
    compute_deriv_subscription_id,
)
from goat.brokers.deriv.core.enums import DerivContractType, DerivDurationUnit
from goat.brokers.deriv.core.models import (
    DerivAccountSnapshot,
    DerivAuthentication,
    DerivExecutionResponse,
    DerivHeartbeat,
    DerivMarketSubscription,
    DerivOrderPayload,
    DerivSession,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
CONTRACT_TYPES = [c.value for c in DerivContractType]
DURATION_UNITS = [d.value for d in DerivDurationUnit]
LOGIN_IDS = ["CR100001", "CR200002", "CR300003"]
CURRENCIES = ["USD", "EUR", "GBP"]


@pytest.mark.parametrize("status", [ConnectionStatus.CONNECTED, ConnectionStatus.DISCONNECTED, ConnectionStatus.DEGRADED])
@pytest.mark.parametrize("ping", [5.0, 15.0, 100.0, 1500.0])
def test_deriv_session_model_matrix(status, ping):
    sess_id, c_hash = compute_deriv_session_id("BRK_DERIV", "2026-07-31T12:00:00Z")
    session = DerivSession(
        session_id=sess_id,
        broker_id="BRK_DERIV",
        status=status,
        server_time="2026-07-31T12:00:00Z",
        ping_ms=ping,
        metadata={},
        canonical_hash=c_hash,
    )
    assert session.session_id.startswith("DRS_")
    assert session.status == status

    with pytest.raises(ValidationError):
        session.ping_ms = 999.0


@pytest.mark.parametrize("app_id", [1089, 9999, 12345])
@pytest.mark.parametrize("user_id", LOGIN_IDS)
def test_deriv_auth_model_matrix(app_id, user_id):
    auth_id, c_hash = compute_deriv_auth_id(app_id, user_id)
    auth = DerivAuthentication(
        auth_id=auth_id,
        app_id=app_id,
        token_hash="HASH1234567890",
        is_authenticated=True,
        user_id=user_id,
        email=f"{user_id}@deriv.com",
        currency="USD",
        metadata={},
        canonical_hash=c_hash,
    )
    assert auth.auth_id.startswith("DAT_")
    assert auth.app_id == app_id
    assert auth.user_id == user_id


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("contract_type", CONTRACT_TYPES)
@pytest.mark.parametrize("unit", DURATION_UNITS)
def test_deriv_order_payload_model_matrix(symbol, contract_type, unit):
    payload_id, c_hash = compute_deriv_order_payload_id("BOI_12345", symbol, 10.0)
    payload = DerivOrderPayload(
        payload_id=payload_id,
        intent_id="BOI_12345",
        symbol=symbol,
        amount=10.0,
        contract_type=DerivContractType(contract_type),
        duration=5,
        duration_unit=DerivDurationUnit(unit),
        barrier=None,
        metadata={},
        canonical_hash=c_hash,
    )
    assert payload.payload_id.startswith("DOP_")
    assert payload.symbol == symbol
    assert payload.contract_type.value == contract_type
    assert payload.duration_unit.value == unit


@pytest.mark.parametrize("login_id", LOGIN_IDS)
@pytest.mark.parametrize("currency", CURRENCIES)
@pytest.mark.parametrize("balance", [100.0, 5000.0, 50000.0])
def test_deriv_account_snapshot_model_matrix(login_id, currency, balance):
    snap_id, c_hash = compute_deriv_account_snapshot_id(login_id, currency, balance)
    snap = DerivAccountSnapshot(
        snapshot_id=snap_id,
        login_id=login_id,
        currency=currency,
        balance=balance,
        equity=balance + 100.0,
        margin=50.0,
        metadata={},
        canonical_hash=c_hash,
    )
    assert snap.snapshot_id.startswith("DAC_")
    assert snap.login_id == login_id
    assert snap.balance == balance


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("req_id", [1001, 1002, 1003])
def test_deriv_market_subscription_model_matrix(symbol, req_id):
    sub_id, c_hash = compute_deriv_subscription_id(symbol, req_id)
    sub = DerivMarketSubscription(
        subscription_id=sub_id,
        symbol=symbol,
        request_id=req_id,
        is_active=True,
        stream_id=f"STR_{symbol}",
        metadata={},
        canonical_hash=c_hash,
    )
    assert sub.subscription_id.startswith("DMS_")
    assert sub.symbol == symbol
    assert sub.request_id == req_id


@pytest.mark.parametrize("contract_id", ["CON_1001", "CON_1002", "CON_1003"])
@pytest.mark.parametrize("buy_price", [10.0, 50.0, 100.0])
def test_deriv_execution_response_model_matrix(contract_id, buy_price):
    exec_id, c_hash = compute_deriv_execution_id(contract_id, buy_price)
    execution = DerivExecutionResponse(
        execution_id=exec_id,
        contract_id=contract_id,
        buy_price=buy_price,
        payout=round(buy_price * 1.95, 2),
        status="PURCHASED",
        transaction_id="TX_999",
        metadata={},
        canonical_hash=c_hash,
    )
    assert execution.execution_id.startswith("DER_")
    assert execution.contract_id == contract_id
    assert execution.buy_price == buy_price


@pytest.mark.parametrize("ping_ms", [5.0, 15.0, 50.0, 150.0])
def test_deriv_heartbeat_model_matrix(ping_ms):
    hb_id, c_hash = compute_deriv_heartbeat_id("2026-07-31T12:00:00Z")
    hb = DerivHeartbeat(
        heartbeat_id=hb_id,
        ping_timestamp="2026-07-31T12:00:00Z",
        pong_timestamp="2026-07-31T12:00:00Z",
        roundtrip_ms=ping_ms,
        metadata={},
        canonical_hash=c_hash,
    )
    assert hb.heartbeat_id.startswith("DHB_")
    assert hb.roundtrip_ms == ping_ms
