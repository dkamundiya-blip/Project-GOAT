"""
Project GOAT v0.7 — SQLite Evolution Repository

Implements transactional SQLite persistence for Knowledge Evolutions, Knowledge Versions, Lineage Nodes, Contexts, and Reports.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.evolution.context import KnowledgeEvolutionContext
from goat.evolution.model import KnowledgeEvolution
from goat.evolution.reporting import KnowledgeEvolutionReport
from goat.evolution.version import KnowledgeVersion


class SQLiteEvolutionRepository:
    """Transactional SQLite repository for scientific knowledge evolution persistence."""

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
                CREATE TABLE IF NOT EXISTS knowledge_evolutions (
                    evolution_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    evolution_type TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS knowledge_versions (
                    version_id TEXT PRIMARY KEY,
                    knowledge_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    parent_version_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS lineage_nodes (
                    version_id TEXT PRIMARY KEY,
                    parent_version_id TEXT NOT NULL,
                    knowledge_id TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS evolution_contexts (
                    evolution_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (evolution_id) REFERENCES knowledge_evolutions(evolution_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS evolution_reports (
                    report_id TEXT PRIMARY KEY,
                    evolution_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (evolution_id) REFERENCES knowledge_evolutions(evolution_id) ON DELETE CASCADE
                );
            """)

    def save_evolution(self, evolution: KnowledgeEvolution) -> None:
        """Persist a KnowledgeEvolution transactionally."""
        json_str = evolution.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO knowledge_evolutions (
                    evolution_id, canonical_hash, scientific_fingerprint, semantic_version, evolution_type, creation_timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(evolution_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (
                    evolution.evolution_id,
                    evolution.canonical_hash,
                    evolution.scientific_fingerprint,
                    evolution.semantic_version,
                    evolution.evolution_type.value,
                    evolution.creation_timestamp,
                    json_str,
                ),
            )

    def get_evolution(self, evolution_id: str) -> KnowledgeEvolution | None:
        """Retrieve KnowledgeEvolution by Evolution ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM knowledge_evolutions WHERE evolution_id = ?;", (evolution_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return KnowledgeEvolution(**json.loads(row["json_data"]))

    def save_version(self, version: KnowledgeVersion) -> None:
        """Persist a KnowledgeVersion."""
        json_str = version.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO knowledge_versions (
                    version_id, knowledge_id, version_number, parent_version_id, status, version_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(version_id) DO UPDATE SET status = excluded.status, json_data = excluded.json_data;
                """,
                (
                    version.version_id,
                    version.knowledge_id,
                    version.version_number,
                    version.parent_version_id,
                    version.status,
                    version.version_hash,
                    json_str,
                ),
            )

    def get_version(self, version_id: str) -> KnowledgeVersion | None:
        """Retrieve KnowledgeVersion."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM knowledge_versions WHERE version_id = ?;", (version_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return KnowledgeVersion(**json.loads(row["json_data"]))

    def save_report(self, report: KnowledgeEvolutionReport) -> None:
        """Persist a KnowledgeEvolutionReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO evolution_reports (report_id, evolution_id, timestamp, json_data)
                VALUES (?, ?, ?, ?);
                """,
                (report.report_id, report.evolution_id, report.timestamp, json_str),
            )

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
