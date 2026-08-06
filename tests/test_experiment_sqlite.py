"""
Project GOAT v0.9 — Dedicated Unit Tests for Experiment SQLite Persistence
"""

import pytest

from goat.experiments.core.canonical import (
    compute_experiment_id,
    compute_lifecycle_id,
    compute_manifest_id,
    compute_replay_id,
    compute_schedule_id,
    compute_summary_id,
)
from goat.experiments.core.enums import ExperimentPriority, ExperimentStatus, ExperimentType
from goat.experiments.core.models import (
    ExperimentLifecycle,
    ExperimentManifest,
    ExperimentReplay,
    ExperimentSchedule,
    ExperimentSummary,
    ScientificExperiment,
)
from goat.experiments.persistence.sqlite import ExperimentPersistenceContext


@pytest.fixture
def persistence_ctx():
    ctx = ExperimentPersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.mark.parametrize("idx", range(1, 15))
def test_experiment_repository_roundtrip(persistence_ctx: ExperimentPersistenceContext, idx: int):
    hyp_id = f"HYP_{idx:016X}"
    exp_id, canonical_hash = compute_experiment_id(
        hypothesis_id=hyp_id,
        title=f"SQLite Experiment #{idx}",
        experiment_type="SIMULATION",
    )

    exp = ScientificExperiment(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        title=f"SQLite Experiment #{idx}",
        description="SQLite roundtrip description",
        experiment_type=ExperimentType.SIMULATION,
        status=ExperimentStatus.PLANNED,
        priority=ExperimentPriority.NORMAL,
        author="QUANT_TEST",
        evidence_ids=[f"EVR_{idx:016X}"],
        manifest_id=f"MAN_{idx:016X}",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        tags=[f"tag_{idx}"],
        metadata={"idx": idx},
        canonical_hash=canonical_hash,
    )

    persistence_ctx.experiments.save(exp)
    fetched = persistence_ctx.experiments.get_by_id(exp_id)

    assert fetched is not None
    assert fetched.experiment_id == exp.experiment_id
    assert fetched.title == exp.title
    assert fetched.evidence_ids == exp.evidence_ids
    assert fetched.canonical_hash == exp.canonical_hash


@pytest.mark.parametrize("idx", range(1, 10))
def test_manifest_repository_roundtrip(persistence_ctx: ExperimentPersistenceContext, idx: int):
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
        dataset_fingerprint="DS_FP_999",
        configuration_params={"param_x": idx},
        software_version="1.0.0",
        author="AUTHOR",
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=man_hash,
    )

    persistence_ctx.manifests.save(manifest)
    fetched = persistence_ctx.manifests.get_by_id(man_id)

    assert fetched is not None
    assert fetched.manifest_id == man_id
    assert fetched.configuration_params["param_x"] == idx


@pytest.mark.parametrize("idx", range(1, 10))
def test_lifecycle_repository_roundtrip(persistence_ctx: ExperimentPersistenceContext, idx: int):
    exp_id = f"EXP_{idx:016X}"
    lfc_id, lfc_hash = compute_lifecycle_id(
        experiment_id=exp_id,
        from_status="PLANNED",
        to_status="RUNNING",
        timestamp="2026-08-04T12:00:00Z",
    )

    lifecycle = ExperimentLifecycle(
        lifecycle_id=lfc_id,
        experiment_id=exp_id,
        from_status=ExperimentStatus.PLANNED,
        to_status=ExperimentStatus.RUNNING,
        actor="ACTOR",
        reason="Reason",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=lfc_hash,
    )

    persistence_ctx.lifecycles.save(lifecycle)
    history = persistence_ctx.lifecycles.get_by_experiment_id(exp_id)

    assert len(history) == 1
    assert history[0].lifecycle_id == lfc_id
    assert history[0].to_status == ExperimentStatus.RUNNING


@pytest.mark.parametrize("idx", range(1, 10))
def test_replay_repository_roundtrip(persistence_ctx: ExperimentPersistenceContext, idx: int):
    exp_id = f"EXP_{idx:016X}"
    man_id = f"MAN_{idx:016X}"
    rpl_id, rpl_hash = compute_replay_id(
        experiment_id=exp_id,
        manifest_id=man_id,
        dataset_hash="HASH123",
        timestamp="2026-08-04T12:00:00Z",
    )

    replay = ExperimentReplay(
        replay_id=rpl_id,
        experiment_id=exp_id,
        manifest_id=man_id,
        dataset_hash="HASH123",
        random_seed=42,
        expected_output_hash="OUT123",
        is_verified=True,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=rpl_hash,
    )

    persistence_ctx.replays.save(replay)
    fetched = persistence_ctx.replays.get_by_id(rpl_id)

    assert fetched is not None
    assert fetched.replay_id == rpl_id
    assert fetched.dataset_hash == "HASH123"


@pytest.mark.parametrize("idx", range(1, 10))
def test_schedule_repository_roundtrip(persistence_ctx: ExperimentPersistenceContext, idx: int):
    exp_id = f"EXP_{idx:016X}"
    sch_id, sch_hash = compute_schedule_id(
        experiment_id=exp_id,
        priority="NORMAL",
        scheduled_timestamp="2026-08-04T12:00:00Z",
    )

    schedule = ExperimentSchedule(
        schedule_id=sch_id,
        experiment_id=exp_id,
        priority=ExperimentPriority.NORMAL,
        scheduled_timestamp="2026-08-04T12:00:00Z",
        queue_position=idx,
        scheduler_id="SCHEDULER",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sch_hash,
    )

    persistence_ctx.schedules.save(schedule)
    fetched = persistence_ctx.schedules.get_by_experiment_id(exp_id)

    assert fetched is not None
    assert fetched.schedule_id == sch_id
    assert fetched.queue_position == idx
