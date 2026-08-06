"""
Project GOAT v0.8 — Test Suite: Broker Order Intent Engine (Exhaustive Matrix)
"""

import pytest
from pydantic import ValidationError

from goat.brokers.contracts.registry import BrokerCapabilityRegistry
from goat.brokers.core.canonical import compute_broker_profile_id, compute_order_intent_id
from goat.brokers.core.enums import BrokerType, OrderSide, OrderType, TimeInForce
from goat.brokers.core.models import BrokerOrderIntent, BrokerProfile
from goat.brokers.orders.engine import BrokerOrderIntentEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
ORDER_TYPES = [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT]
ORDER_SIDES = [OrderSide.BUY, OrderSide.SELL]
QUANTITIES = [-1.0, 0.0, 0.1, 1.0, 10.0]


def make_intent(broker_id: str, symbol: str, quantity: float, order_type: OrderType, side: OrderSide) -> BrokerOrderIntent:
    intent_id, canonical_hash = compute_order_intent_id(broker_id, symbol, side.value, quantity, order_type.value, "2026-07-31T12:00:00Z")
    return BrokerOrderIntent(
        intent_id=intent_id,
        broker_id=broker_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=order_type,
        time_in_force=TimeInForce.GTC,
        stop_loss=None,
        take_profit=None,
        comment="Test Intent",
        metadata={},
        canonical_hash=canonical_hash,
    )


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("quantity", QUANTITIES)
@pytest.mark.parametrize("side", ORDER_SIDES)
def test_order_intent_engine_quantity_matrix(symbol, quantity, side):
    registry = BrokerCapabilityRegistry()
    b_id, c_hash = compute_broker_profile_id("Deriv", "DERIV", "v3")
    profile = BrokerProfile(
        broker_id=b_id,
        broker_name="Deriv",
        broker_type=BrokerType.DERIV,
        api_version="v3",
        supported_assets=SYMBOLS,
        supported_order_types=[OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT],
        supports_streaming=True,
        supports_positions=True,
        supports_history=True,
        metadata={},
        canonical_hash=c_hash,
    )
    registry.register_broker(profile)
    engine = BrokerOrderIntentEngine(registry=registry)

    if quantity <= 0.0:
        with pytest.raises(ValidationError):
            make_intent(b_id, symbol, quantity, OrderType.MARKET, side)
    else:
        intent = make_intent(b_id, symbol, quantity, OrderType.MARKET, side)
        res = engine.validate_intent(intent)
        assert res.valid is True


@pytest.mark.parametrize("symbol", SYMBOLS[:6])
@pytest.mark.parametrize("o_type", ORDER_TYPES)
@pytest.mark.parametrize("sl", [None, 10.0, 50.0])
@pytest.mark.parametrize("tp", [None, 20.0, 100.0])
def test_order_intent_engine_sl_tp_matrix(symbol, o_type, sl, tp):
    registry = BrokerCapabilityRegistry()
    b_id, c_hash = compute_broker_profile_id("Deriv", "DERIV", "v3")
    profile = BrokerProfile(
        broker_id=b_id,
        broker_name="Deriv",
        broker_type=BrokerType.DERIV,
        api_version="v3",
        supported_assets=SYMBOLS,
        supported_order_types=[OrderType.MARKET, OrderType.LIMIT],
        supports_streaming=True,
        supports_positions=True,
        supports_history=True,
        metadata={},
        canonical_hash=c_hash,
    )
    registry.register_broker(profile)
    engine = BrokerOrderIntentEngine(registry=registry)

    intent_id, canonical_hash = compute_order_intent_id(b_id, symbol, "BUY", 1.0, o_type.value, "2026-07-31T12:00:00Z")
    intent = BrokerOrderIntent(
        intent_id=intent_id,
        broker_id=b_id,
        symbol=symbol,
        side=OrderSide.BUY,
        quantity=1.0,
        order_type=o_type,
        time_in_force=TimeInForce.GTC,
        stop_loss=sl,
        take_profit=tp,
        comment="SL TP Test",
        metadata={},
        canonical_hash=canonical_hash,
    )
    res = engine.validate_intent(intent)
    if o_type in (OrderType.MARKET, OrderType.LIMIT):
        assert res.valid is True
    else:
        assert res.valid is False
