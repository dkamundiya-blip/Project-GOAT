"""
Project GOAT v0.8 — Institutional Research Archive Vault Package

Export every public symbol through __all__. No namespace leakage.
"""

from goat.archive.core.canonical import (
    compute_archive_id,
    compute_batch_id,
    compute_replay_checkpoint_id,
    compute_replay_request_id,
    compute_replay_session_id,
    compute_snapshot_manifest_id,
    compute_statistics_id,
    compute_summary_id,
)
from goat.archive.core.enums import (
    ArchiveAuditEventType,
    ArchiveEntityType,
    ArchiveRetentionPolicy,
    ArchiveSubsystemOrigin,
    ReplayStatus,
    SnapshotType,
)
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
from goat.archive.engine import ArchiveEngine
from goat.archive.indexing.engine import ArchiveIndexEngine
from goat.archive.ingestion.engine import ArchiveIngestionEngine
from goat.archive.persistence.repository import (
    ArchiveReportRepository,
    ArchiveRepository,
    ReplayRepository,
    SnapshotRepository,
    SQLiteArchiveRepository,
    StatisticsRepository,
)
from goat.archive.replay.engine import ReplayEngine
from goat.archive.reporting.reports import (
    ArchiveExecutiveReport,
    ArchiveReport,
    ArchiveReportEngine,
    ArchiveStatisticsReport,
    BaseArchiveReport,
    IntegrityReport,
    ReplayReport,
    SnapshotReport,
)
from goat.archive.retention.engine import RetentionEngine
from goat.archive.snapshots.engine import SnapshotEngine

__all__ = [
    # Master Coordinator
    "ArchiveEngine",
    # Subsystem Engines
    "ArchiveIngestionEngine",
    "ArchiveIndexEngine",
    "ReplayEngine",
    "SnapshotEngine",
    "RetentionEngine",
    "ArchiveReportEngine",
    # Enums
    "ArchiveSubsystemOrigin",
    "ArchiveEntityType",
    "ReplayStatus",
    "SnapshotType",
    "ArchiveRetentionPolicy",
    "ArchiveAuditEventType",
    # Canonical SHA-256 Generators
    "compute_archive_id",
    "compute_batch_id",
    "compute_replay_request_id",
    "compute_replay_session_id",
    "compute_replay_checkpoint_id",
    "compute_snapshot_manifest_id",
    "compute_statistics_id",
    "compute_summary_id",
    # Domain Models
    "ArchiveRecord",
    "ArchiveBatch",
    "ReplayRequest",
    "ReplaySession",
    "ReplayCheckpoint",
    "SnapshotManifest",
    "ArchiveStatistics",
    "ArchiveSummary",
    # Persistence Repositories
    "SQLiteArchiveRepository",
    "ArchiveRepository",
    "ReplayRepository",
    "SnapshotRepository",
    "StatisticsRepository",
    "ArchiveReportRepository",
    # Reports
    "BaseArchiveReport",
    "ArchiveReport",
    "ReplayReport",
    "SnapshotReport",
    "IntegrityReport",
    "ArchiveStatisticsReport",
    "ArchiveExecutiveReport",
]
