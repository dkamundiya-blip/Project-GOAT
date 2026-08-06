"""
Project GOAT v0.8 — Test Suite: Execution Intent Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.execution.intents.engine import ExecutionIntentEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
QUANTITIES = [1.0, 5.0, 10.0, 50.0, 100.0]
BROKERS = ["BRK_DERIV", "BRK_DERIV_DEMO", "BRK_DERIV_REAL"]


@pytest.mark.parametrize("symbol,side,quant,broker", [(sym, s, q, b) for sym in SYMBOLS for s in SIDES for q in QUANTITIES for b in BROKERS])
def test_create_execution_intent_matrix(symbol, side, quant, broker):
    engine = ExecutionIntentEngine()
    sig_id = f"SIG_{symbol}_1001"
    siz_id = f"SIZ_{symbol}_1001"
    all_id = f"ALL_{symbol}_1001"

    intent = engine.create_intent(
        signal_id=sig_id,
        sizing_decision_id=siz_id,
        allocation_id=all_id,
        broker_id=broker,
        symbol=symbol,
        side=side,
        quantity=quant,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.GTC,
        stop_loss=90.0,
        take_profit=110.0,
    )

    assert intent.intent_id.startswith("EXI_")
    assert intent.signal_id == sig_id
    assert intent.broker_id == broker
    assert intent.symbol == symbol
    assert intent.side == side
    assert intent.quantity == quant
