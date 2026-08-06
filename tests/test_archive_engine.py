"""
Project GOAT v0.8 — Master ArchiveEngine Dedicated Unit Tests
"""

import pytest

from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin, SnapshotType
from goat.archive.engine import ArchiveEngine


def test_archive_engine_master_workflow():
    engine = ArchiveEngine()
    ts = "2026-08-01T00:00:00Z"

    # Ingest record
    rec = engine.ingest_record(
        source_subsystem=ArchiveSubsystemOrigin.NOTIFICATION_PLATFORM,
        entity_type=ArchiveEntityType.NOTIFICATION,
        entity_id="NTF_001",
        payload={"subject": "Test Alert"},
        timestamp=ts,
    )
    assert rec.archive_id.startswith("ARC_")

    # Replay
    session, replayed, checkpoints = engine.replay(
        start_time="2026-08-01T00:00:00Z",
        end_time="2026-08-01T01:00:00Z",
        execution_timestamp="2026-08-01T01:05:00Z",
    )
    assert len(replayed) == 1
    assert replayed[0].archive_id == rec.archive_id

    # Snapshot
    snp = engine.create_snapshot(SnapshotType.SYSTEM_HEALTH, {"status": "HEALTHY"}, ts)
    assert snp.manifest_id.startswith("SNP_")

    # Integrity & Summary
    report, is_healthy = engine.audit_integrity(ts)
    assert is_healthy

    summary = engine.get_summary(ts)
    assert summary.total_records == 1
    assert summary.total_sessions == 1
