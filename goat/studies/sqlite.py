"""
Project GOAT v0.7 — SQLite Study Repository

Implements transactional SQLite persistence for Studies, Study Designs, Results, Contexts, Experiment Registries, and Audit history.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.studies.audit import StudyAuditEvent
from goat.studies.context import StudyContext
from goat.studies.design import StudyDesign
from goat.studies.model import ScientificStudy
from goat.studies.registry import StudyExperimentRecord
from goat.studies.result import StudyResult


class SQLiteStudyRepository:
    """Transactional SQLite repository for scientific study persistence."""

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
                CREATE TABLE IF NOT EXISTS studies (
                    study_id TEXT PRIMARY KEY,
                    scientific_fingerprint TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS study_designs (
                    design_id TEXT PRIMARY KEY,
                    design_version TEXT NOT NULL,
                    research_objective TEXT NOT NULL,
                    design_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS study_results (
                    result_id TEXT PRIMARY KEY,
                    study_id TEXT NOT NULL,
                    completion_timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (study_id) REFERENCES studies(study_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS study_contexts (
                    study_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (study_id) REFERENCES studies(study_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS experiment_registry (
                    experiment_id TEXT PRIMARY KEY,
                    study_id TEXT NOT NULL,
                    execution_order INTEGER NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (study_id) REFERENCES studies(study_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS study_audit (
                    event_id TEXT PRIMARY KEY,
                    study_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (study_id) REFERENCES studies(study_id) ON DELETE CASCADE
                );
            """)

    def save_study(self, study: ScientificStudy) -> None:
        """Persist a ScientificStudy transactionally."""
        json_str = study.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO studies (
                    study_id, scientific_fingerprint, canonical_hash, semantic_version, title, status, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(study_id) DO UPDATE SET status = excluded.status, json_data = excluded.json_data;
                """,
                (
                    study.study_id,
                    study.scientific_fingerprint,
                    study.canonical_hash,
                    study.semantic_version,
                    study.title,
                    study.status.value,
                    json_str,
                ),
            )

    def get_study(self, study_id: str) -> ScientificStudy | None:
        """Retrieve ScientificStudy by Study ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM studies WHERE study_id = ?;", (study_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificStudy(**json.loads(row["json_data"]))

    def save_design(self, design: StudyDesign) -> None:
        """Persist a StudyDesign."""
        json_str = design.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO study_designs (design_id, design_version, research_objective, design_hash, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(design_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (design.design_id, design.design_version, design.research_objective, design.design_hash, json_str),
            )

    def get_design(self, design_id: str) -> StudyDesign | None:
        """Retrieve StudyDesign."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM study_designs WHERE design_id = ?;", (design_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return StudyDesign(**json.loads(row["json_data"]))

    def save_experiment_record(self, record: StudyExperimentRecord) -> None:
        """Persist a StudyExperimentRecord."""
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO experiment_registry (experiment_id, study_id, execution_order, json_data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(experiment_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (record.experiment_id, record.study_id, record.execution_order, json_str),
            )

    def get_study_experiments(self, study_id: str) -> list[StudyExperimentRecord]:
        """Retrieve all registered experiment records for a study."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM experiment_registry WHERE study_id = ? ORDER BY execution_order ASC;", (study_id,))
        rows = cursor.fetchall()
        return [StudyExperimentRecord(**json.loads(r["json_data"])) for r in rows]

    def save_result(self, result: StudyResult) -> None:
        """Persist a StudyResult."""
        json_str = result.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO study_results (result_id, study_id, completion_timestamp, canonical_hash, json_data)
                VALUES (?, ?, ?, ?, ?);
                """,
                (result.result_id, result.study_id, result.completion_timestamp, result.canonical_hash, json_str),
            )

    def get_result(self, result_id: str) -> StudyResult | None:
        """Retrieve StudyResult."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM study_results WHERE result_id = ?;", (result_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return StudyResult(**json.loads(row["json_data"]))

    def log_audit_event(self, event: StudyAuditEvent) -> None:
        """Log audit event."""
        json_str = event.model_dump_json()
        with self._conn:
            self._conn.execute(
                "INSERT INTO study_audit (event_id, study_id, event_type, timestamp, json_data) VALUES (?, ?, ?, ?, ?);",
                (event.event_id, event.study_id, event.event_type, event.timestamp, json_str),
            )

    def get_audit_trail(self, study_id: str) -> list[StudyAuditEvent]:
        """Retrieve audit trail for a study."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM study_audit WHERE study_id = ? ORDER BY timestamp ASC;", (study_id,))
        rows = cursor.fetchall()
        return [StudyAuditEvent(**json.loads(r["json_data"])) for r in rows]

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
