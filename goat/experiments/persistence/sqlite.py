"""
Project GOAT v0.9 — SQLite Persistence Repositories for Scientific Experiment Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.experiments.core.enums import (
    ExperimentPriority,
    ExperimentStatus,
    ExperimentType,
)
from goat.experiments.core.models import (
    ExperimentLifecycle,
    ExperimentManifest,
    ExperimentReplay,
    ExperimentSchedule,
    ExperimentSummary,
    ScientificExperiment,
)


def init_experiment_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and pragmas for Experiment subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scientific_experiments (
                experiment_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                experiment_type TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                author TEXT NOT NULL,
                evidence_ids_json TEXT NOT NULL,
                manifest_id TEXT NOT NULL,
                created_timestamp TEXT NOT NULL,
                updated_timestamp TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiment_manifests (
                manifest_id TEXT PRIMARY KEY,
                experiment_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                evidence_ids_json TEXT NOT NULL,
                dataset_fingerprint TEXT NOT NULL,
                configuration_params_json TEXT NOT NULL,
                software_version TEXT NOT NULL,
                author TEXT NOT NULL,
                created_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiment_lifecycles (
                lifecycle_id TEXT PRIMARY KEY,
                experiment_id TEXT NOT NULL,
                from_status TEXT NOT NULL,
                to_status TEXT NOT NULL,
                actor TEXT NOT NULL,
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiment_replays (
                replay_id TEXT PRIMARY KEY,
                experiment_id TEXT NOT NULL,
                manifest_id TEXT NOT NULL,
                dataset_hash TEXT NOT NULL,
                random_seed INTEGER NOT NULL,
                expected_output_hash TEXT NOT NULL,
                is_verified INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiment_schedules (
                schedule_id TEXT PRIMARY KEY,
                experiment_id TEXT NOT NULL,
                priority TEXT NOT NULL,
                scheduled_timestamp TEXT NOT NULL,
                queue_position INTEGER NOT NULL,
                scheduler_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiment_summaries (
                summary_id TEXT PRIMARY KEY,
                total_experiments INTEGER NOT NULL,
                status_counts_json TEXT NOT NULL,
                type_counts_json TEXT NOT NULL,
                priority_counts_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class ExperimentRepository:
    """Repository for persisting and querying ScientificExperiment instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, experiment: ScientificExperiment) -> ScientificExperiment:
        """Insert or replace a ScientificExperiment."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO scientific_experiments (
                    experiment_id, hypothesis_id, title, description, experiment_type,
                    status, priority, author, evidence_ids_json, manifest_id,
                    created_timestamp, updated_timestamp, tags_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment.experiment_id,
                    experiment.hypothesis_id,
                    experiment.title,
                    experiment.description,
                    experiment.experiment_type.value,
                    experiment.status.value,
                    experiment.priority.value,
                    experiment.author,
                    json.dumps(experiment.evidence_ids),
                    experiment.manifest_id,
                    experiment.created_timestamp,
                    experiment.updated_timestamp,
                    json.dumps(experiment.tags),
                    json.dumps(experiment.metadata),
                    experiment.canonical_hash,
                ),
            )
        return experiment

    def get_by_id(self, experiment_id: str) -> ScientificExperiment | None:
        """Fetch an experiment by ID."""
        cursor = self._conn.execute("SELECT * FROM scientific_experiments WHERE experiment_id = ?", (experiment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ScientificExperiment]:
        """List all experiments ordered by creation timestamp."""
        cursor = self._conn.execute("SELECT * FROM scientific_experiments ORDER BY created_timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def delete_by_id(self, experiment_id: str) -> bool:
        """Delete experiment by ID."""
        with self._conn:
            cursor = self._conn.execute("DELETE FROM scientific_experiments WHERE experiment_id = ?", (experiment_id,))
            return cursor.rowcount > 0

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ScientificExperiment:
        return ScientificExperiment(
            experiment_id=row[0],
            hypothesis_id=row[1],
            title=row[2],
            description=row[3],
            experiment_type=ExperimentType(row[4]),
            status=ExperimentStatus(row[5]),
            priority=ExperimentPriority(row[6]),
            author=row[7],
            evidence_ids=json.loads(row[8]),
            manifest_id=row[9],
            created_timestamp=row[10],
            updated_timestamp=row[11],
            tags=json.loads(row[12]),
            metadata=json.loads(row[13]),
            canonical_hash=row[14],
        )


class ManifestRepository:
    """Repository for persisting and querying ExperimentManifest instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, manifest: ExperimentManifest) -> ExperimentManifest:
        """Insert or replace an ExperimentManifest."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO experiment_manifests (
                    manifest_id, experiment_id, hypothesis_id, evidence_ids_json,
                    dataset_fingerprint, configuration_params_json, software_version,
                    author, created_timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    manifest.manifest_id,
                    manifest.experiment_id,
                    manifest.hypothesis_id,
                    json.dumps(manifest.evidence_ids),
                    manifest.dataset_fingerprint,
                    json.dumps(manifest.configuration_params),
                    manifest.software_version,
                    manifest.author,
                    manifest.created_timestamp,
                    json.dumps(manifest.metadata),
                    manifest.canonical_hash,
                ),
            )
        return manifest

    def get_by_id(self, manifest_id: str) -> ExperimentManifest | None:
        """Fetch a manifest by ID."""
        cursor = self._conn.execute("SELECT * FROM experiment_manifests WHERE manifest_id = ?", (manifest_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ExperimentManifest]:
        """Fetch all manifests."""
        cursor = self._conn.execute("SELECT * FROM experiment_manifests ORDER BY created_timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ExperimentManifest:
        return ExperimentManifest(
            manifest_id=row[0],
            experiment_id=row[1],
            hypothesis_id=row[2],
            evidence_ids=json.loads(row[3]),
            dataset_fingerprint=row[4],
            configuration_params=json.loads(row[5]),
            software_version=row[6],
            author=row[7],
            created_timestamp=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class LifecycleRepository:
    """Repository for persisting and querying ExperimentLifecycle instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, lifecycle: ExperimentLifecycle) -> ExperimentLifecycle:
        """Insert or replace an ExperimentLifecycle event."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO experiment_lifecycles (
                    lifecycle_id, experiment_id, from_status, to_status, actor,
                    reason, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lifecycle.lifecycle_id,
                    lifecycle.experiment_id,
                    lifecycle.from_status.value,
                    lifecycle.to_status.value,
                    lifecycle.actor,
                    lifecycle.reason,
                    lifecycle.timestamp,
                    json.dumps(lifecycle.metadata),
                    lifecycle.canonical_hash,
                ),
            )
        return lifecycle

    def get_by_experiment_id(self, experiment_id: str) -> list[ExperimentLifecycle]:
        """Fetch lifecycle events for an experiment ID."""
        cursor = self._conn.execute("SELECT * FROM experiment_lifecycles WHERE experiment_id = ? ORDER BY timestamp ASC", (experiment_id,))
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def list_all(self) -> list[ExperimentLifecycle]:
        """Fetch all lifecycle events."""
        cursor = self._conn.execute("SELECT * FROM experiment_lifecycles ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ExperimentLifecycle:
        return ExperimentLifecycle(
            lifecycle_id=row[0],
            experiment_id=row[1],
            from_status=ExperimentStatus(row[2]),
            to_status=ExperimentStatus(row[3]),
            actor=row[4],
            reason=row[5],
            timestamp=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class ReplayRepository:
    """Repository for persisting and querying ExperimentReplay instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, replay: ExperimentReplay) -> ExperimentReplay:
        """Insert or replace an ExperimentReplay."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO experiment_replays (
                    replay_id, experiment_id, manifest_id, dataset_hash, random_seed,
                    expected_output_hash, is_verified, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    replay.replay_id,
                    replay.experiment_id,
                    replay.manifest_id,
                    replay.dataset_hash,
                    replay.random_seed,
                    replay.expected_output_hash,
                    1 if replay.is_verified else 0,
                    replay.timestamp,
                    json.dumps(replay.metadata),
                    replay.canonical_hash,
                ),
            )
        return replay

    def get_by_id(self, replay_id: str) -> ExperimentReplay | None:
        """Fetch a replay by ID."""
        cursor = self._conn.execute("SELECT * FROM experiment_replays WHERE replay_id = ?", (replay_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ExperimentReplay]:
        """Fetch all replay records."""
        cursor = self._conn.execute("SELECT * FROM experiment_replays ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ExperimentReplay:
        return ExperimentReplay(
            replay_id=row[0],
            experiment_id=row[1],
            manifest_id=row[2],
            dataset_hash=row[3],
            random_seed=row[4],
            expected_output_hash=row[5],
            is_verified=bool(row[6]),
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class ScheduleRepository:
    """Repository for persisting and querying ExperimentSchedule instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, schedule: ExperimentSchedule) -> ExperimentSchedule:
        """Insert or replace an ExperimentSchedule."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO experiment_schedules (
                    schedule_id, experiment_id, priority, scheduled_timestamp, queue_position,
                    scheduler_id, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    schedule.schedule_id,
                    schedule.experiment_id,
                    schedule.priority.value,
                    schedule.scheduled_timestamp,
                    schedule.queue_position,
                    schedule.scheduler_id,
                    schedule.timestamp,
                    json.dumps(schedule.metadata),
                    schedule.canonical_hash,
                ),
            )
        return schedule

    def get_by_experiment_id(self, experiment_id: str) -> ExperimentSchedule | None:
        """Fetch schedule by experiment ID."""
        cursor = self._conn.execute("SELECT * FROM experiment_schedules WHERE experiment_id = ?", (experiment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ExperimentSchedule]:
        """Fetch all schedules ordered by queue_position."""
        cursor = self._conn.execute("SELECT * FROM experiment_schedules ORDER BY queue_position ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ExperimentSchedule:
        return ExperimentSchedule(
            schedule_id=row[0],
            experiment_id=row[1],
            priority=ExperimentPriority(row[2]),
            scheduled_timestamp=row[3],
            queue_position=row[4],
            scheduler_id=row[5],
            timestamp=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class SummaryRepository:
    """Repository for persisting and querying ExperimentSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: ExperimentSummary) -> ExperimentSummary:
        """Insert or replace an ExperimentSummary."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO experiment_summaries (
                    summary_id, total_experiments, status_counts_json, type_counts_json,
                    priority_counts_json, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.total_experiments,
                    json.dumps(summary.status_counts),
                    json.dumps(summary.type_counts),
                    json.dumps(summary.priority_counts),
                    summary.timestamp,
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> ExperimentSummary | None:
        """Fetch summary by ID."""
        cursor = self._conn.execute("SELECT * FROM experiment_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ExperimentSummary:
        return ExperimentSummary(
            summary_id=row[0],
            total_experiments=row[1],
            status_counts=json.loads(row[2]),
            type_counts=json.loads(row[3]),
            priority_counts=json.loads(row[4]),
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ExperimentPersistenceContext:
    """Unified Persistence Context wrapping SQLite repositories for scientific experiment subsystem."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_experiment_db(self.conn)
        self.experiments = ExperimentRepository(self.conn)
        self.manifests = ManifestRepository(self.conn)
        self.lifecycles = LifecycleRepository(self.conn)
        self.replays = ReplayRepository(self.conn)
        self.schedules = ScheduleRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
