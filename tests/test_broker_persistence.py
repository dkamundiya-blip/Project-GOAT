"""
Project GOAT v0.8 — Test Suite: Broker Persistence & Round-Trip Repositories (Exhaustive Matrix)
"""

import sqlite3
import pytest

from goat.brokers.core.canonical import (
    compute_account_id,
    compute_broker_profile_id,
    compute_connection_id,
    compute_error_id,
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
from goat.brokers.errors.framework import ConnectionError
from goat.brokers.persistence.repository import (
    AccountRepository,
    BrokerRepository,
    ConnectionRepository,
    ErrorRepository,
    OrderIntentRepository,
    init_brokers_db,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
ACCOUNT_TYPES = ["REAL", "DEMO", "VIRTUAL", "PROP"]
ORDER_SIDES = [OrderSide.BUY, OrderSide.SELL]


@pytest.fixture
def db_conn():
    conn = init_brokers_db(":memory:")
    yield conn
    conn.close()


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_broker_profile_persistence_matrix(db_conn, symbol):
    repo = BrokerRepository(db_conn)
    b_id, c_hash = compute_broker_profile_id(f"Broker_{symbol}", "DERIV", "v3")
    profile = BrokerProfile(
        broker_id=b_id,
        broker_name=f"Broker_{symbol}",
        broker_type=BrokerType.DERIV,
        api_version="v3",
        supported_assets=[symbol],
        supported_order_types=[OrderType.MARKET],
        supports_streaming=True,
        supports_positions=True,
        supports_history=True,
        metadata={"asset": symbol},
        canonical_hash=c_hash,
    )
    repo.save(profile)
    fetched = repo.get_by_id(b_id)
    assert fetched is not None
    assert fetched.broker_id == b_id
    assert fetched.supported_assets == [symbol]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("side", ORDER_SIDES)
def test_broker_connection_and_intent_persistence_matrix(db_conn, symbol, side):
    b_repo = BrokerRepository(db_conn)
    b_id, c_hash = compute_broker_profile_id(f"Broker_{symbol}", "DERIV", "v3")
    profile = BrokerProfile(
        broker_id=b_id,
        broker_name=f"Broker_{symbol}",
        broker_type=BrokerType.DERIV,
        api_version="v3",
        supported_assets=[symbol],
        supported_order_types=[OrderType.MARKET],
        supports_streaming=True,
        supports_positions=True,
        supports_history=True,
        metadata={},
        canonical_hash=c_hash,
    )
    b_repo.save(profile)

    c_repo = ConnectionRepository(db_conn)
    conn_id, conn_hash = compute_connection_id(b_id, "2026-07-31T12:00:00Z")
    conn = BrokerConnection(
        connection_id=conn_id,
        broker_id=b_id,
        status=ConnectionStatus.CONNECTED,
        connected_at="2026-07-31T12:00:00Z",
        heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=10.0,
        reconnect_attempts=0,
        metadata={},
        canonical_hash=conn_hash,
    )
    c_repo.save(conn)
    assert c_repo.get_by_id(conn_id) is not None

    i_repo = OrderIntentRepository(db_conn)
    intent_id, i_hash = compute_order_intent_id(b_id, symbol, side.value, 1.0, "MARKET", "2026-07-31T12:00:00Z")
    intent = BrokerOrderIntent(
        intent_id=intent_id,
        broker_id=b_id,
        symbol=symbol,
        side=side,
        quantity=1.0,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
        stop_loss=None,
        take_profit=None,
        comment="",
        metadata={},
        canonical_hash=i_hash,
    )
    i_repo.save(intent)
    fetched_intent = i_repo.get_by_id(intent_id)
    assert fetched_intent is not None
    assert fetched_intent.side == side


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("acc_type", ACCOUNT_TYPES)
def test_broker_account_persistence_matrix(db_conn, symbol, acc_type):
    b_repo = BrokerRepository(db_conn)
    b_id, c_hash = compute_broker_profile_id(f"Broker_{symbol}", "DERIV", "v3")
    profile = BrokerProfile(
        broker_id=b_id,
        broker_name=f"Broker_{symbol}",
        broker_type=BrokerType.DERIV,
        api_version="v3",
        supported_assets=[symbol],
        supported_order_types=[OrderType.MARKET],
        supports_streaming=True,
        supports_positions=True,
        supports_history=True,
        metadata={},
        canonical_hash=c_hash,
    )
    b_repo.save(profile)

    a_repo = AccountRepository(db_conn)
    acc_id, a_hash = compute_account_id(b_id, acc_type, "USD")
    account = BrokerAccount(
        account_id=acc_id,
        broker_id=b_id,
        account_type=acc_type,
        account_currency="USD",
        balance=10000.0,
        equity=10000.0,
        margin=0.0,
        free_margin=10000.0,
        leverage=100.0,
        metadata={},
        canonical_hash=a_hash,
    )
    a_repo.save(account)
    fetched = a_repo.get_by_id(acc_id)
    assert fetched is not None
    assert fetched.account_type == acc_type


@pytest.mark.parametrize("code", ["ERR_1", "ERR_2", "ERR_3", "ERR_4", "ERR_5"])
def test_error_persistence_matrix(db_conn, code):
    repo = ErrorRepository(db_conn)
    exc = ConnectionError(f"Connection failed {code}")
    repo.save(exc.model)
    fetched = repo.get_by_id(exc.model.error_id)
    assert fetched is not None
    assert fetched.code == exc.model.code
