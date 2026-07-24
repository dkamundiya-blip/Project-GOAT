"""
Project GOAT v0.5 — Unit Tests for Manifest & Statistics Construction Deduplication (P1-02)
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from goat.config import GoatSettings
from goat.data.schemas import Candle, DataSource, Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash
from goat.research.hypothesis.definition import HypothesisDefinition


def setup_dedup_mock_data(tmp_path: Path) -> tuple[GoatSettings, ParquetStorage]:
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


def make_dummy_hypothesis(hyp_id: str = "HYP-DEDUP-1") -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="Dedup Test Hypothesis",
        description="Testing manifest construction deduplication",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )


def test_run_and_resume_manifest_structures_identical(tmp_path: Path) -> None:
    """1-5. Verify run_campaign and resume_campaign construct identical 6-section manifest schemas & statistics."""
    settings, storage = setup_dedup_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-DEDUP-01", configuration_hash=cfg_hash, name="Dedup Test")

    # 1. Run campaign
    out_dir = scheduler.run_campaign(camp_def, [hyp])
    m_run = json.loads((out_dir / "campaign_manifest.json").read_text(encoding="utf-8"))
    s_run = json.loads((out_dir / "campaign_statistics.json").read_text(encoding="utf-8"))

    # Verify 6 mandatory manifest sections exist
    required_sections = {"manifest_schema_version", "provenance_schema_version", "campaign", "configuration", "environment", "research_provenance", "execution_configuration", "validation", "lifecycle_history"}
    assert set(m_run.keys()) == required_sections

    # 2. Pause and resume campaign
    m_run["campaign"]["status"] = "PAUSED"
    (out_dir / "campaign_manifest.json").write_text(json.dumps(m_run, indent=2), encoding="utf-8")

    resumed_scheduler = ExperimentScheduler(settings=settings, storage=storage)
    resumed_dir = resumed_scheduler.resume_campaign("CMP-DEDUP-01", [hyp])

    m_res = json.loads((resumed_dir / "campaign_manifest.json").read_text(encoding="utf-8"))
    s_res = json.loads((resumed_dir / "campaign_statistics.json").read_text(encoding="utf-8"))

    # Verify key structural equivalence
    assert set(m_res.keys()) == set(m_run.keys())
    assert m_res["configuration"] == m_run["configuration"]
    assert m_res["execution_configuration"] == m_run["execution_configuration"]
    assert m_res["validation"] == m_run["validation"]

    # Lockfile hash in environment section must be valid 64-char SHA256 hex digest
    lock_hash = m_res["environment"]["dependency_lockfile_hash"]
    assert len(lock_hash) == 64
    assert lock_hash == m_run["environment"]["dependency_lockfile_hash"]

    # Statistics key structure
    assert s_res["total_experiments"] == s_run["total_experiments"] == 1
    assert s_res["completed_count"] == s_run["completed_count"] == 1
    assert s_res["failed_count"] == s_run["failed_count"] == 0
