"""
Project GOAT v0.8 — Snapshot Engine

Generates SHA-256 integrity-verified state manifests for portfolio, market state, broker account, system health, execution state, and archive statistics.
"""

from __future__ import annotations

from typing import Any

from goat.archive.core.canonical import compute_snapshot_manifest_id
from goat.archive.core.enums import SnapshotType
from goat.archive.core.models import SnapshotManifest


class SnapshotEngine:
    """Engine capturing deterministic state snapshot manifests."""

    def __init__(self):
        self._manifests: list[SnapshotManifest] = []

    def create_snapshot(
        self,
        snapshot_type: SnapshotType | str,
        state_data: dict[str, Any],
        timestamp: str,
    ) -> SnapshotManifest:
        """Capture an immutable state snapshot manifest with SHA-256 integrity hashing."""
        type_enum = (
            SnapshotType(str(snapshot_type).upper())
            if not isinstance(snapshot_type, SnapshotType)
            else snapshot_type
        )

        snp_id, snp_hash = compute_snapshot_manifest_id(
            snapshot_type=type_enum.value,
            timestamp=timestamp,
        )

        manifest = SnapshotManifest(
            manifest_id=snp_id,
            snapshot_type=type_enum,
            state_data=state_data,
            timestamp=timestamp,
            canonical_hash=snp_hash,
        )

        self._manifests.append(manifest)
        return manifest

    def verify_snapshot(self, manifest: SnapshotManifest) -> bool:
        """Verify hash integrity of a SnapshotManifest."""
        _, expected_hash = compute_snapshot_manifest_id(
            snapshot_type=manifest.snapshot_type.value,
            timestamp=manifest.timestamp,
        )
        return manifest.canonical_hash == expected_hash

    def get_latest_snapshot(self, snapshot_type: SnapshotType | str) -> SnapshotManifest | None:
        type_enum = (
            SnapshotType(str(snapshot_type).upper())
            if not isinstance(snapshot_type, SnapshotType)
            else snapshot_type
        )
        for m in reversed(self._manifests):
            if m.snapshot_type == type_enum:
                return m
        return None

    def get_all_snapshots(self) -> list[SnapshotManifest]:
        return list(self._manifests)
