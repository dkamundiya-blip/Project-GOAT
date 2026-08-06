"""
Project GOAT v0.9 — Dedicated Unit Tests for Scientific Experiment Engine Facade
"""

import pytest

from goat.experiments.core.enums import ExperimentPriority, ExperimentStatus, ExperimentType
from goat.experiments.engine import ScientificExperimentEngine
from goat.experiments.persistence.sqlite import ExperimentPersistenceContext


@pytest.fixture
def memory_context():
    ctx = ExperimentPersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.fixture
def exp_engine(memory_context):
    return ScientificExperimentEngine(persistence_context=memory_context)


@pytest.mark.parametrize("idx", range(1, 10))
def test_engine_create_and_transition(exp_engine: ScientificExperimentEngine, idx: int):
    exp, lfc1 = exp_engine.create_experiment(
        hypothesis_id=f"HYP_{idx:016X}",
        title=f"Facade Exp #{idx}",
        experiment_type=ExperimentType.SIMULATION,
        priority=ExperimentPriority.HIGH,
    )

    assert exp.experiment_id.startswith("EXP_")
    assert exp.status == ExperimentStatus.PLANNED
    assert exp_engine.persistence is not None

    fetched_exp = exp_engine.persistence.experiments.get_by_id(exp.experiment_id)
    assert fetched_exp is not None
    assert fetched_exp.title == f"Facade Exp #{idx}"

    exp_app, lfc2 = exp_engine.transition_status(
        experiment_id=exp.experiment_id,
        target_status=ExperimentStatus.APPROVED,
        actor="CSO",
        reason="Approved for facade test.",
    )

    assert exp_app.status == ExperimentStatus.APPROVED
    fetched_lfc = exp_engine.persistence.lifecycles.get_by_experiment_id(exp.experiment_id)
    assert len(fetched_lfc) == 2


@pytest.mark.parametrize("idx", range(1, 10))
def test_engine_manifest_schedule_replay(exp_engine: ScientificExperimentEngine, idx: int):
    exp, _ = exp_engine.create_experiment(
        hypothesis_id=f"HYP_{idx:016X}",
        title=f"Full Facade Flow #{idx}",
        evidence_ids=[f"EVR_{idx:016X}"],
    )

    man = exp_engine.generate_manifest(
        experiment=exp,
        dataset_fingerprint=f"FP_{idx}",
        configuration_params={"param": idx},
    )
    sch = exp_engine.schedule_experiment(exp)
    rpl = exp_engine.create_replay_spec(
        experiment=exp,
        manifest=man,
        dataset_hash=f"DS_HASH_{idx}",
        random_seed=42 + idx,
    )

    assert man.manifest_id.startswith("MAN_")
    assert sch.schedule_id.startswith("SCH_")
    assert rpl.replay_id.startswith("RPL_")

    fetched_man = exp_engine.persistence.manifests.get_by_id(man.manifest_id)
    assert fetched_man is not None
    fetched_sch = exp_engine.persistence.schedules.get_by_experiment_id(exp.experiment_id)
    assert fetched_sch is not None
    fetched_rpl = exp_engine.persistence.replays.get_by_id(rpl.replay_id)
    assert fetched_rpl is not None


def test_engine_report_generation(exp_engine: ScientificExperimentEngine):
    exp, _ = exp_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="Facade Report Exp")
    man = exp_engine.generate_manifest(exp, dataset_fingerprint="DS_123")
    exp_engine.create_replay_spec(exp, man, dataset_hash="HASH_123")

    reports = exp_engine.generate_reports(exp.experiment_id)
    assert "experiment" in reports
    assert "lifecycle" in reports
    assert "executive" in reports
    assert "json" in reports
    assert "manifest" in reports
    assert "replay" in reports
    assert exp.title in reports["experiment"]
