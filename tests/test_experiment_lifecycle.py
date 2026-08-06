"""
Project GOAT v0.9 — Dedicated Unit Tests for Scientific Experiment Lifecycle Engine
"""

import pytest

from goat.experiments.core.enums import ExperimentPriority, ExperimentStatus, ExperimentType
from goat.experiments.lifecycle.engine import ScientificExperimentLifecycleEngine


@pytest.fixture
def lfc_engine():
    return ScientificExperimentLifecycleEngine()


def test_create_experiment_success(lfc_engine: ScientificExperimentLifecycleEngine):
    exp, lfc = lfc_engine.create_experiment(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Volatility Expansion Study",
        description="Testing volatility expansion hypothesis.",
        experiment_type=ExperimentType.SIMULATION,
        priority=ExperimentPriority.HIGH,
        author="QUANT_AUTHOR",
    )

    assert exp.experiment_id.startswith("EXP_")
    assert exp.hypothesis_id == "HYP_1234567890ABCDEF"
    assert exp.status == ExperimentStatus.PLANNED
    assert lfc.from_status == ExperimentStatus.PLANNED
    assert lfc.to_status == ExperimentStatus.PLANNED


@pytest.mark.parametrize("invalid_hyp", ["", "INVALID", "EXP_1234567890ABCDEF"])
def test_create_experiment_invalid_hypothesis_prefix(lfc_engine: ScientificExperimentLifecycleEngine, invalid_hyp: str):
    with pytest.raises(ValueError):
        lfc_engine.create_experiment(
            hypothesis_id=invalid_hyp,
            title="Valid Title",
        )


def test_legal_lifecycle_transitions(lfc_engine: ScientificExperimentLifecycleEngine):
    exp, _ = lfc_engine.create_experiment(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Lifecycle Journey Test",
    )

    exp_id = exp.experiment_id

    # PLANNED -> APPROVED
    exp_app, lfc1 = lfc_engine.approve_experiment(exp_id, actor="CSO", reason="Approved for research.")
    assert exp_app.status == ExperimentStatus.APPROVED

    # APPROVED -> RUNNING
    exp_run, lfc2 = lfc_engine.start_experiment(exp_id, actor="ENGINE", reason="Execution started.")
    assert exp_run.status == ExperimentStatus.RUNNING

    # RUNNING -> PAUSED
    exp_pause, lfc3 = lfc_engine.pause_experiment(exp_id, actor="OPERATOR", reason="Pausing for maintenance.")
    assert exp_pause.status == ExperimentStatus.PAUSED

    # PAUSED -> RUNNING
    exp_res, lfc4 = lfc_engine.resume_experiment(exp_id, actor="OPERATOR", reason="Resuming execution.")
    assert exp_res.status == ExperimentStatus.RUNNING

    # RUNNING -> COMPLETED
    exp_comp, lfc5 = lfc_engine.complete_experiment(exp_id, actor="ENGINE", reason="Completed successfully.")
    assert exp_comp.status == ExperimentStatus.COMPLETED

    # COMPLETED -> ARCHIVED
    exp_arch, lfc6 = lfc_engine.archive_experiment(exp_id, actor="ARCHIVER", reason="Archiving completed run.")
    assert exp_arch.status == ExperimentStatus.ARCHIVED

    history = lfc_engine.get_lifecycle_history(exp_id)
    assert len(history) == 7  # Initial + 6 transitions


@pytest.mark.parametrize(
    "illegal_target",
    [
        ExperimentStatus.COMPLETED,
        ExperimentStatus.PAUSED,
        ExperimentStatus.READY,
    ],
)
def test_reject_illegal_state_transitions_from_planned(lfc_engine: ScientificExperimentLifecycleEngine, illegal_target: ExperimentStatus):
    exp, _ = lfc_engine.create_experiment(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Illegal Transition Test",
    )

    with pytest.raises(ValueError):
        lfc_engine.transition_status(exp.experiment_id, illegal_target, actor="TEST_ACTOR")


def test_reject_transitions_from_archived(lfc_engine: ScientificExperimentLifecycleEngine):
    exp, _ = lfc_engine.create_experiment(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Archived Transition Test",
    )
    lfc_engine.archive_experiment(exp.experiment_id, actor="TEST_ACTOR")

    with pytest.raises(ValueError):
        lfc_engine.start_experiment(exp.experiment_id, actor="TEST_ACTOR")
