"""
Project GOAT v0.9 — Comprehensive Dedicated Unit Tests for Experiment Domain Models
"""

import pytest
from pydantic import ValidationError

from goat.experiments.core.canonical import (
    compute_canonical_sha256,
    compute_experiment_id,
    compute_lifecycle_id,
    compute_manifest_id,
    compute_replay_id,
    compute_schedule_id,
    compute_summary_id,
    serialize_canonical_json,
)
from goat.experiments.core.enums import (
    ExperimentPriority,
    ExperimentStatus,
    ExperimentType,
)
from goat.experiments.core.models import (
    ExperimentLifecycle,
    ExperimentManifest,
    ExperimentReplay,
    ExperimentSchedule,
    ExperimentSummary,
    ScientificExperiment,
)


@pytest.mark.parametrize("status", list(ExperimentStatus))
@pytest.mark.parametrize("exp_type", list(ExperimentType))
@pytest.mark.parametrize("priority", list(ExperimentPriority))
def test_scientific_experiment_model_instantiation(
    status: ExperimentStatus,
    exp_type: ExperimentType,
    priority: ExperimentPriority,
):
    hyp_id = "HYP_1234567890ABCDEF"
    exp_id, canonical_hash = compute_experiment_id(
        hypothesis_id=hyp_id,
        title="Volatility Expansion Experiment",
        experiment_type=exp_type.value,
        author="QUANT_TEST",
    )

    exp = ScientificExperiment(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        title="Volatility Expansion Experiment",
        description="Testing volatility expansion hypothesis.",
        experiment_type=exp_type,
        status=status,
        priority=priority,
        author="QUANT_TEST",
        evidence_ids=["EVR_1234567890ABCDEF"],
        manifest_id="MAN_1234567890ABCDEF",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        tags=["volatility"],
        metadata={"key": "val"},
        canonical_hash=canonical_hash,
    )

    assert exp.experiment_id == exp_id
    assert exp.hypothesis_id == hyp_id
    assert exp.experiment_type == exp_type
    assert exp.status == status
    assert exp.priority == priority
    assert exp.canonical_hash == canonical_hash


@pytest.mark.parametrize("invalid_id", ["INVALID_ID", "EXP_SHORT", "123_EXP", "HYP_1234567890ABCDEF"])
def test_scientific_experiment_invalid_id_pattern(invalid_id: str):
    with pytest.raises(ValidationError):
        ScientificExperiment(
            experiment_id=invalid_id,
            hypothesis_id="HYP_1234567890ABCDEF",
            title="Invalid Experiment",
            created_timestamp="2026-08-04T12:00:00Z",
            updated_timestamp="2026-08-04T12:00:00Z",
        )


def test_scientific_experiment_immutability():
    exp_id, canonical_hash = compute_experiment_id(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Immutable Test",
        experiment_type="SIMULATION",
    )
    exp = ScientificExperiment(
        experiment_id=exp_id,
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Immutable Test",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    with pytest.raises(ValidationError):
        exp.title = "New Title"  # Frozen check


@pytest.mark.parametrize("idx", range(1, 10))
def test_experiment_manifest_model(idx: int):
    exp_id = f"EXP_{idx:016X}"
    hyp_id = f"HYP_{idx:016X}"
    man_id, man_hash = compute_manifest_id(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        evidence_ids=[f"EVR_{idx:016X}"],
    )

    manifest = ExperimentManifest(
        manifest_id=man_id,
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        evidence_ids=[f"EVR_{idx:016X}"],
        dataset_fingerprint="A1B2C3D4E5F67890",
        configuration_params={"param1": idx},
        software_version="1.0.0",
        author="QUANT_TEST",
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=man_hash,
    )

    assert manifest.manifest_id == man_id
    assert manifest.experiment_id == exp_id
    assert manifest.configuration_params["param1"] == idx


@pytest.mark.parametrize("from_st", list(ExperimentStatus))
@pytest.mark.parametrize("to_st", list(ExperimentStatus))
def test_experiment_lifecycle_model(from_st: ExperimentStatus, to_st: ExperimentStatus):
    exp_id = "EXP_1234567890ABCDEF"
    lfc_id, lfc_hash = compute_lifecycle_id(
        experiment_id=exp_id,
        from_status=from_st.value,
        to_status=to_st.value,
        timestamp="2026-08-04T12:00:00Z",
    )

    lfc = ExperimentLifecycle(
        lifecycle_id=lfc_id,
        experiment_id=exp_id,
        from_status=from_st,
        to_status=to_st,
        actor="TEST_ACTOR",
        reason="Lifecycle transition test.",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=lfc_hash,
    )

    assert lfc.lifecycle_id == lfc_id
    assert lfc.from_status == from_st
    assert lfc.to_status == to_st


@pytest.mark.parametrize("seed", [1, 42, 100, 9999])
def test_experiment_replay_model(seed: int):
    exp_id = "EXP_1234567890ABCDEF"
    man_id = "MAN_1234567890ABCDEF"
    rpl_id, rpl_hash = compute_replay_id(
        experiment_id=exp_id,
        manifest_id=man_id,
        dataset_hash="D1A2T3A4S5E6T789",
        timestamp="2026-08-04T12:00:00Z",
    )

    replay = ExperimentReplay(
        replay_id=rpl_id,
        experiment_id=exp_id,
        manifest_id=man_id,
        dataset_hash="D1A2T3A4S5E6T789",
        random_seed=seed,
        expected_output_hash="O1U2T3P4U5T67890",
        is_verified=True,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=rpl_hash,
    )

    assert replay.replay_id == rpl_id
    assert replay.random_seed == seed


@pytest.mark.parametrize("priority", list(ExperimentPriority))
def test_experiment_schedule_model(priority: ExperimentPriority):
    exp_id = "EXP_1234567890ABCDEF"
    sch_id, sch_hash = compute_schedule_id(
        experiment_id=exp_id,
        priority=priority.value,
        scheduled_timestamp="2026-08-04T12:00:00Z",
    )

    schedule = ExperimentSchedule(
        schedule_id=sch_id,
        experiment_id=exp_id,
        priority=priority,
        scheduled_timestamp="2026-08-04T12:00:00Z",
        queue_position=1,
        scheduler_id="TEST_SCHEDULER",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sch_hash,
    )

    assert schedule.schedule_id == sch_id
    assert schedule.priority == priority


@pytest.mark.parametrize("count", [0, 5, 25, 100])
def test_experiment_summary_model(count: int):
    sum_id, sum_hash = compute_summary_id(total_experiments=count, timestamp="2026-08-04T12:00:00Z")

    summary = ExperimentSummary(
        summary_id=sum_id,
        total_experiments=count,
        status_counts={"PLANNED": count},
        type_counts={"SIMULATION": count},
        priority_counts={"NORMAL": count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )

    assert summary.summary_id == sum_id
    assert summary.total_experiments == count
