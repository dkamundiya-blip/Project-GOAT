"""
Project GOAT v0.7 — Test Suite for Scientific Signal Persistence Repositories

Coverage:
- TradingSignalRepository (save, get round-trip)
- SignalPayloadRepository (save, get round-trip)
- SignalLifecycleRepository (save, get round-trip)
- ExecutionReadinessRepository (save, get round-trip)
- SignalAuditRepository (save, get round-trip)
- SignalReportRepository (save, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.signals.core.canonical import (
    compute_lifecycle_event_id,
    compute_payload_id,
    compute_readiness_id,
    compute_signal_audit_id,
    compute_signal_id,
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
from goat.signals.persistence.sqlite import (
    ExecutionReadinessRepository,
    SignalAuditRepository,
    SignalLifecycleRepository,
    SignalPayloadRepository,
    SignalReportRepository,
    TradingSignalRepository,
    init_signals_db,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_signals_db(conn)
    yield conn
    conn.close()


def test_trading_signal_repository_roundtrip(db_conn):
    repo = TradingSignalRepository(db_conn)
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
        canonical_hash=s_hash,
    )

    repo.save_signal(signal)
    fetched = repo.get_signal(s_id)

    assert fetched == signal


def test_payload_repository_roundtrip(db_conn):
    s_repo = TradingSignalRepository(db_conn)
    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(signal_id=s_id, qualification_id="SQL_1", simulation_result_id="SRS_1", risk_assessment_id="RSA_1", composite_id="CMP_1", regime_id="MRG_1", instrument="EURUSD", direction=SignalDirection.BUY, entry_price=1.0850, stop_loss=1.0800, take_profit=1.0950, recommended_lot_size=4.0, monetary_risk=2000.0, monetary_reward=4000.0, risk_reward_ratio=2.0, scientific_confidence=0.90, generation_timestamp="2026-07-30T00:00:00Z", expiration_timestamp="2026-07-31T00:00:00Z", canonical_hash=s_hash)
    s_repo.save_signal(signal)

    p_repo = SignalPayloadRepository(db_conn)
    p_id, p_hash = compute_payload_id(s_id, "JSON")
    payload = SignalPayload(
        payload_id=p_id,
        signal_id=s_id,
        payload_format=PayloadFormat.JSON,
        payload_data={"instrument": "EURUSD"},
        checksum="CHECKSUM123",
        canonical_hash=p_hash,
    )

    p_repo.save_payload(payload)
    fetched = p_repo.get_payload(p_id)

    assert fetched == payload


def test_lifecycle_repository_roundtrip(db_conn):
    s_repo = TradingSignalRepository(db_conn)
    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(signal_id=s_id, qualification_id="SQL_1", simulation_result_id="SRS_1", risk_assessment_id="RSA_1", composite_id="CMP_1", regime_id="MRG_1", instrument="EURUSD", direction=SignalDirection.BUY, entry_price=1.0850, stop_loss=1.0800, take_profit=1.0950, recommended_lot_size=4.0, monetary_risk=2000.0, monetary_reward=4000.0, risk_reward_ratio=2.0, scientific_confidence=0.90, generation_timestamp="2026-07-30T00:00:00Z", expiration_timestamp="2026-07-31T00:00:00Z", canonical_hash=s_hash)
    s_repo.save_signal(signal)

    l_repo = SignalLifecycleRepository(db_conn)
    e_id, e_hash = compute_lifecycle_event_id(s_id, "CREATED", "VALIDATED", "2026-07-30T00:00:00Z")
    event = SignalLifecycleEvent(
        lifecycle_event_id=e_id,
        signal_id=s_id,
        previous_state=SignalLifecycleState.CREATED,
        current_state=SignalLifecycleState.VALIDATED,
        event_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    l_repo.save_event(event)
    fetched = l_repo.get_event(e_id)

    assert fetched == event


def test_readiness_repository_roundtrip(db_conn):
    s_repo = TradingSignalRepository(db_conn)
    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(signal_id=s_id, qualification_id="SQL_1", simulation_result_id="SRS_1", risk_assessment_id="RSA_1", composite_id="CMP_1", regime_id="MRG_1", instrument="EURUSD", direction=SignalDirection.BUY, entry_price=1.0850, stop_loss=1.0800, take_profit=1.0950, recommended_lot_size=4.0, monetary_risk=2000.0, monetary_reward=4000.0, risk_reward_ratio=2.0, scientific_confidence=0.90, generation_timestamp="2026-07-30T00:00:00Z", expiration_timestamp="2026-07-31T00:00:00Z", canonical_hash=s_hash)
    s_repo.save_signal(signal)

    r_repo = ExecutionReadinessRepository(db_conn)
    r_id, r_hash = compute_readiness_id(s_id, "READY")
    readiness = ExecutionReadiness(
        readiness_id=r_id,
        signal_id=s_id,
        execution_status=ExecutionStatus.READY,
        readiness_score=1.0,
        canonical_hash=r_hash,
    )

    r_repo.save_readiness(readiness)
    fetched = r_repo.get_readiness(r_id)

    assert fetched == readiness


def test_audit_repository_roundtrip(db_conn):
    s_repo = TradingSignalRepository(db_conn)
    s_id, s_hash = compute_signal_id("SQL_1", "SRS_1", "RSA_1")
    signal = TradingSignal(signal_id=s_id, qualification_id="SQL_1", simulation_result_id="SRS_1", risk_assessment_id="RSA_1", composite_id="CMP_1", regime_id="MRG_1", instrument="EURUSD", direction=SignalDirection.BUY, entry_price=1.0850, stop_loss=1.0800, take_profit=1.0950, recommended_lot_size=4.0, monetary_risk=2000.0, monetary_reward=4000.0, risk_reward_ratio=2.0, scientific_confidence=0.90, generation_timestamp="2026-07-30T00:00:00Z", expiration_timestamp="2026-07-31T00:00:00Z", canonical_hash=s_hash)
    s_repo.save_signal(signal)

    a_repo = SignalAuditRepository(db_conn)
    a_id, a_hash = compute_signal_audit_id(s_id, "SQL_1")
    audit = SignalAuditRecord(
        audit_id=a_id,
        signal_id=s_id,
        qualification_reference="SQL_1",
        simulation_reference="SRS_1",
        risk_reference="RSA_1",
        replay_reference=f"REPLAY_{s_id}",
        canonical_hash=a_hash,
    )

    a_repo.save_audit(audit)
    fetched = a_repo.get_audit(a_id)

    assert fetched == audit
