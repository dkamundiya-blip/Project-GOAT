"""
Project GOAT v0.8 — Archive Engine Master Coordinator

Master coordinator implementing canonical Institutional Research Archive Vault & Deterministic Replay System.
Integrates ArchiveIngestionEngine, ArchiveIndexEngine, ReplayEngine, SnapshotEngine,
RetentionEngine, SQLiteArchiveRepository, and ArchiveReportEngine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from goat.archive.core.canonical import compute_summary_id
from goat.archive.core.enums import (
    ArchiveEntityType,
    ArchiveSubsystemOrigin,
    SnapshotType,
)
from goat.archive.core.models import (
    ArchiveBatch,
    ArchiveRecord,
    ArchiveSummary,
    ReplayCheckpoint,
    ReplayRequest,
    ReplaySession,
    SnapshotManifest,
)
from goat.archive.indexing.engine import ArchiveIndexEngine
from goat.archive.ingestion.engine import ArchiveIngestionEngine
from goat.archive.persistence.repository import SQLiteArchiveRepository
from goat.archive.replay.engine import ReplayEngine
from goat.archive.reporting.reports import ArchiveExecutiveReport, ArchiveReportEngine, IntegrityReport
from goat.archive.retention.engine import RetentionEngine
from goat.archive.snapshots.engine import SnapshotEngine


class ArchiveEngine:
    """Master coordinator managing append-only vault storage, indexing, replay, and snapshot manifests."""

    def __init__(self, db_path: str | Path | None = None):
        self.ingestion_engine = ArchiveIngestionEngine()
        self.index_engine = ArchiveIndexEngine()
        self.replay_engine = ReplayEngine()
        self.snapshot_engine = SnapshotEngine()
        self.retention_engine = RetentionEngine()
        self.report_engine = ArchiveReportEngine()

        self.repository = SQLiteArchiveRepository(db_path) if db_path else None

    def close(self) -> None:
        """Close database connection if active."""
        if self.repository:
            self.repository.close()

    def ingest_record(
        self,
        source_subsystem: ArchiveSubsystemOrigin | str,
        entity_type: ArchiveEntityType | str,
        entity_id: str,
        payload: dict[str, Any],
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> ArchiveRecord:
        """Ingest an immutable event record into the vault."""
        record = self.ingestion_engine.ingest_record(
            source_subsystem=source_subsystem,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            timestamp=timestamp,
            metadata=metadata,
        )

        self.index_engine.index_record(record)

        if self.repository:
            self.repository.save_record(record)

        return record

    def commit_batch(self, timestamp: str, metadata: dict[str, Any] | None = None) -> ArchiveBatch:
        """Commit queued records into an ArchiveBatch manifest."""
        return self.ingestion_engine.commit_batch(timestamp, metadata)

    def replay(
        self,
        start_time: str,
        end_time: str,
        execution_timestamp: str,
        subsystems: list[ArchiveSubsystemOrigin | str] | None = None,
        entity_types: list[ArchiveEntityType | str] | None = None,
        instrument: str = "",
        session_id: str = "",
    ) -> tuple[ReplaySession, list[ArchiveRecord], list[ReplayCheckpoint]]:
        """Reconstruct historical event stream in exact original order."""
        request = self.replay_engine.create_replay_request(
            start_time=start_time,
            end_time=end_time,
            subsystems=subsystems,
            entity_types=entity_types,
            instrument=instrument,
            session_id=session_id,
        )

        records = self.ingestion_engine.get_all_records()
        session, replayed_records, checkpoints = self.replay_engine.execute_replay(
            request=request,
            records=records,
            execution_timestamp=execution_timestamp,
        )

        if self.repository:
            self.repository.save_replay_session(session)

        return session, replayed_records, checkpoints

    def create_snapshot(
        self,
        snapshot_type: SnapshotType | str,
        state_data: dict[str, Any],
        timestamp: str,
    ) -> SnapshotManifest:
        """Create a state snapshot manifest."""
        manifest = self.snapshot_engine.create_snapshot(snapshot_type, state_data, timestamp)
        if self.repository:
            self.repository.save_snapshot(manifest)
        return manifest

    def audit_integrity(self, timestamp: str) -> tuple[IntegrityReport, bool]:
        """Audit vault records for cryptographic hash consistency."""
        records = self.ingestion_engine.get_all_records()
        is_healthy, valid_cnt, invalid_cnt = self.retention_engine.audit_vault_integrity(records)
        report = self.report_engine.build_integrity_report(is_healthy, valid_cnt, invalid_cnt, timestamp)
        return report, is_healthy

    def get_summary(self, timestamp: str) -> ArchiveSummary:
        """Compute aggregated ArchiveSummary metrics."""
        records = self.ingestion_engine.get_all_records()
        sessions = self.replay_engine.get_all_sessions()
        is_healthy, _, _ = self.retention_engine.audit_vault_integrity(records)

        asm_id, asm_hash = compute_summary_id(len(records), timestamp)

        return ArchiveSummary(
            summary_id=asm_id,
            total_records=len(records),
            total_sessions=len(sessions),
            integrity_status="VERIFIED_HEALTHY" if is_healthy else "TAMPER_DETECTED",
            timestamp=timestamp,
            canonical_hash=asm_hash,
        )

    def generate_executive_report(self, timestamp: str) -> ArchiveExecutiveReport:
        """Generate Vault Executive Report in Markdown and JSON formats."""
        summary = self.get_summary(timestamp)
        recent_records = self.ingestion_engine.get_all_records()[-20:]
        sessions = self.replay_engine.get_all_sessions()

        report = self.report_engine.build_executive_report(summary, recent_records, sessions)

        if self.repository:
            self.repository.save_report(f"REP_{summary.summary_id[4:]}", "EXECUTIVE", timestamp, report.to_markdown(), report.get_dict())

        return report
