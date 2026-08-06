"""
Project GOAT v0.8 — Test Suite: Deriv Persistence & SQLite Repositories (Exhaustive Matrix)
"""

import pytest

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
from goat.brokers.deriv.persistence.repository import (
    AuthenticationRepository,
    ExecutionRepository,
    HeartbeatRepository,
    MarketSubscriptionRepository,
    OrderRepository,
    ReportRepository,
    SessionRepository,
    init_deriv_db,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
LOGIN_IDS = ["CR100001", "CR200002", "CR300003"]
CURRENCIES = ["USD", "EUR", "GBP"]


@pytest.fixture
def db_conn():
    conn = init_deriv_db(":memory:")
    yield conn
    conn.close()


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_deriv_session_and_subscription_persistence_matrix(db_conn, symbol):
    s_repo = SessionRepository(db_conn)
    sess_id, s_hash = compute_deriv_session_id("BRK_DERIV", "2026-07-31T12:00:00Z")
    session = DerivSession(
        session_id=sess_id,
        broker_id="BRK_DERIV",
        status=ConnectionStatus.CONNECTED,
        server_time="2026-07-31T12:00:00Z",
        ping_ms=15.0,
        metadata={},
        canonical_hash=s_hash,
    )
    s_repo.save(session)
    fetched_sess = s_repo.get_by_id(sess_id)
    assert fetched_sess is not None
    assert fetched_sess.session_id == sess_id

    sub_repo = MarketSubscriptionRepository(db_conn)
    sub_id, sub_hash = compute_deriv_subscription_id(symbol, 1001)
    sub = DerivMarketSubscription(
        subscription_id=sub_id,
        symbol=symbol,
        request_id=1001,
        is_active=True,
        stream_id=f"STR_{symbol}",
        metadata={},
        canonical_hash=sub_hash,
    )
    sub_repo.save(sub)
    fetched_sub = sub_repo.get_by_id(sub_id)
    assert fetched_sub is not None
    assert fetched_sub.symbol == symbol


@pytest.mark.parametrize("symbol,amount", [(sym, a) for sym in SYMBOLS for a in [1.0, 10.0, 50.0]])
def test_deriv_order_and_execution_persistence_matrix(db_conn, symbol, amount):
    o_repo = OrderRepository(db_conn)
    payload_id, p_hash = compute_deriv_order_payload_id("BOI_123", symbol, amount)
    payload = DerivOrderPayload(
        payload_id=payload_id,
        intent_id="BOI_123",
        symbol=symbol,
        amount=amount,
        contract_type=DerivContractType.RISE,
        duration=5,
        duration_unit=DerivDurationUnit.TICKS,
        barrier=None,
        metadata={},
        canonical_hash=p_hash,
    )
    o_repo.save(payload)
    fetched_p = o_repo.get_by_id(payload_id)
    assert fetched_p is not None
    assert fetched_p.amount == amount

    e_repo = ExecutionRepository(db_conn)
    exec_id, e_hash = compute_deriv_execution_id(f"CON_{payload_id[4:]}", amount)
    execution = DerivExecutionResponse(
        execution_id=exec_id,
        contract_id=f"CON_{payload_id[4:]}",
        buy_price=amount,
        payout=round(amount * 1.95, 2),
        status="PURCHASED",
        transaction_id="TX_100",
        metadata={},
        canonical_hash=e_hash,
    )
    e_repo.save(execution)
    fetched_e = e_repo.get_by_id(exec_id)
    assert fetched_e is not None
    assert fetched_e.buy_price == amount


@pytest.mark.parametrize("login_id,currency", [(l, c) for l in LOGIN_IDS for c in CURRENCIES])
def test_auth_heartbeat_and_report_persistence(db_conn, login_id, currency):
    a_repo = AuthenticationRepository(db_conn)
    auth_id, a_hash = compute_deriv_auth_id(1089, login_id)
    auth = DerivAuthentication(
        auth_id=auth_id,
        app_id=1089,
        token_hash="HASH_XYZ",
        is_authenticated=True,
        user_id=login_id,
        email=f"{login_id}@deriv.com",
        currency=currency,
        metadata={},
        canonical_hash=a_hash,
    )
    a_repo.save(auth)
    fetched_auth = a_repo.get_by_id(auth_id)
    assert fetched_auth is not None
    assert fetched_auth.user_id == login_id
    assert fetched_auth.currency == currency

    hb_repo = HeartbeatRepository(db_conn)
    hb_id, h_hash = compute_deriv_heartbeat_id("2026-07-31T12:00:00Z")
    hb = DerivHeartbeat(
        heartbeat_id=hb_id,
        ping_timestamp="2026-07-31T12:00:00Z",
        pong_timestamp="2026-07-31T12:00:00Z",
        roundtrip_ms=15.0,
        metadata={},
        canonical_hash=h_hash,
    )
    hb_repo.save(hb)
    assert hb_repo.get_by_id(hb_id) is not None

    r_repo = ReportRepository(db_conn)
    r_repo.save_report(f"DRR_{login_id}", "EXECUTIVE", "2026-07-31T12:00:00Z", "# Report", "{}", "HASH_R")
