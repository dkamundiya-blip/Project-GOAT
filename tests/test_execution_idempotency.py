"""
Project GOAT v0.8 — Test Suite: Execution Idempotency Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import OrderSide
from goat.execution.idempotency.engine import ExecutionIdempotencyEngine
from goat.execution.intents.engine import ExecutionIntentEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
QUANTITIES = [1.0, 5.0, 10.0, 50.0, 100.0]
BROKERS = ["BRK_DERIV", "BRK_DERIV_REAL"]


@pytest.mark.parametrize("symbol,side,quant,broker", [(sym, s, q, b) for sym in SYMBOLS for s in SIDES for q in QUANTITIES for b in BROKERS])
def test_idempotency_single_execution_lock_matrix(symbol, side, quant, broker):
    intent_engine = ExecutionIntentEngine()
    idempotency = ExecutionIdempotencyEngine()

    intent = intent_engine.create_intent(
        signal_id=f"SIG_{symbol}",
        sizing_decision_id="SIZ_1",
        allocation_id="ALL_1",
        broker_id=broker,
        symbol=symbol,
        side=side,
        quantity=quant,
    )

    # First attempt: must succeed
    first_lock = idempotency.check_and_lock_intent(intent)
    assert first_lock is True
    assert idempotency.is_intent_processed(intent.intent_id) is True

    # Second attempt with identical intent: must fail lock
    second_lock = idempotency.check_and_lock_intent(intent)
    assert second_lock is False

    # Dispatch request registration: first attempt succeeds, duplicate retry fails
    req_id = f"EXR_{intent.intent_id[4:]}"
    assert idempotency.register_dispatch(req_id) is True
    assert idempotency.register_dispatch(req_id) is False
