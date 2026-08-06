"""
Project GOAT v0.7 — SQLite Knowledge Repository

Implements transactional SQLite persistence for KnowledgeObjects, EvidenceReferences, Relationships, and Audit history.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.knowledge.enums import KnowledgeStatus, KnowledgeType
from goat.knowledge.evidence import EvidenceReference
from goat.knowledge.model import KnowledgeObject
from goat.knowledge.registry.model import KnowledgeAuditEvent, KnowledgeRegistryRecord
from goat.research.edge.canonical import compute_canonical_sha256


class SQLiteKnowledgeRepository:
    """Transactional SQLite repository for scientific Knowledge persistence."""

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
                CREATE TABLE IF NOT EXISTS knowledge_objects (
                    knowledge_id TEXT PRIMARY KEY,
                    scientific_fingerprint TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    knowledge_type TEXT NOT NULL,
                    knowledge_status TEXT NOT NULL,
                    title TEXT NOT NULL,
                    registration_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS evidence_references (
                    evidence_id TEXT PRIMARY KEY,
                    knowledge_id TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_uri TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (knowledge_id) REFERENCES knowledge_objects(knowledge_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS knowledge_relationships (
                    edge_id TEXT PRIMARY KEY,
                    parent_knowledge_id TEXT NOT NULL,
                    child_knowledge_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS knowledge_audit (
                    event_id TEXT PRIMARY KEY,
                    knowledge_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    previous_state TEXT NOT NULL,
                    new_state TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    FOREIGN KEY (knowledge_id) REFERENCES knowledge_objects(knowledge_id) ON DELETE CASCADE
                );
            """)

    def save(self, record: KnowledgeRegistryRecord) -> None:
        """Persist a KnowledgeRegistryRecord transactionally.

        Args:
            record: KnowledgeRegistryRecord instance.
        """
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO knowledge_objects (
                    knowledge_id, scientific_fingerprint, canonical_hash, semantic_version,
                    knowledge_type, knowledge_status, title, registration_timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    record.knowledge_id,
                    record.scientific_fingerprint,
                    record.canonical_hash,
                    record.semantic_version,
                    record.knowledge_type.value,
                    record.knowledge_status.value,
                    record.title,
                    record.registration_timestamp,
                    json_str,
                ),
            )

            # Insert evidence references
            for evd in record.evidence_references:
                evd_json = evd.model_dump_json()
                self._conn.execute(
                    """
                    INSERT INTO evidence_references (
                        evidence_id, knowledge_id, evidence_type, source_id, source_uri, json_data
                    ) VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        evd.evidence_id,
                        record.knowledge_id,
                        evd.evidence_type.value,
                        evd.source_id,
                        evd.source_uri,
                        evd_json,
                    ),
                )

    def get_by_id(self, knowledge_id: str) -> KnowledgeRegistryRecord | None:
        """Retrieve KnowledgeRegistryRecord by Knowledge ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM knowledge_objects WHERE knowledge_id = ?;", (knowledge_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        data = json.loads(row["json_data"])
        return KnowledgeRegistryRecord(**data)

    def get_by_fingerprint(self, scientific_fingerprint: str) -> KnowledgeRegistryRecord | None:
        """Retrieve KnowledgeRegistryRecord by Scientific Fingerprint."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM knowledge_objects WHERE scientific_fingerprint = ?;", (scientific_fingerprint,))
        row = cursor.fetchone()
        if row is None:
            return None
        data = json.loads(row["json_data"])
        return KnowledgeRegistryRecord(**data)

    def list_all(self) -> list[KnowledgeRegistryRecord]:
        """List all persisted KnowledgeRegistryRecords."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM knowledge_objects ORDER BY registration_timestamp ASC;")
        rows = cursor.fetchall()
        return [KnowledgeRegistryRecord(**json.loads(row["json_data"])) for row in rows]

    def update_status(self, knowledge_id: str, new_status: KnowledgeStatus) -> None:
        """Update status of a Knowledge record."""
        rec = self.get_by_id(knowledge_id)
        if rec is None:
            raise KeyError(f"Knowledge ID '{knowledge_id}' not found in repository")

        old_status = rec.knowledge_status
        new_rec_dict = rec.model_dump()
        new_rec_dict["knowledge_status"] = new_status
        new_rec_dict["knowledge_object"]["knowledge_status"] = new_status
        updated_rec = KnowledgeRegistryRecord(**new_rec_dict)

        with self._conn:
            self._conn.execute(
                "UPDATE knowledge_objects SET knowledge_status = ?, json_data = ? WHERE knowledge_id = ?;",
                (new_status.value, updated_rec.model_dump_json(), knowledge_id),
            )

    def log_audit_event(self, event: KnowledgeAuditEvent) -> None:
        """Log audit event transactionally."""
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO knowledge_audit (
                    event_id, knowledge_id, event_type, timestamp, previous_state, new_state, provenance, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event.event_id,
                    event.knowledge_id,
                    event.event_type,
                    event.timestamp,
                    event.previous_state,
                    event.new_state,
                    event.provenance,
                    event.notes,
                ),
            )

    def get_audit_trail(self, knowledge_id: str) -> list[KnowledgeAuditEvent]:
        """Retrieve audit trail for a Knowledge ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM knowledge_audit WHERE knowledge_id = ? ORDER BY timestamp ASC;", (knowledge_id,))
        rows = cursor.fetchall()
        return [
            KnowledgeAuditEvent(
                event_id=row["event_id"],
                knowledge_id=row["knowledge_id"],
                event_type=row["event_type"],
                timestamp=row["timestamp"],
                previous_state=row["previous_state"],
                new_state=row["new_state"],
                provenance=row["provenance"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()


class KnowledgeRegistryVerifier:
    """Verifier auditing database schema integrity and tamper protection."""

    def __init__(self, repo: SQLiteKnowledgeRepository) -> None:
        self._repo = repo

    def verify_repository(self) -> list[str]:
        """Audit repository integrity returning a list of validation error strings."""
        errors: list[str] = []
        records = self._repo.list_all()

        for rec in records:
            # Verify JSON canonical hash match
            recomputed = compute_canonical_sha256(rec.knowledge_object.model_dump(mode="json"))
            if rec.canonical_hash != recomputed:
                errors.append(f"Canonical hash mismatch for Knowledge ID '{rec.knowledge_id}': stored '{rec.canonical_hash}', computed '{recomputed}'")

        return errors
