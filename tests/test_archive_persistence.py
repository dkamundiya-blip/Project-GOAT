"""
Project GOAT v0.8 — Step 7.9 Persistence Dedicated Unit Tests
"""

import tempfile
from pathlib import Path

import pytest

from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin, SnapshotType
from goat.archive.engine import ArchiveEngine
from goat.archive.persistence.repository import SQLiteArchiveRepository


def test_sqlite_archive_persistence_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_archive.db"
        engine = ArchiveEngine(db_path=db_path)
        ts = "2026-08-01T00:00:00Z"

        record = engine.ingest_record(
            source_subsystem=ArchiveSubsystemOrigin.PORTFOLIO_ENGINE,
            entity_type=ArchiveEntityType.PORTFOLIO_STATE,
            entity_id="PF_101",
            payload={"balance": 50000.0},
            timestamp=ts,
        )

        snp = engine.create_snapshot(SnapshotType.PORTFOLIO, {"balance": 50000.0}, ts)

        engine.close()

        # Verify database contents directly
        repo = SQLiteArchiveRepository(db_path)
        db_rec = repo.get_record(record.archive_id)
        assert db_rec is not None
        assert db_rec.entity_id == "PF_101"

        repo.close()
