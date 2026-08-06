"""
Project GOAT v0.8 — Trade Lifecycle Persistence Repositories

Implements transactional SQLite persistence for:
- TradeLifecycleRepository
- TradeEventRepository
- BrokerExecutionRepository
- LifecycleAuditRepository
- LifecycleReportRepository

Enforces WAL journal mode, foreign key constraints, replayability, and deterministic serialization.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.lifecycle.core.models import (
    BrokerExecution,
    LifecycleAudit,
    LifecycleTransition,
    PositionSnapshot,
    TradeEvent,
    TradeLifecycle,
    TradeStateRecord,
)

LIFECYCLE_SCHEMA_VERSION = 1


class SQLiteLifecycleRepository:
    """Transactional SQLite WAL repository managing trade lifecycle subsystem entities."""

    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Initialize database schema with versioning and foreign keys."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS lifecycle_schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO lifecycle_schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS trade_lifecycles (
                    lifecycle_id TEXT PRIMARY KEY,
                    intent_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    position_id TEXT NOT NULL,
                    broker_execution_id TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    closed_at TEXT,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS trade_events (
                    event_id TEXT PRIMARY KEY,
                    lifecycle_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (lifecycle_id) REFERENCES trade_lifecycles(lifecycle_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS broker_executions (
                    execution_id TEXT PRIMARY KEY,
                    intent_id TEXT NOT NULL,
                    broker_order_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS lifecycle_transitions (
                    transition_id TEXT PRIMARY KEY,
                    lifecycle_id TEXT NOT NULL,
                    from_state TEXT NOT NULL,
                    to_state TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (lifecycle_id) REFERENCES trade_lifecycles(lifecycle_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS lifecycle_audits (
                    audit_id TEXT PRIMARY KEY,
                    lifecycle_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    new_state TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (lifecycle_id) REFERENCES trade_lifecycles(lifecycle_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS lifecycle_reports (
                    report_id TEXT PRIMARY KEY,
                    lifecycle_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );
            """)

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # TradeLifecycle Operations
    # ------------------------------------------------------------------

    def save_lifecycle(self, lifecycle: TradeLifecycle) -> None:
        json_str = lifecycle.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO trade_lifecycles (
                    lifecycle_id, intent_id, symbol, side, quantity, position_id,
                    broker_execution_id, current_state, created_at, updated_at,
                    closed_at, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(lifecycle_id) DO UPDATE SET
                    position_id=excluded.position_id,
                    broker_execution_id=excluded.broker_execution_id,
                    current_state=excluded.current_state,
                    updated_at=excluded.updated_at,
                    closed_at=excluded.closed_at,
                    json_data=excluded.json_data
                """,
                (
                    lifecycle.lifecycle_id,
                    lifecycle.intent_id,
                    lifecycle.symbol,
                    lifecycle.side,
                    lifecycle.quantity,
                    lifecycle.position_id,
                    lifecycle.broker_execution_id,
                    lifecycle.current_state.value if hasattr(lifecycle.current_state, "value") else str(lifecycle.current_state),
                    lifecycle.created_at,
                    lifecycle.updated_at,
                    lifecycle.closed_at,
                    lifecycle.canonical_hash,
                    json_str,
                ),
            )

    def get_lifecycle(self, lifecycle_id: str) -> TradeLifecycle | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM trade_lifecycles WHERE lifecycle_id = ?",
            (lifecycle_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return TradeLifecycle.model_validate_json(row["json_data"])

    def get_all_lifecycles(self) -> list[TradeLifecycle]:
        cursor = self._conn.execute("SELECT json_data FROM trade_lifecycles ORDER BY created_at ASC")
        return [TradeLifecycle.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # TradeEvent Operations
    # ------------------------------------------------------------------

    def save_event(self, event: TradeEvent) -> None:
        json_str = event.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO trade_events (
                    event_id, lifecycle_id, event_type, timestamp, details,
                    canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.lifecycle_id,
                    event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
                    event.timestamp,
                    event.details,
                    event.canonical_hash,
                    json_str,
                ),
            )

    def get_events(self, lifecycle_id: str) -> list[TradeEvent]:
        cursor = self._conn.execute(
            "SELECT json_data FROM trade_events WHERE lifecycle_id = ? ORDER BY timestamp ASC",
            (lifecycle_id,),
        )
        return [TradeEvent.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # BrokerExecution Operations
    # ------------------------------------------------------------------

    def save_broker_execution(self, execution: BrokerExecution) -> None:
        json_str = execution.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO broker_executions (
                    execution_id, intent_id, broker_order_id, symbol, side,
                    quantity, price, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution.execution_id,
                    execution.intent_id,
                    execution.broker_order_id,
                    execution.symbol,
                    execution.side,
                    execution.quantity,
                    execution.price,
                    execution.timestamp,
                    execution.canonical_hash,
                    json_str,
                ),
            )

    def get_broker_execution(self, execution_id: str) -> BrokerExecution | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM broker_executions WHERE execution_id = ?",
            (execution_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return BrokerExecution.model_validate_json(row["json_data"])

    # ------------------------------------------------------------------
    # Transition & Audit Operations
    # ------------------------------------------------------------------

    def save_transition(self, transition: LifecycleTransition) -> None:
        json_str = transition.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO lifecycle_transitions (
                    transition_id, lifecycle_id, from_state, to_state, timestamp,
                    canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transition.transition_id,
                    transition.lifecycle_id,
                    transition.from_state.value if hasattr(transition.from_state, "value") else str(transition.from_state),
                    transition.to_state.value if hasattr(transition.to_state, "value") else str(transition.to_state),
                    transition.timestamp,
                    transition.canonical_hash,
                    json_str,
                ),
            )

    def save_audit(self, audit: LifecycleAudit) -> None:
        json_str = audit.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO lifecycle_audits (
                    audit_id, lifecycle_id, event_type, new_state, timestamp,
                    canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.audit_id,
                    audit.lifecycle_id,
                    audit.event_type.value if hasattr(audit.event_type, "value") else str(audit.event_type),
                    audit.new_state.value if hasattr(audit.new_state, "value") else str(audit.new_state),
                    audit.timestamp,
                    audit.canonical_hash,
                    json_str,
                ),
            )

    def get_audits(self, lifecycle_id: str) -> list[LifecycleAudit]:
        cursor = self._conn.execute(
            "SELECT json_data FROM lifecycle_audits WHERE lifecycle_id = ? ORDER BY timestamp ASC",
            (lifecycle_id,),
        )
        return [LifecycleAudit.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Report Operations
    # ------------------------------------------------------------------

    def save_report(self, report_id: str, lifecycle_id: str, report_type: str, timestamp: str, content: str, json_data: dict[str, Any]) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO lifecycle_reports (
                    report_id, lifecycle_id, report_type, timestamp, content, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    lifecycle_id,
                    report_type,
                    timestamp,
                    content,
                    json.dumps(json_data, sort_keys=True),
                ),
            )


# Named repository exports mapped to the unified SQLite WAL repository
class TradeLifecycleRepository(SQLiteLifecycleRepository):
    pass

class TradeEventRepository(SQLiteLifecycleRepository):
    pass

class BrokerExecutionRepository(SQLiteLifecycleRepository):
    pass

class LifecycleAuditRepository(SQLiteLifecycleRepository):
    pass

class LifecycleReportRepository(SQLiteLifecycleRepository):
    pass
