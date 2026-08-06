"""
Project GOAT v0.8 — Step 7.9 Index Engine Dedicated Unit Tests
"""

import pytest

from goat.archive.core.canonical import compute_archive_id
from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin
from goat.archive.core.models import ArchiveRecord
from goat.archive.indexing.engine import ArchiveIndexEngine


def test_secondary_indexing_queries():
    indexer = ArchiveIndexEngine()
    ts = "2026-08-01T00:00:00Z"

    arc_id, arc_hash = compute_archive_id("EXECUTION_ENGINE", "EXECUTION", "EXC_101", ts)
    record = ArchiveRecord(
        archive_id=arc_id,
        source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
        entity_type=ArchiveEntityType.EXECUTION,
        entity_id="EXC_101",
        payload={"instrument": "EURUSD", "signal_id": "SIG_999"},
        timestamp=ts,
        canonical_hash=arc_hash,
    )

    indexer.index_record(record)

    by_sub = indexer.query_by_subsystem(ArchiveSubsystemOrigin.EXECUTION_ENGINE)
    assert len(by_sub) == 1

    by_type = indexer.query_by_entity_type(ArchiveEntityType.EXECUTION)
    assert len(by_type) == 1

    by_inst = indexer.query_by_instrument("EURUSD")
    assert len(by_inst) == 1
