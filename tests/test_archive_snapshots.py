"""
Project GOAT v0.8 — Step 7.9 Snapshot Engine Dedicated Unit Tests
"""

import pytest

from goat.archive.core.enums import SnapshotType
from goat.archive.snapshots.engine import SnapshotEngine


def test_snapshot_manifest_creation_and_verification():
    engine = SnapshotEngine()
    ts = "2026-08-01T00:00:00Z"

    manifest = engine.create_snapshot(
        snapshot_type=SnapshotType.PORTFOLIO,
        state_data={"balance": 10000.0, "open_positions": 2},
        timestamp=ts,
    )

    assert manifest.manifest_id.startswith("SNP_")
    assert engine.verify_snapshot(manifest)
    assert engine.get_latest_snapshot(SnapshotType.PORTFOLIO) == manifest
