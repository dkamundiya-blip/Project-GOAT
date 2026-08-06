"""
Project GOAT v0.8 — Production Execution Persistence Repositories

SQLite repositories for persisting Execution models with WAL mode,
foreign keys (PRAGMA foreign_keys = ON), and deterministic serialization.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.execution.core.enums import AuditEventType, ExecutionFailureCategory, ExecutionState
from goat.execution.core.models import (
    ExecutionAudit,
    ExecutionDecision,
    ExecutionFailure,
    ExecutionIntent,
    ExecutionLifecycle,
)


def init_execution_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database for Production Execution Engine with foreign keys enabled."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_intents (
                intent_id TEXT PRIMARY KEY,
                signal_id TEXT NOT NULL,
                sizing_decision_id TEXT NOT NULL,
                allocation_id TEXT NOT NULL,
                broker_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                order_type TEXT NOT NULL,
                time_in_force TEXT NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                status TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_decisions (
                decision_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                approved INTEGER NOT NULL,
                explanation TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (intent_id) REFERENCES execution_intents(intent_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_lifecycles (
                lifecycle_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                state TEXT NOT NULL,
                previous_state TEXT,
                transition_timestamp TEXT NOT NULL,
                explanation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (intent_id) REFERENCES execution_intents(intent_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_audits (
                audit_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (intent_id) REFERENCES execution_intents(intent_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_failures (
                failure_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL,
                error_code TEXT NOT NULL,
                category TEXT NOT NULL,
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (intent_id) REFERENCES execution_intents(intent_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                markdown_content TEXT NOT NULL,
                json_content TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )

    return conn


class ExecutionIntentRepository:
    """SQLite repository for ExecutionIntent."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, intent: ExecutionIntent) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO execution_intents (
                    intent_id, signal_id, sizing_decision_id, allocation_id, broker_id,
                    symbol, side, quantity, order_type, time_in_force, stop_loss,
                    take_profit, status, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    intent.intent_id,
                    intent.signal_id,
                    intent.sizing_decision_id,
                    intent.allocation_id,
                    intent.broker_id,
                    intent.symbol,
                    intent.side.value,
                    intent.quantity,
                    intent.order_type.value,
                    intent.time_in_force.value,
                    intent.stop_loss,
                    intent.take_profit,
                    intent.status.value,
                    json.dumps(intent.metadata, sort_keys=True),
                    intent.canonical_hash,
                ),
            )

    def get_by_id(self, intent_id: str) -> ExecutionIntent | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM execution_intents WHERE intent_id = ?;", (intent_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return ExecutionIntent(
            intent_id=row[0],
            signal_id=row[1],
            sizing_decision_id=row[2],
            allocation_id=row[3],
            broker_id=row[4],
            symbol=row[5],
            side=OrderSide(row[6]),
            quantity=row[7],
            order_type=OrderType(row[8]),
            time_in_force=TimeInForce(row[9]),
            stop_loss=row[10],
            take_profit=row[11],
            status=ExecutionState(row[12]),
            metadata=json.loads(row[13]),
            canonical_hash=row[14],
        )


class ExecutionDecisionRepository:
    """SQLite repository for ExecutionDecision."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, decision: ExecutionDecision) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO execution_decisions (
                    decision_id, intent_id, approved, explanation, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    decision.decision_id,
                    decision.intent_id,
                    1 if decision.approved else 0,
                    decision.explanation,
                    decision.timestamp,
                    json.dumps(decision.metadata, sort_keys=True),
                    decision.canonical_hash,
                ),
            )

    def get_by_id(self, decision_id: str) -> ExecutionDecision | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM execution_decisions WHERE decision_id = ?;", (decision_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return ExecutionDecision(
            decision_id=row[0],
            intent_id=row[1],
            approved=bool(row[2]),
            explanation=row[3],
            timestamp=row[4],
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class ExecutionLifecycleRepository:
    """SQLite repository for ExecutionLifecycle."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, entry: ExecutionLifecycle) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO execution_lifecycles (
                    lifecycle_id, intent_id, state, previous_state, transition_timestamp, explanation, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    entry.lifecycle_id,
                    entry.intent_id,
                    entry.state.value,
                    entry.previous_state.value if entry.previous_state else None,
                    entry.transition_timestamp,
                    entry.explanation,
                    json.dumps(entry.metadata, sort_keys=True),
                    entry.canonical_hash,
                ),
            )

    def get_by_id(self, lifecycle_id: str) -> ExecutionLifecycle | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM execution_lifecycles WHERE lifecycle_id = ?;", (lifecycle_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return ExecutionLifecycle(
            lifecycle_id=row[0],
            intent_id=row[1],
            state=ExecutionState(row[2]),
            previous_state=ExecutionState(row[3]) if row[3] else None,
            transition_timestamp=row[4],
            explanation=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ExecutionAuditRepository:
    """SQLite repository for ExecutionAudit."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, audit: ExecutionAudit) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO execution_audits (
                    audit_id, intent_id, event_type, timestamp, details, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    audit.audit_id,
                    audit.intent_id,
                    audit.event_type.value,
                    audit.timestamp,
                    audit.details,
                    json.dumps(audit.metadata, sort_keys=True),
                    audit.canonical_hash,
                ),
            )

    def get_by_id(self, audit_id: str) -> ExecutionAudit | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM execution_audits WHERE audit_id = ?;", (audit_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return ExecutionAudit(
            audit_id=row[0],
            intent_id=row[1],
            event_type=AuditEventType(row[2]),
            timestamp=row[3],
            details=row[4],
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class ExecutionFailureRepository:
    """SQLite repository for ExecutionFailure."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, failure: ExecutionFailure) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO execution_failures (
                    failure_id, intent_id, error_code, category, reason, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    failure.failure_id,
                    failure.intent_id,
                    failure.error_code,
                    failure.category.value,
                    failure.reason,
                    failure.timestamp,
                    json.dumps(failure.metadata, sort_keys=True),
                    failure.canonical_hash,
                ),
            )

    def get_by_id(self, failure_id: str) -> ExecutionFailure | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM execution_failures WHERE failure_id = ?;", (failure_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return ExecutionFailure(
            failure_id=row[0],
            intent_id=row[1],
            error_code=row[2],
            category=ExecutionFailureCategory(row[3]),
            reason=row[4],
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ExecutionReportRepository:
    """SQLite repository for storing generated Execution reports."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_report(
        self,
        report_id: str,
        report_type: str,
        timestamp: str,
        markdown_content: str,
        json_content: str,
        canonical_hash: str,
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO execution_reports (
                    report_id, report_type, timestamp, markdown_content, json_content, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    report_id,
                    report_type,
                    timestamp,
                    markdown_content,
                    json_content,
                    canonical_hash,
                ),
            )
