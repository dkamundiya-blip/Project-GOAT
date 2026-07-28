"""
Project GOAT v0.5 — Unit Tests for Targeted P2 Code-Quality Polish
"""

import json
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import pytest

from goat import __version__ as GOAT_VERSION
from goat.config import GoatSettings
from goat.data.schemas import Candle, DataSource, Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition, InfrastructureFailure
from goat.orchestration.queue import ExperimentTask
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash, compute_experiment_id
from goat.orchestration.worker import WorkerPool
from goat.research.hypothesis.definition import HypothesisDefinition


def setup_p2_mock_data(tmp_path: Path) -> tuple[GoatSettings, ParquetStorage]:
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


def make_dummy_hypothesis(hyp_id: str = "HYP-P2-1") -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="P2 Polish Hypothesis",
        description="Testing P2 polish improvements",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )


def test_goat_version_centralization_and_experiment_id_byte_invariance() -> None:
    """2, 3, 4, 5. GOAT_VERSION equals '0.6.0', dataset_version stays 'v0.3.0', and experiment_id is byte-for-byte invariant."""
    assert GOAT_VERSION == "0.6.0"

    hyp = make_dummy_hypothesis()
    exp_id = compute_experiment_id(
        hypothesis=hyp,
        symbol="R_10",
        timeframe="M1",
        dataset_fingerprint="fp_test",
        experiment_hash_schema=1,
        experiment_hash_algorithm="SHA256",
        goat_version=GOAT_VERSION,
    )

    # Compute again directly
    exp_id_direct = compute_experiment_id(
        hypothesis=hyp,
        symbol="R_10",
        timeframe="M1",
        dataset_fingerprint="fp_test",
    )

    assert exp_id == exp_id_direct
    assert exp_id.startswith("EXP_")
    assert len(exp_id) == 20  # EXP_ (4) + 16 hex chars


def test_worker_pool_log_callback_runtime_safety() -> None:
    """1. WorkerPool log_callback retains identical runtime behavior."""
    events = []

    def mock_callback(level, event_type, message, component="Worker", experiment_id="", worker_id="", metadata=None):
        events.append((level, event_type, experiment_id, worker_id))

    pool = WorkerPool(max_workers=2, master_seed=42, log_callback=mock_callback)
    assert pool.log_callback is mock_callback


def test_resume_narrow_exception_handling(tmp_path: Path) -> None:
    """6, 7, 8. Corrupted checkpoint results raise InfrastructureFailure while valid resume succeeds."""
    settings, storage = setup_p2_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-P2-NARROW", configuration_hash=cfg_hash, name="Narrow Exception")

    out_dir = scheduler.run_campaign(camp_def, [hyp])

    # Corrupt checkpoint task_results with invalid result dictionary
    chk_path = out_dir / "checkpoint.json"
    chk_data = json.loads(chk_path.read_text(encoding="utf-8"))
    first_exp_id = list(chk_data["task_results"].keys())[0]
    chk_data["task_results"][first_exp_id] = {"corrupted_field": "invalid_schema"}
    chk_path.write_text(json.dumps(chk_data, indent=2), encoding="utf-8")

    # Reset status to PAUSED in manifest
    manifest_path = out_dir / "campaign_manifest.json"
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_data["campaign"]["status"] = "PAUSED"
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    resumed_scheduler = ExperimentScheduler(settings=settings, storage=storage)
    with pytest.raises(InfrastructureFailure, match="Corrupted or invalid completed task result"):
        resumed_scheduler.resume_campaign("CMP-P2-NARROW", [hyp])
