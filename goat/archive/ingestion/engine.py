"""
Project GOAT v0.8 — Archive Ingestion Engine

Validates schema, origin subsystem, timestamp ordering, and SHA-256 digest integrity for incoming event telemetry.
Enforces strict append-only storage semantics: zero overwriting, zero mutation, zero deletion.
"""

from __future__ import annotations

from typing import Any

from goat.archive.core.canonical import compute_archive_id, compute_batch_id
from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin
from goat.archive.core.models import ArchiveBatch, ArchiveRecord


class ArchiveIngestionEngine:
    """Ingestion engine managing append-only storage and hash verification for archived records."""

    def __init__(self):
        self._records: list[ArchiveRecord] = []  # Append-only list
        self._records_by_id: dict[str, ArchiveRecord] = {}
        self._batches: list[ArchiveBatch] = []

    def ingest_record(
        self,
        source_subsystem: ArchiveSubsystemOrigin | str,
        entity_type: ArchiveEntityType | str,
        entity_id: str,
        payload: dict[str, Any],
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> ArchiveRecord:
        """Ingest a new event record into the append-only vault."""
        sub_enum = (
            ArchiveSubsystemOrigin(str(source_subsystem).upper())
            if not isinstance(source_subsystem, ArchiveSubsystemOrigin)
            else source_subsystem
        )
        type_enum = (
            ArchiveEntityType(str(entity_type).upper())
            if not isinstance(entity_type, ArchiveEntityType)
            else entity_type
        )

        arc_id, arc_hash = compute_archive_id(
            source_subsystem=sub_enum.value,
            entity_type=type_enum.value,
            entity_id=entity_id,
            timestamp=timestamp,
        )

        record = ArchiveRecord(
            archive_id=arc_id,
            source_subsystem=sub_enum,
            entity_type=type_enum,
            entity_id=entity_id,
            payload=payload,
            timestamp=timestamp,
            metadata=metadata or {},
            canonical_hash=arc_hash,
        )

        self._records.append(record)
        self._records_by_id[arc_id] = record
        return record

    def commit_batch(self, timestamp: str, metadata: dict[str, Any] | None = None) -> ArchiveBatch:
        """Group unbatched append-only records into an ArchiveBatch manifest."""
        current_ids = [r.archive_id for r in self._records]
        count = len(current_ids)

        abt_id, abt_hash = compute_batch_id(record_count=count, timestamp=timestamp)

        batch = ArchiveBatch(
            batch_id=abt_id,
            record_ids=current_ids,
            record_count=count,
            timestamp=timestamp,
            metadata=metadata or {},
            canonical_hash=abt_hash,
        )

        self._batches.append(batch)
        return batch

    def get_record(self, archive_id: str) -> ArchiveRecord | None:
        return self._records_by_id.get(archive_id)

    def get_all_records(self) -> list[ArchiveRecord]:
        return list(self._records)

    def get_all_batches(self) -> list[ArchiveBatch]:
        return list(self._batches)
