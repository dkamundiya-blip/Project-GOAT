"""
Project GOAT v0.9 — Comprehensive Experiment Public API & Canonical Hash Integrity Tests
"""

import pytest

import goat.experiments as experiments
from goat.experiments import (
    ExperimentLifecycle,
    ExperimentManifest,
    ExperimentManifestEngine,
    ExperimentPersistenceContext,
    ExperimentPriority,
    ExperimentReplay,
    ExperimentReplayEngine,
    ExperimentRepository,
    ExperimentSchedule,
    ExperimentSchedulingEngine,
    ExperimentStatus,
    ExperimentSummary,
    ExperimentType,
    LifecycleRepository,
    ManifestRepository,
    ReplayRepository,
    ScheduleRepository,
    ScientificExperiment,
    ScientificExperimentEngine,
    ScientificExperimentLifecycleEngine,
    SummaryRepository,
    compute_canonical_sha256,
    compute_experiment_id,
    compute_lifecycle_id,
    compute_manifest_id,
    compute_replay_id,
    compute_schedule_id,
    compute_summary_id,
    generate_executive_summary,
    generate_experiment_report,
    generate_json_report,
    generate_lifecycle_report,
    generate_manifest_report,
    generate_replay_report,
    init_experiment_db,
    serialize_canonical_json,
)


def test_public_api_exports():
    expected_exports = [
        "ExperimentLifecycle",
        "ExperimentManifest",
        "ExperimentManifestEngine",
        "ExperimentPersistenceContext",
        "ExperimentPriority",
        "ExperimentReplay",
        "ExperimentReplayEngine",
        "ExperimentRepository",
        "ExperimentSchedule",
        "ExperimentSchedulingEngine",
        "ExperimentStatus",
        "ExperimentSummary",
        "ExperimentType",
        "LifecycleRepository",
        "ManifestRepository",
        "ReplayRepository",
        "ScheduleRepository",
        "ScientificExperiment",
        "ScientificExperimentEngine",
        "ScientificExperimentLifecycleEngine",
        "SummaryRepository",
        "compute_canonical_sha256",
        "compute_experiment_id",
        "compute_lifecycle_id",
        "compute_manifest_id",
        "compute_replay_id",
        "compute_schedule_id",
        "compute_summary_id",
        "generate_executive_summary",
        "generate_experiment_report",
        "generate_json_report",
        "generate_lifecycle_report",
        "generate_manifest_report",
        "generate_replay_report",
        "init_experiment_db",
        "serialize_canonical_json",
    ]

    for export_name in expected_exports:
        assert hasattr(experiments, export_name)
        assert export_name in experiments.__all__


@pytest.mark.parametrize("i", range(1, 1001))
def test_experiment_id_determinism_large(i: int):
    hyp_id = f"HYP_{i:016X}"
    title = f"Title #{i}"
    exp_type = "SIMULATION"
    author = "QUANT_AUTHOR"

    id1, hash1 = compute_experiment_id(hypothesis_id=hyp_id, title=title, experiment_type=exp_type, author=author)
    id2, hash2 = compute_experiment_id(hypothesis_id=hyp_id, title=title, experiment_type=exp_type, author=author)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EXP_")
    assert len(id1) == 20
    assert len(hash1) == 64


@pytest.mark.parametrize("m", range(1, 1001))
def test_manifest_id_determinism_large(m: int):
    exp_id = f"EXP_{m:016X}"
    hyp_id = f"HYP_{m:016X}"
    ev_ids = [f"EVR_{m:016X}"]

    id1, hash1 = compute_manifest_id(experiment_id=exp_id, hypothesis_id=hyp_id, evidence_ids=ev_ids)
    id2, hash2 = compute_manifest_id(experiment_id=exp_id, hypothesis_id=hyp_id, evidence_ids=ev_ids)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("MAN_")
    assert len(id1) == 20


@pytest.mark.parametrize("l", range(1, 1001))
def test_lifecycle_id_determinism_large(l: int):
    exp_id = f"EXP_{l:016X}"
    ts = f"2026-08-04T12:{l % 60:02d}:00Z"

    id1, hash1 = compute_lifecycle_id(experiment_id=exp_id, from_status="PLANNED", to_status="RUNNING", timestamp=ts)
    id2, hash2 = compute_lifecycle_id(experiment_id=exp_id, from_status="PLANNED", to_status="RUNNING", timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("LFC_")
    assert len(id1) == 20


@pytest.mark.parametrize("r", range(1, 1001))
def test_replay_id_determinism_large(r: int):
    exp_id = f"EXP_{r:016X}"
    man_id = f"MAN_{r:016X}"
    ts = f"2026-08-04T12:{r % 60:02d}:00Z"

    id1, hash1 = compute_replay_id(experiment_id=exp_id, manifest_id=man_id, dataset_hash="D1A2T3A4", timestamp=ts)
    id2, hash2 = compute_replay_id(experiment_id=exp_id, manifest_id=man_id, dataset_hash="D1A2T3A4", timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RPL_")
    assert len(id1) == 20


@pytest.mark.parametrize("s", range(1, 1001))
def test_schedule_id_determinism_large(s: int):
    exp_id = f"EXP_{s:016X}"
    ts = f"2026-08-04T12:{s % 60:02d}:00Z"

    id1, hash1 = compute_schedule_id(experiment_id=exp_id, priority="HIGH", scheduled_timestamp=ts)
    id2, hash2 = compute_schedule_id(experiment_id=exp_id, priority="HIGH", scheduled_timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SCH_")
    assert len(id1) == 20


@pytest.mark.parametrize("u", range(1, 1001))
def test_summary_id_determinism_large(u: int):
    ts = f"2026-08-04T12:{u % 60:02d}:00Z"

    id1, hash1 = compute_summary_id(total_experiments=u, timestamp=ts)
    id2, hash2 = compute_summary_id(total_experiments=u, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SUM_")
    assert len(id1) == 20
