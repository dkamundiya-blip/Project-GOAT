"""
Project GOAT v0.9 — Dedicated Unit Tests for Experiment Reporting Generators
"""

import json
import pytest

from goat.experiments.core.canonical import compute_summary_id
from goat.experiments.core.enums import ExperimentPriority, ExperimentStatus, ExperimentType
from goat.experiments.core.models import ExperimentSummary
from goat.experiments.lifecycle.engine import ScientificExperimentLifecycleEngine
from goat.experiments.manifests.engine import ExperimentManifestEngine
from goat.experiments.replay.engine import ExperimentReplayEngine
from goat.experiments.reporting.reports import (
    generate_executive_summary,
    generate_experiment_report,
    generate_json_report,
    generate_lifecycle_report,
    generate_manifest_report,
    generate_replay_report,
)


@pytest.fixture
def lfc_engine():
    return ScientificExperimentLifecycleEngine()


@pytest.fixture
def man_engine():
    return ExperimentManifestEngine()


@pytest.fixture
def rpl_engine():
    return ExperimentReplayEngine()


def test_generate_experiment_report(lfc_engine: ScientificExperimentLifecycleEngine):
    exp, _ = lfc_engine.create_experiment(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Report Test Experiment",
        description="Testing report generation.",
        evidence_ids=["EVR_1234567890ABCDEF"],
    )
    report = generate_experiment_report(exp)

    assert "# SCIENTIFIC EXPERIMENT REPORT" in report
    assert exp.title in report
    assert exp.experiment_id in report
    assert "EVR_1234567890ABCDEF" in report


def test_generate_lifecycle_report(lfc_engine: ScientificExperimentLifecycleEngine):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="LFC Report Exp")
    lfc_engine.approve_experiment(exp.experiment_id, actor="CSO", reason="Approved")
    lfc_engine.start_experiment(exp.experiment_id, actor="ENGINE", reason="Started")

    history = lfc_engine.get_lifecycle_history(exp.experiment_id)
    report = generate_lifecycle_report(exp.experiment_id, history)

    assert "# EXPERIMENT LIFECYCLE AUDIT REPORT" in report
    assert exp.experiment_id in report
    assert "PLANNED" in report
    assert "APPROVED" in report
    assert "RUNNING" in report


def test_generate_manifest_report(
    lfc_engine: ScientificExperimentLifecycleEngine,
    man_engine: ExperimentManifestEngine,
):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="Man Report Exp")
    man = man_engine.generate_manifest(
        exp,
        dataset_fingerprint="DS_FP_999",
        configuration_params={"param_a": 100},
    )
    report = generate_manifest_report(man)

    assert "# EXPERIMENT MANIFEST REPORT" in report
    assert man.manifest_id in report
    assert "DS_FP_999" in report
    assert "param_a" in report


def test_generate_replay_report(
    lfc_engine: ScientificExperimentLifecycleEngine,
    man_engine: ExperimentManifestEngine,
    rpl_engine: ExperimentReplayEngine,
):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="RPL Report Exp")
    man = man_engine.generate_manifest(exp)
    rpl = rpl_engine.create_replay_spec(exp, man, dataset_hash="DS_HASH_555", random_seed=42)

    report = generate_replay_report(rpl)
    assert "# EXPERIMENT REPLAY AUDIT REPORT" in report
    assert rpl.replay_id in report
    assert "DS_HASH_555" in report
    assert "PASSED (VERIFIED)" in report


def test_generate_json_report(lfc_engine: ScientificExperimentLifecycleEngine):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="JSON Report Exp")
    json_str = generate_json_report(exp)
    data = json.loads(json_str)

    assert data["experiment_id"] == exp.experiment_id
    assert data["title"] == "JSON Report Exp"


@pytest.mark.parametrize("exp_count", range(1, 10))
def test_generate_executive_summary(lfc_engine: ScientificExperimentLifecycleEngine, exp_count: int):
    experiments = []
    for i in range(exp_count):
        exp, _ = lfc_engine.create_experiment(hypothesis_id=f"HYP_{i:016X}", title=f"Exec Exp #{i}")
        experiments.append(exp)

    sum_id, sum_hash = compute_summary_id(total_experiments=exp_count, timestamp="2026-08-04T12:00:00Z")
    summary = ExperimentSummary(
        summary_id=sum_id,
        total_experiments=exp_count,
        status_counts={"PLANNED": exp_count},
        type_counts={"SIMULATION": exp_count},
        priority_counts={"NORMAL": exp_count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )

    report = generate_executive_summary(summary, experiments)
    assert "# PROJECT GOAT — EXPERIMENT SUBSYSTEM EXECUTIVE REPORT" in report
    assert f"Total Experiments**: `{exp_count}`" in report
    assert f"Exec Exp #{exp_count - 1}" in report
