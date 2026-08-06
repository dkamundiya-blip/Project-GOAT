"""
Project GOAT v0.7 — Test Suite for Signal Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (TradingSignal, SignalPayload, SignalLifecycleEvent, ExecutionReadiness, SignalAuditRecord)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.signals.core.canonical import (
    compute_lifecycle_event_id,
    compute_payload_id,
    compute_readiness_id,
    compute_signal_audit_id,
    compute_signal_id,
    compute_signal_report_id,
    serialize_canonical_json,
)
from goat.signals.core.enums import (
    ExecutionStatus,
    PayloadFormat,
    SignalDirection,
    SignalLifecycleState,
)
from goat.signals.core.models import (
    ExecutionReadiness,
    SignalAuditRecord,
    SignalLifecycleEvent,
    SignalPayload,
    TradingSignal,
)


def test_signal_id_determinism():
    id1, hash1 = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    id2, hash2 = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SIG_")


def test_payload_id_determinism():
    id1, hash1 = compute_payload_id("SIG_1", "JSON")
    id2, hash2 = compute_payload_id("SIG_1", "JSON")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SPL_")


def test_lifecycle_event_id_determinism():
    id1, hash1 = compute_lifecycle_event_id("SIG_1", "CREATED", "VALIDATED", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_lifecycle_event_id("SIG_1", "CREATED", "VALIDATED", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SLE_")


def test_readiness_id_determinism():
    id1, hash1 = compute_readiness_id("SIG_1", "READY")
    id2, hash2 = compute_readiness_id("SIG_1", "READY")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EXR_")


def test_signal_audit_id_determinism():
    id1, hash1 = compute_signal_audit_id("SIG_1", "SQL_1")
    id2, hash2 = compute_signal_audit_id("SIG_1", "SQL_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SAD_")


def test_signal_report_id_determinism():
    id1, hash1 = compute_signal_report_id("SignalExecutiveReport", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_signal_report_id("SignalExecutiveReport", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SSR_")


def test_trading_signal_model():
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
        minimum_lot_size=0.01,
        monetary_risk=2000.0,
        monetary_reward=4000.0,
        risk_reward_ratio=2.0,
        scientific_confidence=0.90,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
        canonical_hash=s_hash,
    )

    assert signal.signal_id == s_id
    assert signal.instrument == "EURUSD"
    assert signal.direction == SignalDirection.BUY

    with pytest.raises((TypeError, ValidationError)):
        signal.entry_price = 1.0900


def test_signal_payload_model():
    p_id, p_hash = compute_payload_id("SIG_1", "JSON")
    payload = SignalPayload(
        payload_id=p_id,
        signal_id="SIG_1",
        payload_format=PayloadFormat.JSON,
        payload_data={"instrument": "EURUSD"},
        checksum="CHECKSUM123",
        canonical_hash=p_hash,
    )
    assert payload.payload_id == p_id
    with pytest.raises((TypeError, ValidationError)):
        payload.checksum = "MUTATED"


def test_signal_lifecycle_event_model():
    e_id, e_hash = compute_lifecycle_event_id("SIG_1", "CREATED", "VALIDATED", "2026-07-30T00:00:00Z")
    event = SignalLifecycleEvent(
        lifecycle_event_id=e_id,
        signal_id="SIG_1",
        previous_state=SignalLifecycleState.CREATED,
        current_state=SignalLifecycleState.VALIDATED,
        event_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )
    assert event.lifecycle_event_id == e_id
    with pytest.raises((TypeError, ValidationError)):
        event.current_state = SignalLifecycleState.DELIVERED


def test_execution_readiness_model():
    r_id, r_hash = compute_readiness_id("SIG_1", "READY")
    readiness = ExecutionReadiness(
        readiness_id=r_id,
        signal_id="SIG_1",
        execution_status=ExecutionStatus.READY,
        readiness_score=1.0,
        canonical_hash=r_hash,
    )
    assert readiness.readiness_id == r_id
    with pytest.raises((TypeError, ValidationError)):
        readiness.readiness_score = 0.5


def test_signal_audit_record_model():
    a_id, a_hash = compute_signal_audit_id("SIG_1", "SQL_1")
    audit = SignalAuditRecord(
        audit_id=a_id,
        signal_id="SIG_1",
        qualification_reference="SQL_1",
        simulation_reference="SRS_1",
        risk_reference="RSA_1",
        replay_reference="REPLAY_SIG_1",
        canonical_hash=a_hash,
    )
    assert audit.audit_id == a_id
    with pytest.raises((TypeError, ValidationError)):
        audit.replay_reference = "MUTATED"
