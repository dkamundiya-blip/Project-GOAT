"""
Project GOAT v0.8 — Step 7.9 Ingestion Engine Dedicated Unit Tests
"""

import pytest

from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin
from goat.archive.ingestion.engine import ArchiveIngestionEngine


def test_ingestion_append_only():
    ingestion = ArchiveIngestionEngine()
    ts = "2026-08-01T00:00:00Z"

    r1 = ingestion.ingest_record(
        source_subsystem=ArchiveSubsystemOrigin.SIGNAL_GENERATED if hasattr(ArchiveSubsystemOrigin, "SIGNAL_GENERATED") else ArchiveSubsystemOrigin.SCIENTIFIC_RESEARCH,
        entity_type=ArchiveEntityType.SIGNAL,
        entity_id="SIG_001",
        payload={"symbol": "EURUSD", "side": "BUY"},
        timestamp=ts,
    )
    assert r1.archive_id.startswith("ARC_")

    r2 = ingestion.ingest_record(
        source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
        entity_type=ArchiveEntityType.EXECUTION,
        entity_id="EXC_001",
        payload={"symbol": "EURUSD", "volume": 1.0},
        timestamp=ts,
    )
    assert r2.archive_id.startswith("ARC_")

    records = ingestion.get_all_records()
    assert len(records) == 2

    batch = ingestion.commit_batch(ts)
    assert batch.batch_id.startswith("ABT_")
    assert batch.record_count == 2
