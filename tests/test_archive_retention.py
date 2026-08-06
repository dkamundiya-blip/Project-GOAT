"""
Project GOAT v0.8 — Step 7.9 Retention Engine Dedicated Unit Tests
"""

import pytest

from goat.archive.core.canonical import compute_archive_id
from goat.archive.core.enums import ArchiveEntityType, ArchiveRetentionPolicy, ArchiveSubsystemOrigin
from goat.archive.core.models import ArchiveRecord
from goat.archive.retention.engine import RetentionEngine


def test_retention_policy_and_integrity_audit():
    retention = RetentionEngine()
    assert retention.policy == ArchiveRetentionPolicy.APPEND_ONLY

    ts = "2026-08-01T00:00:00Z"
    arc_id, arc_hash = compute_archive_id("EXECUTION_ENGINE", "EXECUTION", "EXC_101", ts)
    record = ArchiveRecord(
        archive_id=arc_id,
        source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
        entity_type=ArchiveEntityType.EXECUTION,
        entity_id="EXC_101",
        payload={"data": "test"},
        timestamp=ts,
        canonical_hash=arc_hash,
    )

    assert retention.audit_record_integrity(record)

    is_healthy, valid_cnt, invalid_cnt = retention.audit_vault_integrity([record])
    assert is_healthy
    assert valid_cnt == 1
    assert invalid_cnt == 0
