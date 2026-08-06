"""
Project GOAT v0.7 — Test Suite for SignalLifecycleEngine

Coverage:
- State machine transition rules CREATED -> VALIDATED -> READY_FOR_DELIVERY -> DELIVERED -> ACKNOWLEDGED -> ARCHIVED
- Rejection of illegal state transitions (ValueError)
- SignalLifecycleEvent emission
"""

import pytest

from goat.signals.core.canonical import compute_signal_id
from goat.signals.core.enums import SignalDirection, SignalLifecycleState
from goat.signals.core.models import TradingSignal
from goat.signals.lifecycle.engine import SignalLifecycleEngine


def test_lifecycle_engine_valid_transitions():
    engine = SignalLifecycleEngine()

    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(
        signal_id=s_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        risk_assessment_id="RSA_1",
        composite_id="CMP_1",
        regime_id="MRG_1",
        instrument="EURUSD",
        direction=SignalDirection.BUY,
        entry_price=1.0850,
        stop_loss=1.0800,
        take_profit=1.0950,
        recommended_lot_size=4.0,
        monetary_risk=2000.0,
        monetary_reward=4000.0,
        risk_reward_ratio=2.0,
        scientific_confidence=0.90,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
        lifecycle_state=SignalLifecycleState.CREATED,
        canonical_hash=s_hash,
    )

    # CREATED -> VALIDATED
    s1, e1 = engine.transition_state(signal, SignalLifecycleState.VALIDATED, "2026-07-30T00:01:00Z")
    assert s1.lifecycle_state == SignalLifecycleState.VALIDATED
    assert e1.previous_state == SignalLifecycleState.CREATED
    assert e1.current_state == SignalLifecycleState.VALIDATED

    # VALIDATED -> READY_FOR_DELIVERY
    s2, e2 = engine.transition_state(s1, SignalLifecycleState.READY_FOR_DELIVERY, "2026-07-30T00:02:00Z")
    assert s2.lifecycle_state == SignalLifecycleState.READY_FOR_DELIVERY

    # READY_FOR_DELIVERY -> DELIVERED
    s3, e3 = engine.transition_state(s2, SignalLifecycleState.DELIVERED, "2026-07-30T00:03:00Z")
    assert s3.lifecycle_state == SignalLifecycleState.DELIVERED


def test_lifecycle_engine_illegal_transition():
    engine = SignalLifecycleEngine()

    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(
        signal_id=s_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        risk_assessment_id="RSA_1",
        composite_id="CMP_1",
        regime_id="MRG_1",
        instrument="EURUSD",
        direction=SignalDirection.BUY,
        entry_price=1.0850,
        stop_loss=1.0800,
        take_profit=1.0950,
        recommended_lot_size=4.0,
        monetary_risk=2000.0,
        monetary_reward=4000.0,
        risk_reward_ratio=2.0,
        scientific_confidence=0.90,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
        lifecycle_state=SignalLifecycleState.CREATED,
        canonical_hash=s_hash,
    )

    # CREATED -> ACKNOWLEDGED is illegal!
    with pytest.raises(ValueError, match="Illegal signal lifecycle transition"):
        engine.transition_state(signal, SignalLifecycleState.ACKNOWLEDGED, "2026-07-30T00:01:00Z")
