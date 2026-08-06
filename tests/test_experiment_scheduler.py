"""
Project GOAT v0.9 — Dedicated Unit Tests for Experiment Scheduling Engine
"""

import pytest

from goat.experiments.core.enums import ExperimentPriority
from goat.experiments.lifecycle.engine import ScientificExperimentLifecycleEngine
from goat.experiments.scheduling.engine import ExperimentSchedulingEngine


@pytest.fixture
def lfc_engine():
    return ScientificExperimentLifecycleEngine()


@pytest.fixture
def sch_engine():
    return ExperimentSchedulingEngine()


@pytest.mark.parametrize("priority", list(ExperimentPriority))
def test_schedule_experiment_success(
    lfc_engine: ScientificExperimentLifecycleEngine,
    sch_engine: ExperimentSchedulingEngine,
    priority: ExperimentPriority,
):
    exp, _ = lfc_engine.create_experiment(
        hypothesis_id="HYP_1234567890ABCDEF",
        title=f"Scheduled Exp {priority.value}",
        priority=priority,
    )

    schedule = sch_engine.schedule_experiment(exp)

    assert schedule.schedule_id.startswith("SCH_")
    assert schedule.experiment_id == exp.experiment_id
    assert schedule.priority == priority
    assert sch_engine.get_schedule(schedule.schedule_id) is not None


def test_queue_priority_ordering(
    lfc_engine: ScientificExperimentLifecycleEngine,
    sch_engine: ExperimentSchedulingEngine,
):
    exp_low, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1111111111111111", title="Low Exp", priority=ExperimentPriority.LOW)
    exp_crit, _ = lfc_engine.create_experiment(hypothesis_id="HYP_2222222222222222", title="Crit Exp", priority=ExperimentPriority.CRITICAL)
    exp_high, _ = lfc_engine.create_experiment(hypothesis_id="HYP_3333333333333333", title="High Exp", priority=ExperimentPriority.HIGH)

    sch_engine.schedule_experiment(exp_low, scheduled_timestamp="2026-08-04T12:00:00Z")
    sch_engine.schedule_experiment(exp_crit, scheduled_timestamp="2026-08-04T12:05:00Z")
    sch_engine.schedule_experiment(exp_high, scheduled_timestamp="2026-08-04T12:02:00Z")

    queue = sch_engine.list_queue()
    assert len(queue) == 3
    # Queue order should be CRITICAL (pos 1), HIGH (pos 2), LOW (pos 3)
    assert queue[0].experiment_id == exp_crit.experiment_id
    assert queue[1].experiment_id == exp_high.experiment_id
    assert queue[2].experiment_id == exp_low.experiment_id
    assert queue[0].queue_position == 1
    assert queue[1].queue_position == 2
    assert queue[2].queue_position == 3


def test_schedule_experiment_idempotency(
    lfc_engine: ScientificExperimentLifecycleEngine,
    sch_engine: ExperimentSchedulingEngine,
):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="Idempotent Exp")

    s1 = sch_engine.schedule_experiment(exp)
    s2 = sch_engine.schedule_experiment(exp)

    assert s1.schedule_id == s2.schedule_id
    assert len(sch_engine.list_queue()) == 1
