"""
Project GOAT v0.5 — Unit Tests for Dependency Lockfile Provenance Hashing
"""

import hashlib
import json
from pathlib import Path
import pandas as pd
import pytest

from goat.config import GoatSettings
from goat.data.schemas import Candle, DataSource, Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition, InfrastructureFailure
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash, compute_dependency_lockfile_hash
from goat.research.hypothesis.definition import HypothesisDefinition


def setup_provenance_mock_data(tmp_path: Path) -> tuple[GoatSettings, ParquetStorage]:
    settings = GoatSettings(
        data_dir=tmp_path / "data",
        raw_data_dir=tmp_path / "data" / "raw",
        processed_data_dir=tmp_path / "data" / "processed",
        research_data_dir=tmp_path / "data" / "research",
        campaign_data_dir=tmp_path / "data" / "campaigns",
    )
    storage = ParquetStorage(settings.get_raw_data_dir(), settings.get_processed_data_dir())

    dates = pd.date_range("2024-07-22", periods=60, freq="1min", tz="UTC")
    prices = [100.0 + (i * 0.1) for i in range(60)]
    candles = [
        Candle(
            symbol="R_10",
            timeframe=Timeframe.M1,
            timestamp=d.to_pydatetime(),
            open=p,
            high=p + 0.05,
            low=p - 0.05,
            close=p,
            source=DataSource.HISTORICAL_IMPORT,
        )
        for d, p in zip(dates, prices)
    ]
    storage.write_candles("R_10", Timeframe.M1, candles)
    return settings, storage


def make_dummy_hypothesis(hyp_id: str = "HYP-PROV-1") -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="Provenance Test Hypothesis",
        description="Testing lockfile provenance hash",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )


def test_dependency_lockfile_hash_known_bytes(tmp_path: Path) -> None:
    """1. Known dependency bytes produce the expected lowercase 64-char SHA256 digest."""
    spec_file = tmp_path / "pyproject.toml"
    content = b"[project]\nname = 'test-goat'\nversion = '0.1.0'\n"
    spec_file.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    computed_hash = compute_dependency_lockfile_hash(tmp_path)

    assert len(computed_hash) == 64
    assert computed_hash == computed_hash.lower()
    assert computed_hash == expected_hash


def test_dependency_lockfile_hash_determinism_and_mutation(tmp_path: Path) -> None:
    """2-3. Identical bytes produce identical hashes; modified bytes produce a different hash."""
    dir1 = tmp_path / "d1"
    dir2 = tmp_path / "d2"
    dir1.mkdir()
    dir2.mkdir()

    content1 = b"dependencies = ['pandas>=2.0']"
    content2 = b"dependencies = ['pandas>=2.2']"

    (dir1 / "pyproject.toml").write_bytes(content1)
    (dir2 / "pyproject.toml").write_bytes(content1)

    hash1_a = compute_dependency_lockfile_hash(dir1)
    hash1_b = compute_dependency_lockfile_hash(dir2)
    assert hash1_a == hash1_b

    (dir2 / "pyproject.toml").write_bytes(content2)
    hash2 = compute_dependency_lockfile_hash(dir2)
    assert hash1_a != hash2


def test_manifest_contains_real_computed_digest_and_no_placeholder(tmp_path: Path) -> None:
    """4, 5, 6. Campaign manifest contains real computed digest; placeholder string is absent."""
    settings, storage = setup_provenance_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-PROV-REAL", configuration_hash=cfg_hash, name="Prov Test")

    # Run campaign
    out_dir = scheduler.run_campaign(camp_def, [hyp])
    manifest_data = json.loads((out_dir / "campaign_manifest.json").read_text(encoding="utf-8"))

    env_section = manifest_data.get("environment", {})
    lock_hash = env_section.get("dependency_lockfile_hash")

    assert lock_hash is not None
    assert len(lock_hash) == 64
    assert lock_hash != "sha256_lockfile_hash_v0.5"

    # Verify resume uses same implementation
    manifest_data["campaign"]["status"] = "PAUSED"
    (out_dir / "campaign_manifest.json").write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    resumed_scheduler = ExperimentScheduler(settings=settings, storage=storage)
    resumed_dir = resumed_scheduler.resume_campaign("CMP-PROV-REAL", [hyp])

    resumed_manifest = json.loads((resumed_dir / "campaign_manifest.json").read_text(encoding="utf-8"))
    resumed_lock_hash = resumed_manifest["environment"]["dependency_lockfile_hash"]

    assert resumed_lock_hash == lock_hash


def test_missing_dependency_file_raises_infrastructure_failure(tmp_path: Path) -> None:
    """Failure semantics: If dependency file is missing in an isolated directory, InfrastructureFailure is raised."""
    empty_dir = tmp_path / "empty_root"
    empty_dir.mkdir()

    with pytest.raises(InfrastructureFailure, match="Authoritative dependency specification file not found"):
        compute_dependency_lockfile_hash(empty_dir, allow_cwd_fallback=False)
