"""
Project GOAT v0.8 — Test Suite: Deriv Order Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.canonical import compute_order_intent_id
from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.brokers.core.models import BrokerOrderIntent
from goat.brokers.deriv.core.enums import DerivDurationUnit
from goat.brokers.deriv.orders.engine import DerivOrderEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
AMOUNTS = [1.0, 5.0, 10.0, 50.0]
DURATIONS = [1, 5, 10]
DURATION_UNITS = [DerivDurationUnit.TICKS, DerivDurationUnit.SECONDS]


@pytest.mark.parametrize("symbol,side,amount", [(sym, s, a) for sym in SYMBOLS for s in SIDES for a in AMOUNTS])
def test_deriv_order_engine_matrix(symbol, side, amount):
    engine = DerivOrderEngine()
    b_id = "BRK_DERIV"
    intent_id, c_hash = compute_order_intent_id(b_id, symbol, side.value, amount, "MARKET", "2026-07-31T12:00:00Z")
    intent = BrokerOrderIntent(
        intent_id=intent_id,
        broker_id=b_id,
        symbol=symbol,
        side=side,
        quantity=amount,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
        stop_loss=None,
        take_profit=None,
        comment="Order Test",
        metadata={},
        canonical_hash=c_hash,
    )

    payload_model, req_json = engine.prepare_order_payload(intent, duration=5, duration_unit=DerivDurationUnit.TICKS)
    assert payload_model.payload_id.startswith("DOP_")
    assert payload_model.amount == amount
    assert req_json["symbol"] == symbol

    mock_buy_response = {
        "buy": {
            "contract_id": f"CON_{payload_model.payload_id[4:]}",
            "buy_price": amount,
            "payout": round(amount * 1.95, 2),
            "transaction_id": "TX_1001",
        }
    }
    exec_model, exec_dict = engine.process_execution_response(mock_buy_response, intent_id)
    assert exec_model.execution_id.startswith("DER_")
    assert exec_model.buy_price == amount
    assert exec_dict["status"] == "FILLED"

    history = engine.get_order_history()
    assert len(history) >= 1
    assert history[-1].payload_id == payload_model.payload_id

    exec_history = engine.get_execution_history()
    assert len(exec_history) >= 1
    assert exec_history[-1].execution_id == exec_model.execution_id


@pytest.mark.parametrize("symbol", SYMBOLS[:6])
@pytest.mark.parametrize("duration", DURATIONS)
@pytest.mark.parametrize("unit", DURATION_UNITS)
def test_deriv_order_engine_duration_matrix(symbol, duration, unit):
    engine = DerivOrderEngine()
    b_id = "BRK_DERIV"
    intent_id, c_hash = compute_order_intent_id(b_id, symbol, "BUY", 10.0, "MARKET", "2026-07-31T12:00:00Z")
    intent = BrokerOrderIntent(
        intent_id=intent_id,
        broker_id=b_id,
        symbol=symbol,
        side=OrderSide.BUY,
        quantity=10.0,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
        stop_loss=None,
        take_profit=None,
        comment="Duration Test",
        metadata={},
        canonical_hash=c_hash,
    )

    payload_model, req_json = engine.prepare_order_payload(intent, duration=duration, duration_unit=unit)
    assert payload_model.duration == duration
    assert payload_model.duration_unit == unit
    assert req_json["duration"] == duration
    assert req_json["duration_unit"] == unit.value
