"""
Project GOAT v0.8 — Step 7.9 Archive Models Dedicated Unit Tests
"""

import pytest
from pydantic import ValidationError

from goat.archive.core.canonical import (
    compute_archive_id,
    compute_batch_id,
    compute_replay_checkpoint_id,
    compute_replay_request_id,
    compute_replay_session_id,
    compute_snapshot_manifest_id,
    compute_statistics_id,
    compute_summary_id,
)
from goat.archive.core.enums import (
    ArchiveEntityType,
    ArchiveSubsystemOrigin,
    ReplayStatus,
    SnapshotType,
)
from goat.archive.core.models import (
    ArchiveBatch,
    ArchiveRecord,
    ArchiveStatistics,
    ArchiveSummary,
    ReplayCheckpoint,
    ReplayRequest,
    ReplaySession,
    SnapshotManifest,
)


def test_canonical_id_prefixes():
    arc_id, arc_hash = compute_archive_id("EXECUTION_ENGINE", "EXECUTION", "EXC_101", "2026-08-01T00:00:00Z")
    assert arc_id.startswith("ARC_")
    assert len(arc_id) == 20
    assert len(arc_hash) == 64

    abt_id, abt_hash = compute_batch_id(10, "2026-08-01T00:00:00Z")
    assert abt_id.startswith("ABT_")
    assert len(abt_id) == 20

    rrq_id, rrq_hash = compute_replay_request_id("2026-08-01T00:00:00Z", "2026-08-01T01:00:00Z")
    assert rrq_id.startswith("RRQ_")
    assert len(rrq_id) == 20

    rps_id, rps_hash = compute_replay_session_id(rrq_id, "2026-08-01T00:00:00Z")
    assert rps_id.startswith("RPS_")
    assert len(rps_id) == 20

    rcp_id, rcp_hash = compute_replay_checkpoint_id(1, arc_id, "2026-08-01T00:00:00Z")
    assert rcp_id.startswith("RCP_")
    assert len(rcp_id) == 20

    snp_id, snp_hash = compute_snapshot_manifest_id("PORTFOLIO", "2026-08-01T00:00:00Z")
    assert snp_id.startswith("SNP_")
    assert len(snp_id) == 20

    ast_id, ast_hash = compute_statistics_id(100, "2026-08-01T00:00:00Z")
    assert ast_id.startswith("AST_")
    assert len(ast_id) == 20

    asm_id, asm_hash = compute_summary_id(100, "2026-08-01T00:00:00Z")
    assert asm_id.startswith("ASM_")
    assert len(asm_id) == 20


def test_archive_model_immutability():
    arc_id, arc_hash = compute_archive_id("EXECUTION_ENGINE", "EXECUTION", "EXC_101", "2026-08-01T00:00:00Z")
    record = ArchiveRecord(
        archive_id=arc_id,
        source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
        entity_type=ArchiveEntityType.EXECUTION,
        entity_id="EXC_101",
        payload={"order_id": "101"},
        timestamp="2026-08-01T00:00:00Z",
        canonical_hash=arc_hash,
    )

    with pytest.raises(ValidationError):
        record.entity_id = "EXC_MODIFIED"


def test_archive_model_extra_forbid():
    arc_id, arc_hash = compute_archive_id("EXECUTION_ENGINE", "EXECUTION", "EXC_101", "2026-08-01T00:00:00Z")
    with pytest.raises(ValidationError):
        ArchiveRecord(
            archive_id=arc_id,
            source_subsystem=ArchiveSubsystemOrigin.EXECUTION_ENGINE,
            entity_type=ArchiveEntityType.EXECUTION,
            entity_id="EXC_101",
            payload={"order_id": "101"},
            timestamp="2026-08-01T00:00:00Z",
            canonical_hash=arc_hash,
            extra_field="invalid",
        )


@pytest.mark.parametrize("idx", range(150))
def test_archive_model_serialization_matrix(idx):
    arc_id, arc_hash = compute_archive_id("LIVE_MARKET_DATA", "MARKET_TICK", f"TICK_{idx}", f"2026-08-01T00:{idx % 60:02d}:00Z")
    record = ArchiveRecord(
        archive_id=arc_id,
        source_subsystem=ArchiveSubsystemOrigin.LIVE_MARKET_DATA,
        entity_type=ArchiveEntityType.MARKET_TICK,
        entity_id=f"TICK_{idx}",
        payload={"price": 1.0850 + idx * 0.0001},
        timestamp=f"2026-08-01T00:{idx % 60:02d}:00Z",
        canonical_hash=arc_hash,
    )
    json_str = record.model_dump_json()
    reloaded = ArchiveRecord.model_validate_json(json_str)
    assert reloaded == record
