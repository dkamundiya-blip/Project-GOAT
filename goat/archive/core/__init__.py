"""
Project GOAT v0.8 — Archive Core Package
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

__all__ = [
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
]
