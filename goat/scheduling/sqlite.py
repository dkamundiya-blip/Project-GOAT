"""
Project GOAT v0.7 — SQLite Scheduling Repository

Implements transactional SQLite persistence for Research Schedules, Scheduled Tasks,
Scheduling Contexts, Scheduling Reports, Coordinator State, and Audit Events.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.scheduling.context import ScientificSchedulingContext
from goat.scheduling.model import ResearchSchedule
from goat.scheduling.reporting import ScientificSchedulingReport
from goat.scheduling.task import ScheduledTask

SCHEDULING_SCHEMA_VERSION = 1


class SQLiteSchedulingRepository:
    """Transactional SQLite repository for scientific scheduling persistence."""

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
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS research_schedules (
                    schedule_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    scientific_fingerprint TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    schedule_status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    task_schedule_id TEXT PRIMARY KEY,
                    parent_schedule_id TEXT NOT NULL,
                    source_plan_task_id TEXT NOT NULL,
                    execution_position INTEGER NOT NULL,
                    execution_state TEXT NOT NULL,
                    task_schedule_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (parent_schedule_id) REFERENCES research_schedules(schedule_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS scheduling_contexts (
                    schedule_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (schedule_id) REFERENCES research_schedules(schedule_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS scheduling_reports (
                    report_id TEXT PRIMARY KEY,
                    schedule_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (schedule_id) REFERENCES research_schedules(schedule_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS coordinator_state (
                    merged_schedule_id TEXT PRIMARY KEY,
                    source_schedule_ids TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (merged_schedule_id) REFERENCES research_schedules(schedule_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    event_data TEXT NOT NULL,
                    FOREIGN KEY (schedule_id) REFERENCES research_schedules(schedule_id) ON DELETE CASCADE
                );
            """)

    # ------------------------------------------------------------------
    # Research Schedule CRUD
    # ------------------------------------------------------------------

    def save_schedule(self, schedule: ResearchSchedule) -> None:
        """Persist a ResearchSchedule transactionally."""
        json_str = schedule.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO research_schedules (
                    schedule_id, canonical_hash, scientific_fingerprint, semantic_version,
                    creation_timestamp, schedule_status, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(schedule_id) DO UPDATE SET
                    schedule_status = excluded.schedule_status,
                    json_data = excluded.json_data;
                """,
                (
                    schedule.schedule_id,
                    schedule.canonical_hash,
                    schedule.scientific_fingerprint,
                    schedule.semantic_version,
                    schedule.creation_timestamp,
                    schedule.schedule_status.value,
                    json_str,
                ),
            )

    def get_schedule(self, schedule_id: str) -> ResearchSchedule | None:
        """Retrieve ResearchSchedule by Schedule ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM research_schedules WHERE schedule_id = ?;", (schedule_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ResearchSchedule(**json.loads(row["json_data"]))

    def list_schedules(self) -> list[ResearchSchedule]:
        """List all persisted schedules."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM research_schedules ORDER BY creation_timestamp;")
        return [ResearchSchedule(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Scheduled Task CRUD
    # ------------------------------------------------------------------

    def save_task(self, task: ScheduledTask) -> None:
        """Persist a ScheduledTask."""
        json_str = task.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO scheduled_tasks (
                    task_schedule_id, parent_schedule_id, source_plan_task_id,
                    execution_position, execution_state, task_schedule_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_schedule_id) DO UPDATE SET
                    execution_state = excluded.execution_state,
                    json_data = excluded.json_data;
                """,
                (
                    task.task_schedule_id,
                    task.parent_schedule_id,
                    task.source_plan_task_id,
                    task.execution_position,
                    task.execution_state.value,
                    task.task_schedule_hash,
                    json_str,
                ),
            )

    def get_task(self, task_schedule_id: str) -> ScheduledTask | None:
        """Retrieve ScheduledTask by Task Schedule ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM scheduled_tasks WHERE task_schedule_id = ?;", (task_schedule_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScheduledTask(**json.loads(row["json_data"]))

    def get_tasks_for_schedule(self, schedule_id: str) -> list[ScheduledTask]:
        """Retrieve all ScheduledTasks for a schedule, ordered by position."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT json_data FROM scheduled_tasks WHERE parent_schedule_id = ? ORDER BY execution_position;",
            (schedule_id,),
        )
        return [ScheduledTask(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Context CRUD
    # ------------------------------------------------------------------

    def save_context(self, schedule_id: str, context: ScientificSchedulingContext) -> None:
        """Persist a ScientificSchedulingContext."""
        json_str = context.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO scheduling_contexts (schedule_id, json_data)
                VALUES (?, ?)
                ON CONFLICT(schedule_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (schedule_id, json_str),
            )

    def get_context(self, schedule_id: str) -> ScientificSchedulingContext | None:
        """Retrieve ScientificSchedulingContext."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM scheduling_contexts WHERE schedule_id = ?;", (schedule_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificSchedulingContext(**json.loads(row["json_data"]))

    # ------------------------------------------------------------------
    # Report CRUD
    # ------------------------------------------------------------------

    def save_report(self, report: ScientificSchedulingReport) -> None:
        """Persist a ScientificSchedulingReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO scheduling_reports (report_id, schedule_id, timestamp, json_data)
                VALUES (?, ?, ?, ?);
                """,
                (report.report_id, report.schedule_id, report.timestamp, json_str),
            )

    def get_report(self, report_id: str) -> ScientificSchedulingReport | None:
        """Retrieve ScientificSchedulingReport."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM scheduling_reports WHERE report_id = ?;", (report_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificSchedulingReport(**json.loads(row["json_data"]))

    # ------------------------------------------------------------------
    # Coordinator State CRUD
    # ------------------------------------------------------------------

    def save_coordinator_state(
        self,
        merged_schedule_id: str,
        source_schedule_ids: list[str],
        state_data: dict[str, Any] | None = None,
    ) -> None:
        """Persist coordinator merge state."""
        payload = {
            "merged_schedule_id": merged_schedule_id,
            "source_schedule_ids": source_schedule_ids,
            **(state_data or {}),
        }
        json_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO coordinator_state (merged_schedule_id, source_schedule_ids, json_data)
                VALUES (?, ?, ?)
                ON CONFLICT(merged_schedule_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (merged_schedule_id, json.dumps(source_schedule_ids), json_str),
            )

    # ------------------------------------------------------------------
    # Audit Events
    # ------------------------------------------------------------------

    def save_audit_event(
        self,
        schedule_id: str,
        event_type: str,
        event_timestamp: str,
        event_data: dict[str, Any],
    ) -> None:
        """Persist an audit event."""
        json_str = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO audit_events (schedule_id, event_type, event_timestamp, event_data)
                VALUES (?, ?, ?, ?);
                """,
                (schedule_id, event_type, event_timestamp, json_str),
            )

    def get_audit_events(self, schedule_id: str) -> list[dict[str, Any]]:
        """Retrieve all audit events for a schedule."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT event_type, event_timestamp, event_data FROM audit_events WHERE schedule_id = ? ORDER BY event_id;",
            (schedule_id,),
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

    def export_schedule(self, schedule_id: str) -> dict[str, Any]:
        """Export a complete schedule with all related artifacts as a dict."""
        schedule = self.get_schedule(schedule_id)
        if schedule is None:
            raise KeyError(f"Schedule '{schedule_id}' not found for export")

        tasks = self.get_tasks_for_schedule(schedule_id)
        context = self.get_context(schedule_id)
        audit_events = self.get_audit_events(schedule_id)

        return {
            "schema_version": SCHEDULING_SCHEMA_VERSION,
            "schedule": json.loads(schedule.model_dump_json()),
            "tasks": [json.loads(t.model_dump_json()) for t in tasks],
            "context": json.loads(context.model_dump_json()) if context else None,
            "audit_events": audit_events,
        }

    def import_schedule(self, data: dict[str, Any]) -> ResearchSchedule:
        """Import a complete schedule from exported data.

        Args:
            data: Dict from export_schedule().

        Returns:
            Imported ResearchSchedule.

        Raises:
            ValueError: If schema version mismatch.
        """
        if data.get("schema_version") != SCHEDULING_SCHEMA_VERSION:
            raise ValueError(
                f"Schema version mismatch: expected {SCHEDULING_SCHEMA_VERSION}, "
                f"got {data.get('schema_version')}"
            )

        schedule = ResearchSchedule(**data["schedule"])
        self.save_schedule(schedule)

        for task_data in data.get("tasks", []):
            task = ScheduledTask(**task_data)
            self.save_task(task)

        if data.get("context"):
            context = ScientificSchedulingContext(**data["context"])
            self.save_context(schedule.schedule_id, context)

        return schedule

    # ------------------------------------------------------------------
    # Integrity verification
    # ------------------------------------------------------------------

    def verify_integrity(self, schedule_id: str) -> bool:
        """Verify persistence integrity for a schedule.

        Returns:
            True if all tasks reference the schedule and data is consistent.

        Raises:
            ValueError: If integrity check fails.
        """
        schedule = self.get_schedule(schedule_id)
        if schedule is None:
            raise ValueError(f"Schedule '{schedule_id}' not found")

        tasks = self.get_tasks_for_schedule(schedule_id)
        persisted_ids = {t.task_schedule_id for t in tasks}
        expected_ids = set(schedule.scheduled_task_ids)

        if persisted_ids != expected_ids:
            raise ValueError(
                f"Task ID mismatch for schedule '{schedule_id}': "
                f"expected {expected_ids}, got {persisted_ids}"
            )
        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
