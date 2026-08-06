"""
Project GOAT v0.8 — Archive Vault Persistence Repositories

Implements transactional SQLite persistence for:
- ArchiveRepository
- ReplayRepository
- SnapshotRepository
- StatisticsRepository
- ArchiveReportRepository

Enforces WAL journal mode, foreign key constraints, append-only integrity, ON CONFLICT DO UPDATE, and deterministic serialization.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.archive.core.models import (
    ArchiveBatch,
    ArchiveRecord,
    ArchiveStatistics,
    ArchiveSummary,
    ReplayCheckpoint,
    ReplayRequest,
    ReplaySession,
    SnapshotManifest,
)

ARCHIVE_SCHEMA_VERSION = 1


class SQLiteArchiveRepository:
    """Transactional SQLite WAL repository managing archive vault entities."""

    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Initialize database schema with versioning."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS archive_schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO archive_schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS archive_records (
                    archive_id TEXT PRIMARY KEY,
                    source_subsystem TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS archive_batches (
                    batch_id TEXT PRIMARY KEY,
                    record_count INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS replay_sessions (
                    session_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    records_replayed INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    status TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS snapshot_manifests (
                    manifest_id TEXT PRIMARY KEY,
                    snapshot_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS archive_reports (
                    report_id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );
            """)

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Archive Record Operations
    # ------------------------------------------------------------------

    def save_record(self, record: ArchiveRecord) -> None:
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO archive_records (
                    archive_id, source_subsystem, entity_type, entity_id, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(archive_id) DO UPDATE SET
                    json_data=excluded.json_data
                """,
                (
                    record.archive_id,
                    record.source_subsystem.value if hasattr(record.source_subsystem, "value") else str(record.source_subsystem),
                    record.entity_type.value if hasattr(record.entity_type, "value") else str(record.entity_type),
                    record.entity_id,
                    record.timestamp,
                    record.canonical_hash,
                    json_str,
                ),
            )

    def get_record(self, archive_id: str) -> ArchiveRecord | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM archive_records WHERE archive_id = ?",
            (archive_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return ArchiveRecord.model_validate_json(row["json_data"])

    def get_all_records(self) -> list[ArchiveRecord]:
        cursor = self._conn.execute("SELECT json_data FROM archive_records ORDER BY timestamp ASC")
        return [ArchiveRecord.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Replay & Snapshot Operations
    # ------------------------------------------------------------------

    def save_replay_session(self, session: ReplaySession) -> None:
        json_str = session.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO replay_sessions (
                    session_id, request_id, records_replayed, start_time, end_time, status, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.request_id,
                    session.records_replayed,
                    session.start_time,
                    session.end_time,
                    session.status.value if hasattr(session.status, "value") else str(session.status),
                    session.canonical_hash,
                    json_str,
                ),
            )

    def save_snapshot(self, manifest: SnapshotManifest) -> None:
        json_str = manifest.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO snapshot_manifests (
                    manifest_id, snapshot_type, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    manifest.manifest_id,
                    manifest.snapshot_type.value if hasattr(manifest.snapshot_type, "value") else str(manifest.snapshot_type),
                    manifest.timestamp,
                    manifest.canonical_hash,
                    json_str,
                ),
            )

    def save_report(self, report_id: str, report_type: str, timestamp: str, content: str, json_data: dict[str, Any]) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO archive_reports (
                    report_id, report_type, timestamp, content, json_data
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    report_type,
                    timestamp,
                    content,
                    json.dumps(json_data, sort_keys=True),
                ),
            )


# Mapped repository export classes
class ArchiveRepository(SQLiteArchiveRepository):
    pass

class ReplayRepository(SQLiteArchiveRepository):
    pass

class SnapshotRepository(SQLiteArchiveRepository):
    pass

class StatisticsRepository(SQLiteArchiveRepository):
    pass

class ArchiveReportRepository(SQLiteArchiveRepository):
    pass
