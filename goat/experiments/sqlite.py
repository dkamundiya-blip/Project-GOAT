"""
Project GOAT v0.7 — SQLite Experiment Repository

Implements transactional SQLite persistence for Experiments, Protocols, Hypotheses, Results, Contexts, and Audit history.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.experiments.audit import ExperimentAuditEvent
from goat.experiments.context import ExperimentContext
from goat.experiments.hypothesis import HypothesisRecord
from goat.experiments.model import ScientificExperiment
from goat.experiments.protocol import ExperimentProtocol
from goat.experiments.result import ExperimentResult


class SQLiteExperimentRepository:
    """Transactional SQLite repository for scientific experiment persistence."""

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
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    scientific_fingerprint TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS protocols (
                    protocol_id TEXT PRIMARY KEY,
                    protocol_version TEXT NOT NULL,
                    protocol_name TEXT NOT NULL,
                    protocol_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS hypotheses (
                    hypothesis_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS results (
                    result_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    completion_timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS contexts (
                    experiment_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS experiment_audit (
                    event_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id) ON DELETE CASCADE
                );
            """)

    def save_experiment(self, experiment: ScientificExperiment) -> None:
        """Persist a ScientificExperiment transactionally."""
        json_str = experiment.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO experiments (
                    experiment_id, scientific_fingerprint, canonical_hash, semantic_version, name, status, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(experiment_id) DO UPDATE SET status = excluded.status, json_data = excluded.json_data;
                """,
                (
                    experiment.experiment_id,
                    experiment.scientific_fingerprint,
                    experiment.canonical_hash,
                    experiment.semantic_version,
                    experiment.name,
                    experiment.status.value,
                    json_str,
                ),
            )

    def get_experiment(self, experiment_id: str) -> ScientificExperiment | None:
        """Retrieve ScientificExperiment by Experiment ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM experiments WHERE experiment_id = ?;", (experiment_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificExperiment(**json.loads(row["json_data"]))

    def save_protocol(self, protocol: ExperimentProtocol) -> None:
        """Persist an ExperimentProtocol."""
        json_str = protocol.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO protocols (protocol_id, protocol_version, protocol_name, protocol_hash, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(protocol_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (protocol.protocol_id, protocol.protocol_version, protocol.protocol_name, protocol.protocol_hash, json_str),
            )

    def get_protocol(self, protocol_id: str) -> ExperimentProtocol | None:
        """Retrieve ExperimentProtocol."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM protocols WHERE protocol_id = ?;", (protocol_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ExperimentProtocol(**json.loads(row["json_data"]))

    def save_hypothesis(self, hypothesis: HypothesisRecord) -> None:
        """Persist a HypothesisRecord."""
        json_str = hypothesis.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO hypotheses (hypothesis_id, title, status, version, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(hypothesis_id) DO UPDATE SET status = excluded.status, json_data = excluded.json_data;
                """,
                (hypothesis.hypothesis_id, hypothesis.title, hypothesis.status.value, hypothesis.version, json_str),
            )

    def get_hypothesis(self, hypothesis_id: str) -> HypothesisRecord | None:
        """Retrieve HypothesisRecord."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM hypotheses WHERE hypothesis_id = ?;", (hypothesis_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return HypothesisRecord(**json.loads(row["json_data"]))

    def save_result(self, result: ExperimentResult) -> None:
        """Persist an ExperimentResult."""
        json_str = result.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO results (result_id, experiment_id, outcome, completion_timestamp, canonical_hash, json_data)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (result.result_id, result.experiment_id, result.outcome.value, result.completion_timestamp, result.canonical_hash, json_str),
            )

    def get_result(self, result_id: str) -> ExperimentResult | None:
        """Retrieve ExperimentResult."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM results WHERE result_id = ?;", (result_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ExperimentResult(**json.loads(row["json_data"]))

    def log_audit_event(self, event: ExperimentAuditEvent) -> None:
        """Log audit event."""
        json_str = event.model_dump_json()
        with self._conn:
            self._conn.execute(
                "INSERT INTO experiment_audit (event_id, experiment_id, event_type, timestamp, json_data) VALUES (?, ?, ?, ?, ?);",
                (event.event_id, event.experiment_id, event.event_type, event.timestamp, json_str),
            )

    def get_audit_trail(self, experiment_id: str) -> list[ExperimentAuditEvent]:
        """Retrieve audit log for experiment."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM experiment_audit WHERE experiment_id = ? ORDER BY timestamp ASC;", (experiment_id,))
        rows = cursor.fetchall()
        return [ExperimentAuditEvent(**json.loads(r["json_data"])) for r in rows]

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
