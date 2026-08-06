"""
Project GOAT v0.8 — Step 7.9 Public API Dedicated Unit Tests
"""

import pytest

import goat.archive as archive_pkg


def test_public_api_exports():
    expected_exports = [
        "ArchiveEngine",
        "ArchiveIngestionEngine",
        "ArchiveIndexEngine",
        "ReplayEngine",
        "SnapshotEngine",
        "RetentionEngine",
        "ArchiveReportEngine",
        "ArchiveSubsystemOrigin",
        "ArchiveEntityType",
        "ReplayStatus",
        "SnapshotType",
        "ArchiveRetentionPolicy",
        "ArchiveAuditEventType",
        "compute_archive_id",
        "compute_batch_id",
        "compute_replay_request_id",
        "compute_replay_session_id",
        "compute_replay_checkpoint_id",
        "compute_snapshot_manifest_id",
        "compute_statistics_id",
        "compute_summary_id",
        "ArchiveRecord",
        "ArchiveBatch",
        "ReplayRequest",
        "ReplaySession",
        "ReplayCheckpoint",
        "SnapshotManifest",
        "ArchiveStatistics",
        "ArchiveSummary",
        "SQLiteArchiveRepository",
        "ArchiveRepository",
        "ReplayRepository",
        "SnapshotRepository",
        "StatisticsRepository",
        "ArchiveReportRepository",
        "BaseArchiveReport",
        "ArchiveReport",
        "ReplayReport",
        "SnapshotReport",
        "IntegrityReport",
        "ArchiveStatisticsReport",
        "ArchiveExecutiveReport",
    ]

    for item in expected_exports:
        assert hasattr(archive_pkg, item)
    assert set(archive_pkg.__all__) == set(expected_exports)
