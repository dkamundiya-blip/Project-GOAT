"""
Project GOAT v0.7 — SQLite Execution Repository

Implements transactional SQLite persistence for Execution Sessions, Execution Events,
Execution History, Execution Contexts, Execution Reports, and Audit Events.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.execution.context import ScientificExecutionContext
from goat.execution.event import ExecutionEvent
from goat.execution.model import ScientificExecutionSession
from goat.execution.reporting import ScientificExecutionReport

EXECUTION_SCHEMA_VERSION = 1


class SQLiteExecutionRepository:
    """Transactional SQLite repository for scientific execution persistence."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Enforce Schema v1 tables."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS execution_schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO execution_schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS execution_sessions (
                    session_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    scientific_fingerprint TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    source_schedule_id TEXT NOT NULL,
                    session_status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS execution_events (
                    event_id TEXT PRIMARY KEY,
                    parent_session_id TEXT NOT NULL,
                    scheduled_task_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    previous_state TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (parent_session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS execution_contexts (
                    session_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS execution_reports (
                    report_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS execution_audit_events (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    event_data TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES execution_sessions(session_id) ON DELETE CASCADE
                );
            """)

    # ------------------------------------------------------------------
    # Session CRUD
    # ------------------------------------------------------------------

    def save_session(self, session: ScientificExecutionSession) -> None:
        """Persist a ScientificExecutionSession transactionally."""
        json_str = session.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO execution_sessions (
                    session_id, canonical_hash, scientific_fingerprint, semantic_version,
                    creation_timestamp, source_schedule_id, session_status, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    session_status = excluded.session_status,
                    json_data = excluded.json_data;
                """,
                (
                    session.session_id,
                    session.canonical_hash,
                    session.scientific_fingerprint,
                    session.semantic_version,
                    session.creation_timestamp,
                    session.source_schedule_id,
                    session.session_status.value,
                    json_str,
                ),
            )

    def get_session(self, session_id: str) -> ScientificExecutionSession | None:
        """Retrieve ScientificExecutionSession by Session ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM execution_sessions WHERE session_id = ?;", (session_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificExecutionSession(**json.loads(row["json_data"]))

    def list_sessions(self) -> list[ScientificExecutionSession]:
        """List all persisted sessions."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM execution_sessions ORDER BY creation_timestamp;")
        return [ScientificExecutionSession(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Event CRUD
    # ------------------------------------------------------------------

    def save_event(self, event: ExecutionEvent) -> None:
        """Persist an ExecutionEvent (append-only semantics)."""
        json_str = event.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO execution_events (
                    event_id, parent_session_id, scheduled_task_id, event_type,
                    event_timestamp, previous_state, current_state, event_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event.event_id,
                    event.parent_session_id,
                    event.scheduled_task_id,
                    event.event_type,
                    event.event_timestamp,
                    event.previous_state.value,
                    event.current_state.value,
                    event.event_hash,
                    json_str,
                ),
            )

    def get_event(self, event_id: str) -> ExecutionEvent | None:
        """Retrieve ExecutionEvent by Event ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM execution_events WHERE event_id = ?;", (event_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ExecutionEvent(**json.loads(row["json_data"]))

    def get_events_for_session(self, session_id: str) -> list[ExecutionEvent]:
        """Retrieve all events for a session, ordered by timestamp."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT json_data FROM execution_events WHERE parent_session_id = ? ORDER BY event_timestamp;",
            (session_id,),
        )
        return [ExecutionEvent(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    def get_events_for_task(self, scheduled_task_id: str) -> list[ExecutionEvent]:
        """Retrieve all events for a scheduled task, ordered by timestamp."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT json_data FROM execution_events WHERE scheduled_task_id = ? ORDER BY event_timestamp;",
            (scheduled_task_id,),
        )
        return [ExecutionEvent(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Context CRUD
    # ------------------------------------------------------------------

    def save_context(self, session_id: str, context: ScientificExecutionContext) -> None:
        """Persist a ScientificExecutionContext."""
        json_str = context.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO execution_contexts (session_id, json_data)
                VALUES (?, ?)
                ON CONFLICT(session_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (session_id, json_str),
            )

    def get_context(self, session_id: str) -> ScientificExecutionContext | None:
        """Retrieve ScientificExecutionContext."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM execution_contexts WHERE session_id = ?;", (session_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificExecutionContext(**json.loads(row["json_data"]))

    # ------------------------------------------------------------------
    # Report CRUD
    # ------------------------------------------------------------------

    def save_report(self, report: ScientificExecutionReport) -> None:
        """Persist a ScientificExecutionReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO execution_reports (report_id, session_id, timestamp, json_data)
                VALUES (?, ?, ?, ?);
                """,
                (report.report_id, report.session_id, report.timestamp, json_str),
            )

    def get_report(self, report_id: str) -> ScientificExecutionReport | None:
        """Retrieve ScientificExecutionReport."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM execution_reports WHERE report_id = ?;", (report_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificExecutionReport(**json.loads(row["json_data"]))

    # ------------------------------------------------------------------
    # Audit Events
    # ------------------------------------------------------------------

    def save_audit_event(
        self,
        session_id: str,
        event_type: str,
        event_timestamp: str,
        event_data: dict[str, Any],
    ) -> None:
        """Persist an audit event."""
        json_str = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO execution_audit_events (session_id, event_type, event_timestamp, event_data)
                VALUES (?, ?, ?, ?);
                """,
                (session_id, event_type, event_timestamp, json_str),
            )

    def get_audit_events(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve all audit events for a session."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT event_type, event_timestamp, event_data FROM execution_audit_events WHERE session_id = ? ORDER BY audit_id;",
            (session_id,),
        )
        return [
            {
                "event_type": row["event_type"],
                "event_timestamp": row["event_timestamp"],
                "event_data": json.loads(row["event_data"]),
            }
            for row in cursor.fetchall()
        ]

    # ------------------------------------------------------------------
    # Export / Import
    # ------------------------------------------------------------------

    def export_session(self, session_id: str) -> dict[str, Any]:
        """Export a complete session with all related artifacts as a dict."""
        session = self.get_session(session_id)
        if session is None:
            raise KeyError(f"Session '{session_id}' not found for export")

        events = self.get_events_for_session(session_id)
        context = self.get_context(session_id)
        audit_events = self.get_audit_events(session_id)

        return {
            "schema_version": EXECUTION_SCHEMA_VERSION,
            "session": json.loads(session.model_dump_json()),
            "events": [json.loads(e.model_dump_json()) for e in events],
            "context": json.loads(context.model_dump_json()) if context else None,
            "audit_events": audit_events,
        }

    def import_session(self, data: dict[str, Any]) -> ScientificExecutionSession:
        """Import a complete session from exported data.

        Args:
            data: Dict from export_session().

        Returns:
            Imported ScientificExecutionSession.

        Raises:
            ValueError: If schema version mismatch.
        """
        if data.get("schema_version") != EXECUTION_SCHEMA_VERSION:
            raise ValueError(
                f"Schema version mismatch: expected {EXECUTION_SCHEMA_VERSION}, "
                f"got {data.get('schema_version')}"
            )

        session = ScientificExecutionSession(**data["session"])
        self.save_session(session)

        for event_data in data.get("events", []):
            event = ExecutionEvent(**event_data)
            self.save_event(event)

        if data.get("context"):
            context = ScientificExecutionContext(**data["context"])
            self.save_context(session.session_id, context)

        return session

    # ------------------------------------------------------------------
    # Integrity verification
    # ------------------------------------------------------------------

    def verify_integrity(self, session_id: str) -> bool:
        """Verify persistence integrity for a session.

        Returns:
            True if events exist and data is consistent.

        Raises:
            ValueError: If integrity check fails.
        """
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session '{session_id}' not found")

        events = self.get_events_for_session(session_id)
        # Verify all events reference the session
        for event in events:
            if event.parent_session_id != session_id:
                raise ValueError(
                    f"Event '{event.event_id}' has parent_session_id "
                    f"'{event.parent_session_id}', expected '{session_id}'"
                )
        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
