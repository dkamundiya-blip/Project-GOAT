"""
Project GOAT v0.8 — Step 7.9 Integrity Dedicated Unit Tests
"""

import pytest

from goat.archive.core.canonical import compute_archive_id
from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin
from goat.archive.core.models import ArchiveRecord
from goat.archive.retention.engine import RetentionEngine


def test_vault_tamper_detection():
    retention = RetentionEngine()
    ts = "2026-08-01T00:00:00Z"
    arc_id, _ = compute_archive_id("EXECUTION_ENGINE", "EXECUTION", "EXC_101", ts)

    corrupted_record = ArchiveRecord(
        archive_id=arc_id,
        source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
        entity_type=ArchiveEntityType.EXECUTION,
        entity_id="EXC_101",
        payload={"data": "tampered_content"},
        timestamp=ts,
        canonical_hash="INVALID_TAMPERED_HASH_1234567890ABCDEF1234567890ABCDEF12345678",
    )

    assert not retention.audit_record_integrity(corrupted_record)
    is_healthy, valid_cnt, invalid_cnt = retention.audit_vault_integrity([corrupted_record])
    assert not is_healthy
    assert invalid_cnt == 1
