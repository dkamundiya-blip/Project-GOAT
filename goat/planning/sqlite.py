"""
Project GOAT v0.7 — SQLite Planning Repository

Implements transactional SQLite persistence for Scientific Plans, Plan Tasks, Planning Graphs, Contexts, and Reports.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.planning.context import ScientificPlanningContext
from goat.planning.model import ScientificPlan
from goat.planning.reporting import ScientificPlanningReport
from goat.planning.task import ScientificPlanTask


class SQLitePlanningRepository:
    """Transactional SQLite repository for scientific planning persistence."""

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
                CREATE TABLE IF NOT EXISTS scientific_plans (
                    plan_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    execution_status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS plan_tasks (
                    task_id TEXT PRIMARY KEY,
                    parent_plan_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    execution_order INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    task_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS planning_contexts (
                    plan_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (plan_id) REFERENCES scientific_plans(plan_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS planning_reports (
                    report_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (plan_id) REFERENCES scientific_plans(plan_id) ON DELETE CASCADE
                );
            """)

    def save_plan(self, plan: ScientificPlan) -> None:
        """Persist a ScientificPlan transactionally."""
        json_str = plan.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO scientific_plans (
                    plan_id, canonical_hash, scientific_fingerprint, semantic_version, creation_timestamp, execution_status, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(plan_id) DO UPDATE SET execution_status = excluded.execution_status, json_data = excluded.json_data;
                """,
                (
                    plan.plan_id,
                    plan.canonical_hash,
                    plan.scientific_fingerprint,
                    plan.semantic_version,
                    plan.creation_timestamp,
                    plan.execution_status,
                    json_str,
                ),
            )

    def get_plan(self, plan_id: str) -> ScientificPlan | None:
        """Retrieve ScientificPlan by Plan ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM scientific_plans WHERE plan_id = ?;", (plan_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificPlan(**json.loads(row["json_data"]))

    def save_task(self, task: ScientificPlanTask) -> None:
        """Persist a ScientificPlanTask."""
        json_str = task.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO plan_tasks (
                    task_id, parent_plan_id, stage, execution_order, status, task_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET status = excluded.status, json_data = excluded.json_data;
                """,
                (
                    task.task_id,
                    task.parent_plan_id,
                    task.stage.value,
                    task.execution_order,
                    task.status,
                    task.task_hash,
                    json_str,
                ),
            )

    def get_task(self, task_id: str) -> ScientificPlanTask | None:
        """Retrieve ScientificPlanTask."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM plan_tasks WHERE task_id = ?;", (task_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificPlanTask(**json.loads(row["json_data"]))

    def save_report(self, report: ScientificPlanningReport) -> None:
        """Persist a ScientificPlanningReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO planning_reports (report_id, plan_id, timestamp, json_data)
                VALUES (?, ?, ?, ?);
                """,
                (report.report_id, report.plan_id, report.timestamp, json_str),
            )

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
