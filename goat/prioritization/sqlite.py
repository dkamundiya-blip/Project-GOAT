"""
Project GOAT v0.7 — SQLite Prioritization Repository

Implements transactional SQLite persistence for Research Priorities, Priority Queues, Contexts, and Reports.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.prioritization.context import ResearchPrioritizationContext
from goat.prioritization.model import ResearchPriority
from goat.prioritization.queue import ResearchPriorityQueue
from goat.prioritization.reporting import ResearchPriorityReport


class SQLitePrioritizationRepository:
    """Transactional SQLite repository for scientific research prioritization persistence."""

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
                CREATE TABLE IF NOT EXISTS research_priorities (
                    priority_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    priority_score REAL NOT NULL,
                    priority_level TEXT NOT NULL,
                    opportunity_type TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS priority_queues (
                    queue_id TEXT PRIMARY KEY,
                    queue_hash TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS priority_contexts (
                    queue_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (queue_id) REFERENCES priority_queues(queue_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS priority_reports (
                    report_id TEXT PRIMARY KEY,
                    queue_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (queue_id) REFERENCES priority_queues(queue_id) ON DELETE CASCADE
                );
            """)

    def save_priority(self, priority: ResearchPriority) -> None:
        """Persist a ResearchPriority transactionally."""
        json_str = priority.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO research_priorities (
                    priority_id, canonical_hash, scientific_fingerprint, semantic_version, priority_score, priority_level, opportunity_type, creation_timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(priority_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (
                    priority.priority_id,
                    priority.canonical_hash,
                    priority.scientific_fingerprint,
                    priority.semantic_version,
                    priority.priority_score,
                    priority.priority_level.value,
                    priority.opportunity_type.value,
                    priority.creation_timestamp,
                    json_str,
                ),
            )

    def get_priority(self, priority_id: str) -> ResearchPriority | None:
        """Retrieve ResearchPriority by Priority ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM research_priorities WHERE priority_id = ?;", (priority_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ResearchPriority(**json.loads(row["json_data"]))

    def save_queue(self, queue: ResearchPriorityQueue) -> None:
        """Persist a ResearchPriorityQueue."""
        json_str = queue.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO priority_queues (queue_id, queue_hash, creation_timestamp, json_data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(queue_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (queue.queue_id, queue.queue_hash, queue.creation_timestamp, json_str),
            )

    def get_queue(self, queue_id: str) -> ResearchPriorityQueue | None:
        """Retrieve ResearchPriorityQueue."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM priority_queues WHERE queue_id = ?;", (queue_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ResearchPriorityQueue(**json.loads(row["json_data"]))

    def save_report(self, report: ResearchPriorityReport) -> None:
        """Persist a ResearchPriorityReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO priority_reports (report_id, queue_id, timestamp, json_data)
                VALUES (?, ?, ?, ?);
                """,
                (report.report_id, report.queue_id, report.timestamp, json_str),
            )

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
