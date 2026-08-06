"""
Project GOAT v0.8 — Test Suite: Execution Validation Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import OrderSide
from goat.execution.intents.engine import ExecutionIntentEngine
from goat.execution.validation.engine import ExecutionValidationEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
FAILURES = ["duplicate", "qualified", "risk", "capital", "market", "broker", "freshness"]


@pytest.mark.parametrize("symbol,side", [(sym, s) for sym in SYMBOLS for s in SIDES])
def test_validation_engine_all_passed(symbol, side):
    intent_engine = ExecutionIntentEngine()
    validator = ExecutionValidationEngine()

    intent = intent_engine.create_intent(
        signal_id=f"SIG_{symbol}",
        sizing_decision_id="SIZ_1",
        allocation_id="ALL_1",
        broker_id="BRK_DERIV",
        symbol=symbol,
        side=side,
        quantity=10.0,
    )

    decision = validator.validate_intent(intent)
    assert decision.decision_id.startswith("EXD_")
    assert decision.approved is True
    assert "satisfied all 8 validation prerequisite rules" in decision.explanation


@pytest.mark.parametrize("failed_rule", FAILURES)
@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("side", SIDES)
def test_validation_engine_rule_rejections(failed_rule, symbol, side):
    intent_engine = ExecutionIntentEngine()
    validator = ExecutionValidationEngine()

    intent = intent_engine.create_intent(
        signal_id=f"SIG_{symbol}",
        sizing_decision_id="SIZ_1",
        allocation_id="ALL_1",
        broker_id="BRK_DERIV",
        symbol=symbol,
        side=side,
        quantity=10.0,
    )

    kwargs = {
        "is_qualified": failed_rule != "qualified",
        "is_risk_approved": failed_rule != "risk",
        "has_sufficient_capital": failed_rule != "capital",
        "is_market_active": failed_rule != "market",
        "is_broker_connected": failed_rule != "broker",
        "is_signal_fresh": failed_rule != "freshness",
        "is_duplicate": failed_rule == "duplicate",
    }

    decision = validator.validate_intent(intent, **kwargs)
    assert decision.approved is False
    assert decision.decision_id.startswith("EXD_")
