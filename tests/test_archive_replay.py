"""
Project GOAT v0.8 — Step 7.9 Replay Engine Dedicated Unit Tests
"""

import pytest

from goat.archive.core.canonical import compute_archive_id
from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin, ReplayStatus
from goat.archive.core.models import ArchiveRecord
from goat.archive.replay.engine import ReplayEngine


def test_replay_chronological_reconstruction():
    replay_eng = ReplayEngine()

    records = []
    for idx in range(10):
        ts = f"2026-08-01T00:{idx % 60:02d}:00Z"
        arc_id, arc_hash = compute_archive_id("EXECUTION_ENGINE", "EXECUTION", f"EXC_{idx}", ts)
        r = ArchiveRecord(
            archive_id=arc_id,
            source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
            entity_type=ArchiveEntityType.EXECUTION,
            entity_id=f"EXC_{idx}",
            payload={"idx": idx},
            timestamp=ts,
            canonical_hash=arc_hash,
        )
        records.append(r)

    req = replay_eng.create_replay_request(
        start_time="2026-08-01T00:00:00Z",
        end_time="2026-08-01T00:10:00Z",
        subsystems=[ArchiveSubsystemOrigin.EXECUTION_ENGINE],
    )

    session, replayed, checkpoints = replay_eng.execute_replay(req, records, "2026-08-01T00:15:00Z")
    assert session.status == ReplayStatus.COMPLETED
    assert len(replayed) == 10
    assert len(checkpoints) == 10
    assert checkpoints[0].sequence == 1
