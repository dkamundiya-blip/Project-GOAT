"""
Project GOAT v0.7 — SQLite Consensus Repository

Implements transactional SQLite persistence for Consensus objects, Consensus Conflicts, Contexts, and Reports.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.consensus.conflict import ConsensusConflict
from goat.consensus.context import ConsensusContext
from goat.consensus.model import ScientificConsensus
from goat.consensus.reporting import ConsensusReport


class SQLiteConsensusRepository:
    """Transactional SQLite repository for scientific consensus persistence."""

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
                CREATE TABLE IF NOT EXISTS consensus_objects (
                    consensus_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    consensus_status TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS consensus_conflicts (
                    conflict_id TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    resolution_status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    conflict_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS consensus_contexts (
                    consensus_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (consensus_id) REFERENCES consensus_objects(consensus_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS consensus_reports (
                    report_id TEXT PRIMARY KEY,
                    consensus_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (consensus_id) REFERENCES consensus_objects(consensus_id) ON DELETE CASCADE
                );
            """)

    def save_consensus(self, consensus: ScientificConsensus) -> None:
        """Persist a ScientificConsensus transactionally."""
        json_str = consensus.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO consensus_objects (
                    consensus_id, canonical_hash, scientific_fingerprint, semantic_version, consensus_status, creation_timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(consensus_id) DO UPDATE SET consensus_status = excluded.consensus_status, json_data = excluded.json_data;
                """,
                (
                    consensus.consensus_id,
                    consensus.canonical_hash,
                    consensus.scientific_fingerprint,
                    consensus.semantic_version,
                    consensus.consensus_status.value,
                    consensus.creation_timestamp,
                    json_str,
                ),
            )

    def get_consensus(self, consensus_id: str) -> ScientificConsensus | None:
        """Retrieve ScientificConsensus by Consensus ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM consensus_objects WHERE consensus_id = ?;", (consensus_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificConsensus(**json.loads(row["json_data"]))

    def save_conflict(self, conflict: ConsensusConflict) -> None:
        """Persist a ConsensusConflict."""
        json_str = conflict.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO consensus_conflicts (conflict_id, severity, resolution_status, timestamp, conflict_hash, json_data)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(conflict_id) DO UPDATE SET resolution_status = excluded.resolution_status, json_data = excluded.json_data;
                """,
                (conflict.conflict_id, conflict.severity, conflict.resolution_status, conflict.timestamp, conflict.conflict_hash, json_str),
            )

    def get_conflict(self, conflict_id: str) -> ConsensusConflict | None:
        """Retrieve ConsensusConflict."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM consensus_conflicts WHERE conflict_id = ?;", (conflict_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ConsensusConflict(**json.loads(row["json_data"]))

    def save_report(self, report: ConsensusReport) -> None:
        """Persist a ConsensusReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO consensus_reports (report_id, consensus_id, timestamp, json_data)
                VALUES (?, ?, ?, ?);
                """,
                (report.report_id, report.consensus_id, report.timestamp, json_str),
            )

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
