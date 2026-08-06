"""
Project GOAT v0.7 — SQLite Synthesis Repository

Implements transactional SQLite persistence for Syntheses, Clusters, Contradictions, Replication Records, Contexts, and Reports.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.synthesis.cluster import EvidenceCluster
from goat.synthesis.context import EvidenceSynthesisContext
from goat.synthesis.contradiction import ContradictionRecord
from goat.synthesis.model import EvidenceSynthesis
from goat.synthesis.replication import ReplicationRecord
from goat.synthesis.reporting import EvidenceSynthesisReport


class SQLiteSynthesisRepository:
    """Transactional SQLite repository for scientific evidence synthesis persistence."""

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
                CREATE TABLE IF NOT EXISTS syntheses (
                    synthesis_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    version TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clusters (
                    cluster_id TEXT PRIMARY KEY,
                    replication_count INTEGER NOT NULL,
                    provenance TEXT NOT NULL,
                    cluster_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS contradictions (
                    record_id TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    record_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS replication_records (
                    replication_id TEXT PRIMARY KEY,
                    source_evidence_id TEXT NOT NULL,
                    replicated_evidence_id TEXT NOT NULL,
                    quality TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS synthesis_contexts (
                    synthesis_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (synthesis_id) REFERENCES syntheses(synthesis_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS synthesis_reports (
                    report_id TEXT PRIMARY KEY,
                    synthesis_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (synthesis_id) REFERENCES syntheses(synthesis_id) ON DELETE CASCADE
                );
            """)

    def save_synthesis(self, synthesis: EvidenceSynthesis) -> None:
        """Persist an EvidenceSynthesis transactionally."""
        json_str = synthesis.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO syntheses (
                    synthesis_id, canonical_hash, scientific_fingerprint, version, creation_timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(synthesis_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (
                    synthesis.synthesis_id,
                    synthesis.canonical_hash,
                    synthesis.scientific_fingerprint,
                    synthesis.version,
                    synthesis.creation_timestamp,
                    json_str,
                ),
            )

    def get_synthesis(self, synthesis_id: str) -> EvidenceSynthesis | None:
        """Retrieve EvidenceSynthesis by Synthesis ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM syntheses WHERE synthesis_id = ?;", (synthesis_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return EvidenceSynthesis(**json.loads(row["json_data"]))

    def save_cluster(self, cluster: EvidenceCluster) -> None:
        """Persist an EvidenceCluster."""
        json_str = cluster.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO clusters (cluster_id, replication_count, provenance, cluster_hash, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(cluster_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (cluster.cluster_id, cluster.replication_count, cluster.provenance, cluster.cluster_hash, json_str),
            )

    def get_cluster(self, cluster_id: str) -> EvidenceCluster | None:
        """Retrieve EvidenceCluster."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM clusters WHERE cluster_id = ?;", (cluster_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return EvidenceCluster(**json.loads(row["json_data"]))

    def save_contradiction(self, record: ContradictionRecord) -> None:
        """Persist a ContradictionRecord."""
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO contradictions (record_id, severity, timestamp, record_hash, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (record.record_id, record.severity.value, record.timestamp, record.record_hash, json_str),
            )

    def get_contradiction(self, record_id: str) -> ContradictionRecord | None:
        """Retrieve ContradictionRecord."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM contradictions WHERE record_id = ?;", (record_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ContradictionRecord(**json.loads(row["json_data"]))

    def save_replication(self, record: ReplicationRecord) -> None:
        """Persist a ReplicationRecord."""
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO replication_records (replication_id, source_evidence_id, replicated_evidence_id, quality, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(replication_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (record.replication_id, record.source_evidence_id, record.replicated_evidence_id, record.quality.value, json_str),
            )

    def save_report(self, report: EvidenceSynthesisReport) -> None:
        """Persist an EvidenceSynthesisReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO synthesis_reports (report_id, synthesis_id, timestamp, json_data)
                VALUES (?, ?, ?, ?);
                """,
                (report.report_id, report.synthesis_id, report.timestamp, json_str),
            )

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
