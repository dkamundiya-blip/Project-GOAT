"""
Project GOAT v0.7 — SQLite Program Repository

Implements transactional SQLite persistence for Programs, Program Designs, Milestones, Results, Contexts, Study Registries, and Audit history.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.programs.audit import ProgramAuditEvent
from goat.programs.context import ProgramContext
from goat.programs.design import ProgramDesign
from goat.programs.milestone import ProgramMilestone
from goat.programs.model import ScientificResearchProgram
from goat.programs.registry import ProgramStudyRecord
from goat.programs.result import ProgramResult


class SQLiteProgramRepository:
    """Transactional SQLite repository for scientific research program persistence."""

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
                CREATE TABLE IF NOT EXISTS programs (
                    program_id TEXT PRIMARY KEY,
                    scientific_fingerprint TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    program_title TEXT NOT NULL,
                    program_status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS program_designs (
                    design_id TEXT PRIMARY KEY,
                    design_version TEXT NOT NULL,
                    strategic_objectives TEXT NOT NULL,
                    design_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS program_milestones (
                    milestone_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS program_results (
                    result_id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    completion_timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS program_contexts (
                    program_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS study_registry (
                    study_id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    execution_order INTEGER NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS program_audit (
                    event_id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE
                );
            """)

    def save_program(self, program: ScientificResearchProgram) -> None:
        """Persist a ScientificResearchProgram transactionally."""
        json_str = program.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO programs (
                    program_id, scientific_fingerprint, canonical_hash, semantic_version, program_title, program_status, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(program_id) DO UPDATE SET program_status = excluded.program_status, json_data = excluded.json_data;
                """,
                (
                    program.program_id,
                    program.scientific_fingerprint,
                    program.canonical_hash,
                    program.semantic_version,
                    program.program_title,
                    program.program_status.value,
                    json_str,
                ),
            )

    def get_program(self, program_id: str) -> ScientificResearchProgram | None:
        """Retrieve ScientificResearchProgram by Program ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM programs WHERE program_id = ?;", (program_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificResearchProgram(**json.loads(row["json_data"]))

    def save_design(self, design: ProgramDesign) -> None:
        """Persist a ProgramDesign."""
        json_str = design.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO program_designs (design_id, design_version, strategic_objectives, design_hash, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(design_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (design.design_id, design.design_version, design.strategic_objectives, design.design_hash, json_str),
            )

    def get_design(self, design_id: str) -> ProgramDesign | None:
        """Retrieve ProgramDesign."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM program_designs WHERE design_id = ?;", (design_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ProgramDesign(**json.loads(row["json_data"]))

    def save_milestone(self, milestone: ProgramMilestone) -> None:
        """Persist a ProgramMilestone."""
        json_str = milestone.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO program_milestones (milestone_id, title, status, json_data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(milestone_id) DO UPDATE SET status = excluded.status, json_data = excluded.json_data;
                """,
                (milestone.milestone_id, milestone.title, milestone.status.value, json_str),
            )

    def get_milestone(self, milestone_id: str) -> ProgramMilestone | None:
        """Retrieve ProgramMilestone."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM program_milestones WHERE milestone_id = ?;", (milestone_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ProgramMilestone(**json.loads(row["json_data"]))

    def save_study_record(self, record: ProgramStudyRecord) -> None:
        """Persist a ProgramStudyRecord."""
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO study_registry (study_id, program_id, execution_order, json_data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(study_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (record.study_id, record.program_id, record.execution_order, json_str),
            )

    def get_program_studies(self, program_id: str) -> list[ProgramStudyRecord]:
        """Retrieve all registered study records for a program."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM study_registry WHERE program_id = ? ORDER BY execution_order ASC;", (program_id,))
        rows = cursor.fetchall()
        return [ProgramStudyRecord(**json.loads(r["json_data"])) for r in rows]

    def save_result(self, result: ProgramResult) -> None:
        """Persist a ProgramResult."""
        json_str = result.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO program_results (result_id, program_id, completion_timestamp, canonical_hash, json_data)
                VALUES (?, ?, ?, ?, ?);
                """,
                (result.result_id, result.program_id, result.completion_timestamp, result.canonical_hash, json_str),
            )

    def get_result(self, result_id: str) -> ProgramResult | None:
        """Retrieve ProgramResult."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM program_results WHERE result_id = ?;", (result_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ProgramResult(**json.loads(row["json_data"]))

    def log_audit_event(self, event: ProgramAuditEvent) -> None:
        """Log audit event."""
        json_str = event.model_dump_json()
        with self._conn:
            self._conn.execute(
                "INSERT INTO program_audit (event_id, program_id, event_type, timestamp, json_data) VALUES (?, ?, ?, ?, ?);",
                (event.event_id, event.program_id, event.event_type, event.timestamp, json_str),
            )

    def get_audit_trail(self, program_id: str) -> list[ProgramAuditEvent]:
        """Retrieve audit trail for a program."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM program_audit WHERE program_id = ? ORDER BY timestamp ASC;", (program_id,))
        rows = cursor.fetchall()
        return [ProgramAuditEvent(**json.loads(r["json_data"])) for r in rows]

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
