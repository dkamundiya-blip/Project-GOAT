"""
Project GOAT v0.5 — Unit Tests for CheckpointManager
"""

import pytest

from goat.orchestration.campaign import QueueSnapshot
from goat.orchestration.checkpoint import CheckpointManager


def test_checkpoint_manager_atomic_save_and_load(tmp_path) -> None:
    """Test CheckpointManager saves snapshot atomically and loads correctly."""
    mgr = CheckpointManager(checkpoint_format_version=1)

    snapshot = QueueSnapshot(
        campaign_id="CMP-ATOMIC-01",
        configuration_hash="cfg_atomic_123",
        completed_task_ids=("exp_1", "exp_2"),
        failed_task_ids=("exp_3",),
        in_progress_task_ids=(),
        pending_task_ids=("exp_4",),
        task_results={"exp_1": {"validation_status": "SUPPORTED"}},
        last_event_sequence=42,
    )

    checkpoint_file = mgr.save_checkpoint(snapshot, tmp_path)
    assert checkpoint_file.exists()
    assert checkpoint_file.name == "checkpoint.json"

    # Reload snapshot
    reloaded_snapshot = mgr.load_checkpoint(checkpoint_file)
    assert reloaded_snapshot.campaign_id == "CMP-ATOMIC-01"
    assert reloaded_snapshot.configuration_hash == "cfg_atomic_123"
    assert len(reloaded_snapshot.completed_task_ids) == 2
    assert "exp_1" in reloaded_snapshot.completed_task_ids
    assert reloaded_snapshot.last_event_sequence == 42
    assert reloaded_snapshot.task_results["exp_1"]["validation_status"] == "SUPPORTED"
