"""
Project GOAT v0.8 — Test Suite: Execution Core Models & Canonical IDs (Exhaustive Matrix)
"""

import pytest
from pydantic import ValidationError

from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.execution.core.canonical import (
    compute_execution_audit_id,
    compute_execution_decision_id,
    compute_execution_failure_id,
    compute_execution_intent_id,
    compute_execution_lifecycle_id,
    compute_execution_request_id,
    compute_execution_summary_id,
)
from goat.execution.core.enums import AuditEventType, ExecutionFailureCategory, ExecutionState
from goat.execution.core.models import (
    ExecutionAudit,
    ExecutionDecision,
    ExecutionFailure,
    ExecutionIntent,
    ExecutionLifecycle,
    ExecutionRequest,
    ExecutionSummary,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
SIDES = [OrderSide.BUY, OrderSide.SELL]
ORDER_TYPES = [OrderType.MARKET, OrderType.LIMIT]
TIMEFRAMES = [TimeInForce.GTC, TimeInForce.IOC, TimeInForce.FOK]
BROKERS = ["BRK_DERIV", "BRK_DERIV_DEMO", "BRK_DERIV_REAL"]


@pytest.mark.parametrize("symbol,side,order_type,tif", [(sym, s, ot, tif) for sym in SYMBOLS for s in SIDES for ot in ORDER_TYPES for tif in TIMEFRAMES])
def test_execution_intent_model_matrix(symbol, side, order_type, tif):
    intent_id, c_hash = compute_execution_intent_id("SIG_1001", "BRK_DERIV", symbol, side.value, 10.0)
    intent = ExecutionIntent(
        intent_id=intent_id,
        signal_id="SIG_1001",
        sizing_decision_id="SIZ_1001",
        allocation_id="ALL_1001",
        broker_id="BRK_DERIV",
        symbol=symbol,
        side=side,
        quantity=10.0,
        order_type=order_type,
        time_in_force=tif,
        stop_loss=100.0,
        take_profit=150.0,
        status=ExecutionState.CREATED,
        metadata={},
        canonical_hash=c_hash,
    )
    assert intent.intent_id.startswith("EXI_")
    assert intent.symbol == symbol
    assert intent.side == side
    assert intent.order_type == order_type
    assert intent.time_in_force == tif

    with pytest.raises(ValidationError):
        intent.quantity = 99.0


@pytest.mark.parametrize("broker", BROKERS)
@pytest.mark.parametrize("symbol", SYMBOLS[:6])
def test_execution_request_model_matrix(broker, symbol):
    req_id, c_hash = compute_execution_request_id(f"EXI_{symbol}", broker, "2026-07-31T12:00:00Z")
    req = ExecutionRequest(
        request_id=req_id,
        intent_id=f"EXI_{symbol}",
        broker_id=broker,
        payload_dict={"symbol": symbol},
        dispatched_at="2026-07-31T12:00:00Z",
        metadata={},
        canonical_hash=c_hash,
    )
    assert req.request_id.startswith("EXR_")
    assert req.broker_id == broker


@pytest.mark.parametrize("approved", [True, False])
@pytest.mark.parametrize("symbol", SYMBOLS[:6])
def test_execution_decision_model_matrix(approved, symbol):
    dec_id, c_hash = compute_execution_decision_id(f"EXI_{symbol}", approved, "2026-07-31T12:00:00Z")
    decision = ExecutionDecision(
        decision_id=dec_id,
        intent_id=f"EXI_{symbol}",
        approved=approved,
        explanation=f"Decision for {symbol}",
        timestamp="2026-07-31T12:00:00Z",
        metadata={},
        canonical_hash=c_hash,
    )
    assert decision.decision_id.startswith("EXD_")
    assert decision.approved == approved


@pytest.mark.parametrize("state", [ExecutionState.CREATED, ExecutionState.VALIDATED, ExecutionState.READY, ExecutionState.DISPATCHED, ExecutionState.FILLED])
def test_execution_lifecycle_model_matrix(state):
    lc_id, c_hash = compute_execution_lifecycle_id("EXI_1001", state.value, "2026-07-31T12:00:00Z")
    lc = ExecutionLifecycle(
        lifecycle_id=lc_id,
        intent_id="EXI_1001",
        state=state,
        previous_state=None,
        transition_timestamp="2026-07-31T12:00:00Z",
        explanation="State transition",
        metadata={},
        canonical_hash=c_hash,
    )
    assert lc.lifecycle_id.startswith("EXL_")
    assert lc.state == state


@pytest.mark.parametrize("category", [ExecutionFailureCategory.VALIDATION_FAILED, ExecutionFailureCategory.CAPITAL_EXHAUSTED, ExecutionFailureCategory.SESSION_EXPIRED])
def test_execution_failure_model_matrix(category):
    fail_id, c_hash = compute_execution_failure_id("EXI_1001", category.value, "ERR_TEST", "2026-07-31T12:00:00Z")
    failure = ExecutionFailure(
        failure_id=fail_id,
        intent_id="EXI_1001",
        error_code="ERR_TEST",
        category=category,
        reason="Test failure",
        timestamp="2026-07-31T12:00:00Z",
        metadata={},
        canonical_hash=c_hash,
    )
    assert failure.failure_id.startswith("EXF_")
    assert failure.category == category
