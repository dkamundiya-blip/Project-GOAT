"""
Project GOAT v0.9 — Dedicated Unit Tests for Experiment Replay Engine
"""

import pytest

from goat.experiments.lifecycle.engine import ScientificExperimentLifecycleEngine
from goat.experiments.manifests.engine import ExperimentManifestEngine
from goat.experiments.replay.engine import ExperimentReplayEngine


@pytest.fixture
def lfc_engine():
    return ScientificExperimentLifecycleEngine()


@pytest.fixture
def man_engine():
    return ExperimentManifestEngine()


@pytest.fixture
def rpl_engine():
    return ExperimentReplayEngine()


@pytest.mark.parametrize("seed", [1, 42, 100, 999])
def test_create_replay_spec_success(
    lfc_engine: ScientificExperimentLifecycleEngine,
    man_engine: ExperimentManifestEngine,
    rpl_engine: ExperimentReplayEngine,
    seed: int,
):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="Replay Test Exp")
    man = man_engine.generate_manifest(exp, dataset_fingerprint="DS_FINGERPRINT_123")

    replay = rpl_engine.create_replay_spec(
        experiment=exp,
        manifest=man,
        dataset_hash="D1A2T3A4S5E6T789",
        random_seed=seed,
        expected_output_hash="EXPECTED_OUTPUT_HASH_123",
    )

    assert replay.replay_id.startswith("RPL_")
    assert replay.experiment_id == exp.experiment_id
    assert replay.manifest_id == man.manifest_id
    assert replay.random_seed == seed
    assert rpl_engine.get_replay(replay.replay_id) is not None


@pytest.mark.parametrize("invalid_hash", ["", "123", "   "])
def test_create_replay_invalid_dataset_hash(
    lfc_engine: ScientificExperimentLifecycleEngine,
    man_engine: ExperimentManifestEngine,
    rpl_engine: ExperimentReplayEngine,
    invalid_hash: str,
):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="Invalid Hash Exp")
    man = man_engine.generate_manifest(exp)

    with pytest.raises(ValueError):
        rpl_engine.create_replay_spec(
            experiment=exp,
            manifest=man,
            dataset_hash=invalid_hash,
        )


def test_verify_replay_integrity(
    lfc_engine: ScientificExperimentLifecycleEngine,
    man_engine: ExperimentManifestEngine,
    rpl_engine: ExperimentReplayEngine,
):
    exp, _ = lfc_engine.create_experiment(hypothesis_id="HYP_1234567890ABCDEF", title="Integrity Exp")
    man = man_engine.generate_manifest(exp)

    replay = rpl_engine.create_replay_spec(
        experiment=exp,
        manifest=man,
        dataset_hash="D1A2T3A4S5E6T789",
        expected_output_hash="OUTPUT_HASH_999",
    )

    assert rpl_engine.verify_replay_integrity(replay.replay_id, "OUTPUT_HASH_999") is True
    assert rpl_engine.verify_replay_integrity(replay.replay_id, "MISMATCH_HASH") is False
