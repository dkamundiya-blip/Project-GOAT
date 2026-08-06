"""
Project GOAT v0.8 — Test Suite: Execution Dispatch Engine & Broker Adapter (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.brokers.deriv.adapter import DerivAdapter
from goat.execution.dispatch.engine import ExecutionDispatchEngine
from goat.execution.intents.engine import ExecutionIntentEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
AMOUNTS = [1.0, 5.0, 10.0, 50.0, 100.0]
ORDER_TYPES = [OrderType.MARKET, OrderType.LIMIT]


@pytest.mark.parametrize("symbol,side,amount,order_type", [(sym, s, a, ot) for sym in SYMBOLS for s in SIDES for a in AMOUNTS for ot in ORDER_TYPES])
def test_execution_dispatch_via_deriv_adapter_matrix(symbol, side, amount, order_type):
    adapter = DerivAdapter(app_id=1089, api_token="mock_valid_token_123")
    adapter.connect()

    intent_engine = ExecutionIntentEngine()
    dispatch_engine = ExecutionDispatchEngine(adapter=adapter)

    intent = intent_engine.create_intent(
        signal_id=f"SIG_{symbol}",
        sizing_decision_id="SIZ_1",
        allocation_id="ALL_1",
        broker_id=adapter.broker_id,
        symbol=symbol,
        side=side,
        quantity=amount,
        order_type=order_type,
        time_in_force=TimeInForce.GTC,
    )

    exec_req, fill_result = dispatch_engine.dispatch_intent(intent)
    assert exec_req.request_id.startswith("EXR_")
    assert exec_req.intent_id == intent.intent_id
    assert fill_result["status"] == "FILLED"
    assert fill_result["fill_price"] == amount

    history = dispatch_engine.get_dispatch_history()
    assert len(history) >= 1
    assert history[-1].request_id == exec_req.request_id
