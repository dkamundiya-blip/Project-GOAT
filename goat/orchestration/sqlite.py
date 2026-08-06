"""
Project GOAT v0.7 — SQLite Orchestration Repository

Implements transactional SQLite database persistence for pipelines, stages, contexts, artifacts, audit events, and checkpoints.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.orchestration.artifacts import ArtifactRecord
from goat.orchestration.audit import PipelineAuditEvent
from goat.orchestration.context import ResearchExecutionContext
from goat.orchestration.enums import PipelineState
from goat.orchestration.model import ResearchPipeline
from goat.orchestration.recovery import PipelineCheckpoint
from goat.orchestration.stage import PipelineStage


class SQLiteOrchestrationRepository:
    """Transactional SQLite repository for research orchestration persistence."""

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
                CREATE TABLE IF NOT EXISTS pipelines (
                    pipeline_id TEXT PRIMARY KEY,
                    pipeline_version TEXT NOT NULL,
                    pipeline_hash TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS pipeline_stages (
                    stage_id TEXT PRIMARY KEY,
                    pipeline_id TEXT NOT NULL,
                    stage_type TEXT NOT NULL,
                    stage_index INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS execution_contexts (
                    pipeline_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS artifact_registry (
                    artifact_id TEXT PRIMARY KEY,
                    pipeline_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    registration_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS pipeline_audit (
                    event_id TEXT PRIMARY KEY,
                    pipeline_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    pipeline_id TEXT NOT NULL,
                    stage_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id) ON DELETE CASCADE
                );
            """)

    def save_pipeline(self, pipeline: ResearchPipeline) -> None:
        """Persist a ResearchPipeline transactionally."""
        json_str = pipeline.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO pipelines (
                    pipeline_id, pipeline_version, pipeline_hash, creation_timestamp, current_state, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(pipeline_id) DO UPDATE SET
                    current_state = excluded.current_state,
                    json_data = excluded.json_data;
                """,
                (
                    pipeline.pipeline_id,
                    pipeline.pipeline_version,
                    pipeline.pipeline_hash,
                    pipeline.creation_timestamp,
                    pipeline.current_state.value,
                    json_str,
                ),
            )

            # Insert or replace stages
            for stg in pipeline.registered_stages:
                stg_json = stg.model_dump_json()
                self._conn.execute(
                    """
                    INSERT INTO pipeline_stages (
                        stage_id, pipeline_id, stage_type, stage_index, status, json_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(stage_id) DO UPDATE SET
                        status = excluded.status,
                        json_data = excluded.json_data;
                    """,
                    (
                        stg.stage_id,
                        pipeline.pipeline_id,
                        stg.stage_type.value,
                        stg.stage_index,
                        stg.status,
                        stg_json,
                    ),
                )

    def get_pipeline(self, pipeline_id: str) -> ResearchPipeline | None:
        """Retrieve ResearchPipeline by Pipeline ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM pipelines WHERE pipeline_id = ?;", (pipeline_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ResearchPipeline(**json.loads(row["json_data"]))

    def save_context(self, context: ResearchExecutionContext) -> None:
        """Persist execution context."""
        json_str = context.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO execution_contexts (pipeline_id, json_data) VALUES (?, ?)
                ON CONFLICT(pipeline_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (context.pipeline_id, json_str),
            )

    def get_context(self, pipeline_id: str) -> ResearchExecutionContext | None:
        """Retrieve execution context."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM execution_contexts WHERE pipeline_id = ?;", (pipeline_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ResearchExecutionContext(**json.loads(row["json_data"]))

    def save_artifact(self, artifact: ArtifactRecord) -> None:
        """Persist artifact record."""
        json_str = artifact.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO artifact_registry (artifact_id, pipeline_id, artifact_type, registration_timestamp, json_data)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    artifact.artifact_id,
                    artifact.pipeline_id,
                    artifact.artifact_type.value,
                    artifact.registration_timestamp,
                    json_str,
                ),
            )

    def get_pipeline_artifacts(self, pipeline_id: str) -> list[ArtifactRecord]:
        """Retrieve all artifacts linked to pipeline."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM artifact_registry WHERE pipeline_id = ? ORDER BY registration_timestamp ASC;", (pipeline_id,))
        rows = cursor.fetchall()
        return [ArtifactRecord(**json.loads(r["json_data"])) for r in rows]

    def log_audit_event(self, event: PipelineAuditEvent) -> None:
        """Log pipeline audit event."""
        json_str = event.model_dump_json()
        with self._conn:
            self._conn.execute(
                "INSERT INTO pipeline_audit (event_id, pipeline_id, event_type, timestamp, json_data) VALUES (?, ?, ?, ?, ?);",
                (event.event_id, event.pipeline_id, event.event_type, event.timestamp, json_str),
            )

    def get_audit_trail(self, pipeline_id: str) -> list[PipelineAuditEvent]:
        """Retrieve audit trail for pipeline."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM pipeline_audit WHERE pipeline_id = ? ORDER BY timestamp ASC;", (pipeline_id,))
        rows = cursor.fetchall()
        return [PipelineAuditEvent(**json.loads(r["json_data"])) for r in rows]

    def save_checkpoint(self, checkpoint: PipelineCheckpoint) -> None:
        """Persist checkpoint."""
        json_str = checkpoint.model_dump_json()
        with self._conn:
            self._conn.execute(
                "INSERT INTO checkpoints (checkpoint_id, pipeline_id, stage_id, timestamp, json_data) VALUES (?, ?, ?, ?, ?);",
                (checkpoint.checkpoint_id, checkpoint.pipeline_id, checkpoint.stage_id, checkpoint.timestamp, json_str),
            )

    def get_checkpoints(self, pipeline_id: str) -> list[PipelineCheckpoint]:
        """Retrieve checkpoints for pipeline."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM checkpoints WHERE pipeline_id = ? ORDER BY timestamp ASC;", (pipeline_id,))
        rows = cursor.fetchall()
        return [PipelineCheckpoint(**json.loads(r["json_data"])) for r in rows]

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
