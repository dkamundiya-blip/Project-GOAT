"""
Project GOAT v0.8 — Step 7.6 Trade Tracking Engine Dedicated Unit Tests
"""

import pytest

from goat.lifecycle.core.enums import TradeState
from goat.lifecycle.tracking.engine import TradeTrackingEngine


def test_trade_tracking_engine_create():
    engine = TradeTrackingEngine()
    lifecycle = engine.create_lifecycle("EXI_1234567890ABCDEF", "EURUSD", "BUY", 1.0, "2026-08-01T00:00:00Z")
    assert lifecycle.current_state == TradeState.CREATED
    assert lifecycle.symbol == "EURUSD"
    assert lifecycle.quantity == 1.0


def test_trade_tracking_engine_legal_transitions():
    engine = TradeTrackingEngine()
    lifecycle = engine.create_lifecycle("EXI_1234567890ABCDEF", "EURUSD", "BUY", 1.0, "2026-08-01T00:00:00Z")

    l1, t1 = engine.transition_state(lifecycle.lifecycle_id, TradeState.SUBMITTED, "2026-08-01T00:00:01Z")
    assert l1.current_state == TradeState.SUBMITTED

    l2, t2 = engine.transition_state(lifecycle.lifecycle_id, TradeState.ACKNOWLEDGED, "2026-08-01T00:00:02Z")
    assert l2.current_state == TradeState.ACKNOWLEDGED

    l3, t3 = engine.transition_state(lifecycle.lifecycle_id, TradeState.FILLED, "2026-08-01T00:00:03Z")
    assert l3.current_state == TradeState.FILLED

    l4, t4 = engine.transition_state(lifecycle.lifecycle_id, TradeState.OPEN, "2026-08-01T00:00:04Z")
    assert l4.current_state == TradeState.OPEN

    l5, t5 = engine.transition_state(lifecycle.lifecycle_id, TradeState.SL_UPDATED, "2026-08-01T00:00:05Z")
    assert l5.current_state == TradeState.SL_UPDATED

    l6, t6 = engine.transition_state(lifecycle.lifecycle_id, TradeState.CLOSED, "2026-08-01T00:00:06Z")
    assert l6.current_state == TradeState.CLOSED
    assert l6.closed_at == "2026-08-01T00:00:06Z"


def test_trade_tracking_engine_illegal_transitions():
    engine = TradeTrackingEngine()
    lifecycle = engine.create_lifecycle("EXI_1234567890ABCDEF", "EURUSD", "BUY", 1.0, "2026-08-01T00:00:00Z")

    # CREATED -> OPEN is illegal!
    with pytest.raises(ValueError, match="Illegal state transition"):
        engine.transition_state(lifecycle.lifecycle_id, TradeState.OPEN, "2026-08-01T00:00:01Z")

    # CREATED -> CLOSED is illegal!
    with pytest.raises(ValueError, match="Illegal state transition"):
        engine.transition_state(lifecycle.lifecycle_id, TradeState.CLOSED, "2026-08-01T00:00:01Z")

    # Move to terminal state CANCELLED
    l1, _ = engine.transition_state(lifecycle.lifecycle_id, TradeState.CANCELLED, "2026-08-01T00:00:01Z")
    assert l1.current_state == TradeState.CANCELLED

    # Transition from CANCELLED to anything is illegal!
    with pytest.raises(ValueError, match="Illegal state transition"):
        engine.transition_state(lifecycle.lifecycle_id, TradeState.OPEN, "2026-08-01T00:00:02Z")


@pytest.mark.parametrize("state_from", list(TradeState))
@pytest.mark.parametrize("state_to", list(TradeState))
def test_all_state_transitions_matrix(state_from, state_to):
    engine = TradeTrackingEngine()
    # Check validate_transition method
    isValid = engine.validate_transition(state_from, state_to)
    if state_from in {TradeState.CLOSED, TradeState.CANCELLED, TradeState.REJECTED, TradeState.FAILED}:
        assert not isValid
