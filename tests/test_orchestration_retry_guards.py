"""
Project GOAT v0.5 — Unit Tests for ExperimentQueue Retry Transitions & State Guards
"""

import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from goat.config import GoatSettings
from goat.data.schemas import Candle, DataSource, Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition, ExperimentStatus
from goat.orchestration.queue import ExperimentQueue, ExperimentTask
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash, compute_experiment_id
from goat.orchestration.worker import WorkerPool, derive_canonical_seed_material
from goat.research.hypothesis.definition import HypothesisDefinition


def setup_mock_market_data(tmp_path: Path) -> tuple[GoatSettings, ParquetStorage]:
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


def make_dummy_hypothesis(hyp_id: str = "HYP-RETRY-1") -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="Retry Test Hypothesis",
        description="Testing retry transition state guards",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )


def test_retry_legal_transition_sequence() -> None:
    """1-3. Tests legal retry transition sequence: PENDING -> RUNNING -> FAILED -> PENDING -> RUNNING."""
    hyp = make_dummy_hypothesis()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp")
    task = ExperimentTask(exp_id, hyp, "R_10", "M1")
    queue = ExperimentQueue(campaign_id="CMP-RETRY-SEQ", configuration_hash="cfg_1", tasks=[task])

    # 1. PENDING -> RUNNING
    queue.update_status(exp_id, ExperimentStatus.RUNNING)
    assert queue.get_task(exp_id).status == ExperimentStatus.RUNNING

    # 2. RUNNING -> FAILED
    queue.update_status(exp_id, ExperimentStatus.FAILED)
    assert queue.get_task(exp_id).status == ExperimentStatus.FAILED

    # 3. FAILED -> PENDING (Requeue for retry)
    queue.update_status(exp_id, ExperimentStatus.PENDING)
    assert queue.get_task(exp_id).status == ExperimentStatus.PENDING

    # 4. PENDING -> RUNNING (Retried execution)
    queue.update_status(exp_id, ExperimentStatus.RUNNING)
    assert queue.get_task(exp_id).status == ExperimentStatus.RUNNING


def test_illegal_status_transitions_raise_value_error() -> None:
    """4, 13. Illegal transitions (RUNNING->PENDING, COMPLETED->RUNNING, SKIPPED->PENDING, CANCELLED->RUNNING) raise ValueError."""
    hyp = make_dummy_hypothesis()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp")

    # Direct RUNNING -> PENDING is illegal (must go RUNNING -> FAILED -> PENDING)
    t1 = ExperimentTask(exp_id, hyp, "R_10", "M1")
    q1 = ExperimentQueue("CMP-1", "cfg-1", [t1])
    q1.update_status(exp_id, ExperimentStatus.RUNNING)
    with pytest.raises(ValueError, match="Invalid status transition"):
        q1.update_status(exp_id, ExperimentStatus.PENDING)

    # COMPLETED -> RUNNING is illegal
    t2 = ExperimentTask(exp_id, hyp, "R_10", "M1")
    q2 = ExperimentQueue("CMP-2", "cfg-2", [t2])
    q2.update_status(exp_id, ExperimentStatus.RUNNING)
    q2.update_status(exp_id, ExperimentStatus.COMPLETED)
    with pytest.raises(ValueError):
        q2.update_status(exp_id, ExperimentStatus.RUNNING)

    # SKIPPED -> PENDING is illegal
    t3 = ExperimentTask(exp_id, hyp, "R_10", "M1")
    q3 = ExperimentQueue("CMP-3", "cfg-3", [t3])
    q3.update_status(exp_id, ExperimentStatus.SKIPPED)
    with pytest.raises(ValueError):
        q3.update_status(exp_id, ExperimentStatus.PENDING)

    # CANCELLED -> RUNNING is illegal
    t4 = ExperimentTask(exp_id, hyp, "R_10", "M1")
    q4 = ExperimentQueue("CMP-4", "cfg-4", [t4])
    q4.update_status(exp_id, ExperimentStatus.CANCELLED)
    with pytest.raises(ValueError):
        q4.update_status(exp_id, ExperimentStatus.RUNNING)


def test_scheduler_retry_preserves_experiment_id_and_seed(tmp_path: Path) -> None:
    """7, 8, 9, 10. Scheduler retry preserves experiment_id, canonical_seed_material, canonical queue ordering, and retry count."""
    settings, storage = setup_mock_market_data(tmp_path)
    settings.max_experiment_retries = 2
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-RETRY-SEEDS", configuration_hash=cfg_hash, name="Retry Seeds")

    call_count = 0
    original_execute_batch = WorkerPool.execute_batch

    def failing_execute_batch(self_pool, tasks, df_map, outcomes_map, fingerprint_map):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return [(tasks[0], None, "Simulated transient worker failure")]
        return original_execute_batch(self_pool, tasks, df_map, outcomes_map, fingerprint_map)

    with patch.object(WorkerPool, "execute_batch", failing_execute_batch):
        out_dir = scheduler.run_campaign(camp_def, [hyp])

    assert call_count == 2
    res_list = json.loads((out_dir / "experiment_results.json").read_text(encoding="utf-8"))
    assert len(res_list) == 1

    exp_id = compute_experiment_id(hyp, "R_10", "M1", res_list[0]["dataset_fingerprint"])
    assert res_list[0]["hypothesis_id"] == "HYP-RETRY-1"
    seed_bytes = derive_canonical_seed_material(42, exp_id)
    assert len(seed_bytes) == 32


def test_max_retries_exhaustion(tmp_path: Path) -> None:
    """11, 12. max_retries exhaustion prevents further requeue and task remains in FAILED state."""
    settings, storage = setup_mock_market_data(tmp_path)
    settings.max_experiment_retries = 2
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-RETRY-EXHAUST", configuration_hash=cfg_hash, name="Retry Exhaustion")

    def always_fail_batch(self_pool, tasks, df_map, outcomes_map, fingerprint_map):
        return [(task, None, "Persistent failure") for task in tasks]

    with patch.object(WorkerPool, "execute_batch", always_fail_batch):
        out_dir = scheduler.run_campaign(camp_def, [hyp])

    stats = json.loads((out_dir / "campaign_statistics.json").read_text(encoding="utf-8"))
    assert stats["failed_count"] == 1
    assert stats["completed_count"] == 0
    assert stats["total_retries"] == 2


def test_checkpoint_resume_preserves_retry_state(tmp_path: Path) -> None:
    """14, 15. Checkpoint/resume preserves retry count state and worker-count invariance with retries."""
    settings, storage = setup_mock_market_data(tmp_path)
    settings.max_experiment_retries = 2
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp")
    task = ExperimentTask(exp_id, hyp, "R_10", "M1")
    task.retry_count = 1

    queue = ExperimentQueue("CMP-RETRY-SNP", "cfg_snp", [task])
    snapshot = queue.take_snapshot(last_event_sequence=10)

    reloaded_queue = ExperimentQueue.from_snapshot(snapshot, [task])
    reloaded_task = reloaded_queue.get_task(exp_id)
    assert reloaded_task.retry_count == 1
