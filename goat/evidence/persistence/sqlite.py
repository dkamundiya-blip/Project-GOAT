"""
Project GOAT v0.9 — SQLite Persistence Repositories for Observation & Evidence Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.evidence.core.enums import (
    EvidenceCategory,
    ObservationSource,
    ObservationStatus,
)
from goat.evidence.core.models import (
    EvidenceLink,
    EvidenceRecord,
    EvidenceSummary,
    ObservationCollection,
    ScientificObservation,
)


def init_evidence_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and pragmas for Evidence subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scientific_observations (
                observation_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                metric_value_json TEXT NOT NULL,
                unit_of_measure TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                instrument TEXT NOT NULL,
                status TEXT NOT NULL,
                observer_id TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_records (
                evidence_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                observation_ids_json TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                source TEXT NOT NULL,
                instrument TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS observation_collections (
                collection_id TEXT PRIMARY KEY,
                collection_name TEXT NOT NULL,
                observation_ids_json TEXT NOT NULL,
                start_timestamp TEXT NOT NULL,
                end_timestamp TEXT NOT NULL,
                collector_id TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_links (
                link_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                link_type TEXT NOT NULL,
                linker_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_summaries (
                summary_id TEXT PRIMARY KEY,
                total_observations INTEGER NOT NULL,
                total_evidence_records INTEGER NOT NULL,
                total_collections INTEGER NOT NULL,
                total_links INTEGER NOT NULL,
                category_counts_json TEXT NOT NULL,
                source_counts_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class ObservationRepository:
    """Repository for persisting and querying ScientificObservation instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, observation: ScientificObservation) -> ScientificObservation:
        """Insert or replace a ScientificObservation record."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO scientific_observations (
                    observation_id, metric_name, metric_value_json, unit_of_measure, timestamp,
                    source, category, instrument, status, observer_id, tags_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.observation_id,
                    observation.metric_name,
                    json.dumps(observation.metric_value),
                    observation.unit_of_measure,
                    observation.timestamp,
                    observation.source.value,
                    observation.category.value,
                    observation.instrument,
                    observation.status.value,
                    observation.observer_id,
                    json.dumps(observation.tags),
                    json.dumps(observation.metadata),
                    observation.canonical_hash,
                ),
            )
        return observation

    def get_by_id(self, observation_id: str) -> ScientificObservation | None:
        """Fetch a ScientificObservation by observation_id."""
        cursor = self._conn.execute(
            "SELECT * FROM scientific_observations WHERE observation_id = ?",
            (observation_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ScientificObservation]:
        """Fetch all ScientificObservation records sorted by timestamp."""
        cursor = self._conn.execute("SELECT * FROM scientific_observations ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def delete_by_id(self, observation_id: str) -> bool:
        """Delete an observation by ID."""
        with self._conn:
            cursor = self._conn.execute("DELETE FROM scientific_observations WHERE observation_id = ?", (observation_id,))
            return cursor.rowcount > 0

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ScientificObservation:
        return ScientificObservation(
            observation_id=row[0],
            metric_name=row[1],
            metric_value=json.loads(row[2]),
            unit_of_measure=row[3],
            timestamp=row[4],
            source=ObservationSource(row[5]),
            category=EvidenceCategory(row[6]),
            instrument=row[7],
            status=ObservationStatus(row[8]),
            observer_id=row[9],
            tags=json.loads(row[10]),
            metadata=json.loads(row[11]),
            canonical_hash=row[12],
        )


class EvidenceRepository:
    """Repository for persisting and querying EvidenceRecord instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, record: EvidenceRecord) -> EvidenceRecord:
        """Insert or replace an EvidenceRecord."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO evidence_records (
                    evidence_id, category, observation_ids_json, title, description,
                    source, instrument, timestamp, tags_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.evidence_id,
                    record.category.value,
                    json.dumps(record.observation_ids),
                    record.title,
                    record.description,
                    record.source.value,
                    record.instrument,
                    record.timestamp,
                    json.dumps(record.tags),
                    json.dumps(record.metadata),
                    record.canonical_hash,
                ),
            )
        return record

    def get_by_id(self, evidence_id: str) -> EvidenceRecord | None:
        """Fetch an EvidenceRecord by ID."""
        cursor = self._conn.execute("SELECT * FROM evidence_records WHERE evidence_id = ?", (evidence_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[EvidenceRecord]:
        """Fetch all EvidenceRecord rows sorted by timestamp."""
        cursor = self._conn.execute("SELECT * FROM evidence_records ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=row[0],
            category=EvidenceCategory(row[1]),
            observation_ids=json.loads(row[2]),
            title=row[3],
            description=row[4],
            source=ObservationSource(row[5]),
            instrument=row[6],
            timestamp=row[7],
            tags=json.loads(row[8]),
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class CollectionRepository:
    """Repository for persisting and querying ObservationCollection instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, collection: ObservationCollection) -> ObservationCollection:
        """Insert or replace an ObservationCollection."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO observation_collections (
                    collection_id, collection_name, observation_ids_json, start_timestamp,
                    end_timestamp, collector_id, tags_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    collection.collection_id,
                    collection.collection_name,
                    json.dumps(collection.observation_ids),
                    collection.start_timestamp,
                    collection.end_timestamp,
                    collection.collector_id,
                    json.dumps(collection.tags),
                    json.dumps(collection.metadata),
                    collection.canonical_hash,
                ),
            )
        return collection

    def get_by_id(self, collection_id: str) -> ObservationCollection | None:
        """Fetch an ObservationCollection by ID."""
        cursor = self._conn.execute("SELECT * FROM observation_collections WHERE collection_id = ?", (collection_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ObservationCollection]:
        """Fetch all ObservationCollection rows."""
        cursor = self._conn.execute("SELECT * FROM observation_collections ORDER BY start_timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ObservationCollection:
        return ObservationCollection(
            collection_id=row[0],
            collection_name=row[1],
            observation_ids=json.loads(row[2]),
            start_timestamp=row[3],
            end_timestamp=row[4],
            collector_id=row[5],
            tags=json.loads(row[6]),
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class LinkRepository:
    """Repository for persisting and querying EvidenceLink instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, link: EvidenceLink) -> EvidenceLink:
        """Insert or replace an EvidenceLink."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO evidence_links (
                    link_id, hypothesis_id, target_id, link_type, linker_id,
                    timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    link.link_id,
                    link.hypothesis_id,
                    link.target_id,
                    link.link_type,
                    link.linker_id,
                    link.timestamp,
                    json.dumps(link.metadata),
                    link.canonical_hash,
                ),
            )
        return link

    def get_by_hypothesis_id(self, hypothesis_id: str) -> list[EvidenceLink]:
        """Fetch links for a hypothesis ID."""
        cursor = self._conn.execute("SELECT * FROM evidence_links WHERE hypothesis_id = ? ORDER BY timestamp ASC", (hypothesis_id,))
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def get_by_target_id(self, target_id: str) -> list[EvidenceLink]:
        """Fetch links for a target ID."""
        cursor = self._conn.execute("SELECT * FROM evidence_links WHERE target_id = ? ORDER BY timestamp ASC", (target_id,))
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def list_all(self) -> list[EvidenceLink]:
        """Fetch all links."""
        cursor = self._conn.execute("SELECT * FROM evidence_links ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EvidenceLink:
        return EvidenceLink(
            link_id=row[0],
            hypothesis_id=row[1],
            target_id=row[2],
            link_type=row[3],
            linker_id=row[4],
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class SummaryRepository:
    """Repository for persisting and querying EvidenceSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: EvidenceSummary) -> EvidenceSummary:
        """Insert or replace an EvidenceSummary."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO evidence_summaries (
                    summary_id, total_observations, total_evidence_records, total_collections,
                    total_links, category_counts_json, source_counts_json, timestamp,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.total_observations,
                    summary.total_evidence_records,
                    summary.total_collections,
                    summary.total_links,
                    json.dumps(summary.category_counts),
                    json.dumps(summary.source_counts),
                    summary.timestamp,
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> EvidenceSummary | None:
        """Fetch a summary by summary_id."""
        cursor = self._conn.execute("SELECT * FROM evidence_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EvidenceSummary:
        return EvidenceSummary(
            summary_id=row[0],
            total_observations=row[1],
            total_evidence_records=row[2],
            total_collections=row[3],
            total_links=row[4],
            category_counts=json.loads(row[5]),
            source_counts=json.loads(row[6]),
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class EvidencePersistenceContext:
    """Unified Persistence Context wrapping SQLite repositories for evidence subsystem."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_evidence_db(self.conn)
        self.observations = ObservationRepository(self.conn)
        self.evidence_records = EvidenceRepository(self.conn)
        self.collections = CollectionRepository(self.conn)
        self.links = LinkRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
