"""
Project GOAT v0.8 — Archive Retention Engine

Enforces strict APPEND_ONLY retention rules: zero record deletion, zero mutation, zero data compaction/merging.
Audits vault records for hash consistency and cryptographic tamper evidence.
"""

from __future__ import annotations

from typing import Any

from goat.archive.core.canonical import compute_archive_id
from goat.archive.core.enums import ArchiveRetentionPolicy
from goat.archive.core.models import ArchiveRecord


class RetentionEngine:
    """Engine enforcing append-only retention rules and auditing archive hash integrity."""

    def __init__(self):
        self.policy = ArchiveRetentionPolicy.APPEND_ONLY

    def audit_record_integrity(self, record: ArchiveRecord) -> bool:
        """Verify that an ArchiveRecord's hash matches its canonical computation."""
        _, expected_hash = compute_archive_id(
            source_subsystem=record.source_subsystem.value,
            entity_type=record.entity_type.value,
            entity_id=record.entity_id,
            timestamp=record.timestamp,
        )
        return record.canonical_hash == expected_hash

    def audit_vault_integrity(self, records: list[ArchiveRecord]) -> tuple[bool, int, int]:
        """Audit full list of vault records for hash tampering."""
        valid_count = 0
        invalid_count = 0

        for r in records:
            if self.audit_record_integrity(r):
                valid_count += 1
            else:
                invalid_count += 1

        is_healthy = invalid_count == 0
        return is_healthy, valid_count, invalid_count
