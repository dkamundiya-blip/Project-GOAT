"""
Project GOAT v0.7 — SQLite Persistence for Scientific Signal Generation Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- TradingSignalRepository
- SignalPayloadRepository
- SignalLifecycleRepository
- ExecutionReadinessRepository
- SignalAuditRepository
- SignalReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.signals.core.models import (
    ExecutionReadiness,
    SignalAuditRecord,
    SignalLifecycleEvent,
    SignalPayload,
    TradingSignal,
)


def init_signals_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for Scientific Signal Engine."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trading_signals (
                signal_id TEXT PRIMARY KEY,
                qualification_id TEXT NOT NULL,
                simulation_result_id TEXT NOT NULL,
                risk_assessment_id TEXT NOT NULL,
                composite_id TEXT NOT NULL,
                regime_id TEXT NOT NULL,
                instrument TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                recommended_lot_size REAL NOT NULL,
                minimum_lot_size REAL NOT NULL,
                monetary_risk REAL NOT NULL,
                monetary_reward REAL NOT NULL,
                risk_reward_ratio REAL NOT NULL,
                scientific_confidence REAL NOT NULL,
                readiness_level TEXT NOT NULL,
                generation_timestamp TEXT NOT NULL,
                expiration_timestamp TEXT NOT NULL,
                lifecycle_state TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signal_payloads (
                payload_id TEXT PRIMARY KEY,
                signal_id TEXT NOT NULL,
                notification_version TEXT NOT NULL,
                payload_format TEXT NOT NULL,
                payload_data_json TEXT NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (signal_id) REFERENCES trading_signals(signal_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signal_lifecycle_events (
                lifecycle_event_id TEXT PRIMARY KEY,
                signal_id TEXT NOT NULL,
                previous_state TEXT NOT NULL,
                current_state TEXT NOT NULL,
                event_timestamp TEXT NOT NULL,
                triggering_reason TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (signal_id) REFERENCES trading_signals(signal_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_readiness_evaluations (
                readiness_id TEXT PRIMARY KEY,
                signal_id TEXT NOT NULL,
                execution_status TEXT NOT NULL,
                broker_requirements_json TEXT NOT NULL,
                validation_summary TEXT NOT NULL,
                readiness_score REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (signal_id) REFERENCES trading_signals(signal_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signal_audit_records (
                audit_id TEXT PRIMARY KEY,
                signal_id TEXT NOT NULL,
                qualification_reference TEXT NOT NULL,
                simulation_reference TEXT NOT NULL,
                risk_reference TEXT NOT NULL,
                replay_reference TEXT NOT NULL,
                scientific_trace_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (signal_id) REFERENCES trading_signals(signal_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signal_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class TradingSignalRepository:
    """Repository for storing and retrieving TradingSignal models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_signals_db(self.conn)

    def save_signal(self, signal: TradingSignal) -> None:
        dir_val = signal.direction.value if hasattr(signal.direction, "value") else str(signal.direction)
        st_val = signal.lifecycle_state.value if hasattr(signal.lifecycle_state, "value") else str(signal.lifecycle_state)

        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO trading_signals (
                    signal_id, qualification_id, simulation_result_id, risk_assessment_id,
                    composite_id, regime_id, instrument, direction, entry_price,
                    stop_loss, take_profit, recommended_lot_size, minimum_lot_size,
                    monetary_risk, monetary_reward, risk_reward_ratio, scientific_confidence,
                    readiness_level, generation_timestamp, expiration_timestamp, lifecycle_state,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.signal_id,
                    signal.qualification_id,
                    signal.simulation_result_id,
                    signal.risk_assessment_id,
                    signal.composite_id,
                    signal.regime_id,
                    signal.instrument,
                    dir_val,
                    signal.entry_price,
                    signal.stop_loss,
                    signal.take_profit,
                    signal.recommended_lot_size,
                    signal.minimum_lot_size,
                    signal.monetary_risk,
                    signal.monetary_reward,
                    signal.risk_reward_ratio,
                    signal.scientific_confidence,
                    signal.readiness_level,
                    signal.generation_timestamp,
                    signal.expiration_timestamp,
                    st_val,
                    json.dumps(signal.metadata, sort_keys=True),
                    signal.canonical_hash,
                ),
            )

    def get_signal(self, signal_id: str) -> TradingSignal | None:
        cursor = self.conn.execute(
            """
            SELECT signal_id, qualification_id, simulation_result_id, risk_assessment_id,
                   composite_id, regime_id, instrument, direction, entry_price,
                   stop_loss, take_profit, recommended_lot_size, minimum_lot_size,
                   monetary_risk, monetary_reward, risk_reward_ratio, scientific_confidence,
                   readiness_level, generation_timestamp, expiration_timestamp, lifecycle_state,
                   metadata_json, canonical_hash
            FROM trading_signals WHERE signal_id = ?
            """,
            (signal_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return TradingSignal(
            signal_id=row[0],
            qualification_id=row[1],
            simulation_result_id=row[2],
            risk_assessment_id=row[3],
            composite_id=row[4],
            regime_id=row[5],
            instrument=row[6],
            direction=row[7],
            entry_price=row[8],
            stop_loss=row[9],
            take_profit=row[10],
            recommended_lot_size=row[11],
            minimum_lot_size=row[12],
            monetary_risk=row[13],
            monetary_reward=row[14],
            risk_reward_ratio=row[15],
            scientific_confidence=row[16],
            readiness_level=row[17],
            generation_timestamp=row[18],
            expiration_timestamp=row[19],
            lifecycle_state=row[20],
            metadata=json.loads(row[21]),
            canonical_hash=row[22],
        )


class SignalPayloadRepository:
    """Repository for storing and retrieving SignalPayload models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_signals_db(self.conn)

    def save_payload(self, payload: SignalPayload) -> None:
        fmt_val = payload.payload_format.value if hasattr(payload.payload_format, "value") else str(payload.payload_format)
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO signal_payloads (
                    payload_id, signal_id, notification_version, payload_format,
                    payload_data_json, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.payload_id,
                    payload.signal_id,
                    payload.notification_version,
                    fmt_val,
                    json.dumps(payload.payload_data, sort_keys=True),
                    payload.checksum,
                    json.dumps(payload.metadata, sort_keys=True),
                    payload.canonical_hash,
                ),
            )

    def get_payload(self, payload_id: str) -> SignalPayload | None:
        cursor = self.conn.execute(
            """
            SELECT payload_id, signal_id, notification_version, payload_format,
                   payload_data_json, checksum, metadata_json, canonical_hash
            FROM signal_payloads WHERE payload_id = ?
            """,
            (payload_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SignalPayload(
            payload_id=row[0],
            signal_id=row[1],
            notification_version=row[2],
            payload_format=row[3],
            payload_data=json.loads(row[4]),
            checksum=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class SignalLifecycleRepository:
    """Repository for storing and retrieving SignalLifecycleEvent models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_signals_db(self.conn)

    def save_event(self, event: SignalLifecycleEvent) -> None:
        prev_val = event.previous_state.value if hasattr(event.previous_state, "value") else str(event.previous_state)
        curr_val = event.current_state.value if hasattr(event.current_state, "value") else str(event.current_state)

        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO signal_lifecycle_events (
                    lifecycle_event_id, signal_id, previous_state, current_state,
                    event_timestamp, triggering_reason, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.lifecycle_event_id,
                    event.signal_id,
                    prev_val,
                    curr_val,
                    event.event_timestamp,
                    event.triggering_reason,
                    json.dumps(event.metadata, sort_keys=True),
                    event.canonical_hash,
                ),
            )

    def get_event(self, lifecycle_event_id: str) -> SignalLifecycleEvent | None:
        cursor = self.conn.execute(
            """
            SELECT lifecycle_event_id, signal_id, previous_state, current_state,
                   event_timestamp, triggering_reason, metadata_json, canonical_hash
            FROM signal_lifecycle_events WHERE lifecycle_event_id = ?
            """,
            (lifecycle_event_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SignalLifecycleEvent(
            lifecycle_event_id=row[0],
            signal_id=row[1],
            previous_state=row[2],
            current_state=row[3],
            event_timestamp=row[4],
            triggering_reason=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ExecutionReadinessRepository:
    """Repository for storing and retrieving ExecutionReadiness models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_signals_db(self.conn)

    def save_readiness(self, readiness: ExecutionReadiness) -> None:
        st_val = readiness.execution_status.value if hasattr(readiness.execution_status, "value") else str(readiness.execution_status)

        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO execution_readiness_evaluations (
                    readiness_id, signal_id, execution_status, broker_requirements_json,
                    validation_summary, readiness_score, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    readiness.readiness_id,
                    readiness.signal_id,
                    st_val,
                    json.dumps(readiness.broker_requirements, sort_keys=True),
                    readiness.validation_summary,
                    readiness.readiness_score,
                    json.dumps(readiness.metadata, sort_keys=True),
                    readiness.canonical_hash,
                ),
            )

    def get_readiness(self, readiness_id: str) -> ExecutionReadiness | None:
        cursor = self.conn.execute(
            """
            SELECT readiness_id, signal_id, execution_status, broker_requirements_json,
                   validation_summary, readiness_score, metadata_json, canonical_hash
            FROM execution_readiness_evaluations WHERE readiness_id = ?
            """,
            (readiness_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ExecutionReadiness(
            readiness_id=row[0],
            signal_id=row[1],
            execution_status=row[2],
            broker_requirements=json.loads(row[3]),
            validation_summary=row[4],
            readiness_score=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class SignalAuditRepository:
    """Repository for storing and retrieving SignalAuditRecord models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_signals_db(self.conn)

    def save_audit(self, audit: SignalAuditRecord) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO signal_audit_records (
                    audit_id, signal_id, qualification_reference, simulation_reference,
                    risk_reference, replay_reference, scientific_trace_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.audit_id,
                    audit.signal_id,
                    audit.qualification_reference,
                    audit.simulation_reference,
                    audit.risk_reference,
                    audit.replay_reference,
                    json.dumps(audit.scientific_trace, sort_keys=True),
                    json.dumps(audit.metadata, sort_keys=True),
                    audit.canonical_hash,
                ),
            )

    def get_audit(self, audit_id: str) -> SignalAuditRecord | None:
        cursor = self.conn.execute(
            """
            SELECT audit_id, signal_id, qualification_reference, simulation_reference,
                   risk_reference, replay_reference, scientific_trace_json,
                   metadata_json, canonical_hash
            FROM signal_audit_records WHERE audit_id = ?
            """,
            (audit_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SignalAuditRecord(
            audit_id=row[0],
            signal_id=row[1],
            qualification_reference=row[2],
            simulation_reference=row[3],
            risk_reference=row[4],
            replay_reference=row[5],
            scientific_trace=json.loads(row[6]),
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class SignalReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_signals_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO signal_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM signal_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
