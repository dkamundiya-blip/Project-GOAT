"""
Project GOAT v0.8 — Test Suite: Deriv Adapter Contract Compliance (Exhaustive Matrix)
"""

import pytest

from goat.brokers.contracts.adapter import AbstractBrokerAdapter
from goat.brokers.core.canonical import compute_order_intent_id
from goat.brokers.core.enums import ConnectionStatus, OrderSide, OrderType, TimeInForce
from goat.brokers.core.models import BrokerOrderIntent
from goat.brokers.deriv.adapter import DerivAdapter
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
AMOUNTS = [1.0, 5.0, 10.0, 50.0, 100.0]


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_deriv_adapter_lifecycle_and_market_data(symbol):
    adapter = DerivAdapter(app_id=1089, api_token="mock_valid_token_123")
    assert isinstance(adapter, AbstractBrokerAdapter)

    conn = adapter.connect()
    assert conn.status == ConnectionStatus.CONNECTED
    assert conn.broker_id == adapter.broker_id

    hb = adapter.heartbeat()
    assert hb.connection_id.startswith("BCN_")

    assert adapter.subscribe_market_data(symbol) is True
    assert adapter.unsubscribe_market_data(symbol) is True

    account = adapter.get_account()
    assert account.balance >= 0.0

    profile = adapter.capabilities()
    assert profile.broker_name == "Deriv Synthetic Indices"
    assert symbol in profile.supported_assets

    assert adapter.health() == ConnectionStatus.CONNECTED

    disc = adapter.disconnect()
    assert disc.status == ConnectionStatus.DISCONNECTED


@pytest.mark.parametrize("symbol,side,amount", [(sym, s, a) for sym in SYMBOLS for s in SIDES for a in AMOUNTS])
def test_deriv_adapter_order_submission_matrix(symbol, side, amount):
    adapter = DerivAdapter(app_id=1089, api_token="mock_valid_token_123")
    adapter.connect()

    intent_id, c_hash = compute_order_intent_id(adapter.broker_id, symbol, side.value, amount, "MARKET", "2026-07-31T12:00:00Z")
    intent = BrokerOrderIntent(
        intent_id=intent_id,
        broker_id=adapter.broker_id,
        symbol=symbol,
        side=side,
        quantity=amount,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
        stop_loss=None,
        take_profit=None,
        comment="Adapter test",
        metadata={},
        canonical_hash=c_hash,
    )

    exec_dict = adapter.submit_order_intent(intent)
    assert exec_dict["status"] == "FILLED"
    assert exec_dict["fill_price"] == amount

    assert adapter.cancel_order("CON_12345") is True
    assert adapter.modify_order("CON_12345", new_stop_loss=9.0) is True

    assert isinstance(adapter.get_positions(), list)
    assert isinstance(adapter.get_open_orders(), list)
    assert isinstance(adapter.get_order_history(), list)
    assert isinstance(adapter.get_execution_history(), list)
