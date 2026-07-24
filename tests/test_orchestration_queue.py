"""
Project GOAT v0.5 — Unit Tests for ExperimentQueue
"""

import pytest

from goat.orchestration.campaign import ExperimentStatus, QueueSnapshot
from goat.orchestration.queue import ExperimentQueue, ExperimentTask
from goat.research.hypothesis.definition import HypothesisDefinition


def dummy_hypothesis(hyp_id: str) -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name=f"Hypothesis {hyp_id}",
        description="Test hypothesis",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
    )


def test_experiment_queue_canonical_ordering() -> None:
    """Test ExperimentQueue returns tasks strictly ordered by canonical_sort_key."""
    t1 = ExperimentTask("exp_z", dummy_hypothesis("HZ"), "R_75", "M1", priority=1)
    t2 = ExperimentTask("exp_a", dummy_hypothesis("HA"), "R_10", "M1", priority=0)
    t3 = ExperimentTask("exp_b", dummy_hypothesis("HB"), "R_10", "M1", priority=0)

    queue = ExperimentQueue("CMP-001", "cfg_001", tasks=[t1, t2, t3])

    # Canonical order: (priority=0, R_10, M1, exp_a) -> (priority=0, R_10, M1, exp_b) -> (priority=1, R_75, M1, exp_z)
    next_task = queue.get_next_task()
    assert next_task is not None
    assert next_task.experiment_id == "exp_a"

    queue.update_status("exp_a", ExperimentStatus.RUNNING)
    queue.update_status("exp_a", ExperimentStatus.COMPLETED)

    next_task_2 = queue.get_next_task()
    assert next_task_2 is not None
    assert next_task_2.experiment_id == "exp_b"


def test_experiment_queue_transition_guards() -> None:
    """Test ExperimentQueue enforces valid state transition guards."""
    t1 = ExperimentTask("exp_1", dummy_hypothesis("H1"), "R_10", "M1")
    queue = ExperimentQueue("CMP-001", "cfg_001", tasks=[t1])

    # Valid transition: PENDING -> RUNNING -> COMPLETED
    queue.update_status("exp_1", ExperimentStatus.RUNNING)
    assert t1.status == ExperimentStatus.RUNNING

    # Invalid transition: COMPLETED -> PENDING raises ValueError
    queue.update_status("exp_1", ExperimentStatus.COMPLETED)
    with pytest.raises(ValueError):
        queue.update_status("exp_1", ExperimentStatus.PENDING)


def test_experiment_queue_snapshot_restore() -> None:
    """Test ExperimentQueue snapshot export and class factory restoration."""
    t1 = ExperimentTask("exp_1", dummy_hypothesis("H1"), "R_10", "M1")
    t2 = ExperimentTask("exp_2", dummy_hypothesis("H2"), "R_10", "M1")

    queue = ExperimentQueue("CMP-001", "cfg_001", tasks=[t1, t2])
    queue.update_status("exp_1", ExperimentStatus.RUNNING)
    queue.update_status("exp_1", ExperimentStatus.COMPLETED, result={"score": 85.0})
    queue.update_status("exp_2", ExperimentStatus.RUNNING)  # In progress during crash

    snapshot = queue.take_snapshot(last_event_sequence=15)
    assert len(snapshot.completed_task_ids) == 1
    assert len(snapshot.in_progress_task_ids) == 1
    assert snapshot.last_event_sequence == 15

    # Re-instantiate queue from snapshot using class factory
    fresh_queue = ExperimentQueue.from_snapshot(snapshot, tasks=[t1, t2])

    # exp_1 remains COMPLETED
    assert fresh_queue.get_task("exp_1").status == ExperimentStatus.COMPLETED
    # exp_2 (interrupted RUNNING) resets to PENDING
    assert fresh_queue.get_task("exp_2").status == ExperimentStatus.PENDING
