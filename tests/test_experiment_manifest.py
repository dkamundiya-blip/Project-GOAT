"""
Project GOAT v0.9 — Dedicated Unit Tests for Experiment Manifest Engine
"""

import pytest

from goat.experiments.lifecycle.engine import ScientificExperimentLifecycleEngine
from goat.experiments.manifests.engine import ExperimentManifestEngine


@pytest.fixture
def lfc_engine():
    return ScientificExperimentLifecycleEngine()


@pytest.fixture
def man_engine():
    return ExperimentManifestEngine()


@pytest.mark.parametrize("idx", range(1, 10))
def test_generate_manifest_success(
    lfc_engine: ScientificExperimentLifecycleEngine,
    man_engine: ExperimentManifestEngine,
    idx: int,
):
    exp, _ = lfc_engine.create_experiment(
        hypothesis_id=f"HYP_{idx:016X}",
        title=f"Experiment #{idx}",
        evidence_ids=[f"EVR_{idx:016X}"],
    )

    manifest = man_engine.generate_manifest(
        experiment=exp,
        dataset_fingerprint=f"FINGERPRINT_{idx}",
        configuration_params={"window_length": idx * 10, "threshold": 0.5},
        software_version="1.0.0",
    )

    assert manifest.manifest_id.startswith("MAN_")
    assert manifest.experiment_id == exp.experiment_id
    assert manifest.hypothesis_id == exp.hypothesis_id
    assert manifest.dataset_fingerprint == f"FINGERPRINT_{idx}"
    assert manifest.configuration_params["window_length"] == idx * 10
    assert man_engine.get_manifest(manifest.manifest_id) is not None
    assert man_engine.get_manifest_for_experiment(exp.experiment_id) is not None


def test_generate_manifest_idempotency(
    lfc_engine: ScientificExperimentLifecycleEngine,
    man_engine: ExperimentManifestEngine,
):
    exp, _ = lfc_engine.create_experiment(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Manifest Idempotency Test",
        evidence_ids=["EVR_1234567890ABCDEF"],
    )

    m1 = man_engine.generate_manifest(exp, dataset_fingerprint="FP123")
    m2 = man_engine.generate_manifest(exp, dataset_fingerprint="FP123")

    assert m1.manifest_id == m2.manifest_id
    assert len(man_engine.list_all_manifests()) == 1
