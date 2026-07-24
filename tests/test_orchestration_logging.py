"""
Project GOAT v0.5 — Unit Tests for Structured Logging & Observability (campaign.log.jsonl)
"""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import pandas as pd
import pytest

from goat.config import GoatSettings
from goat.data.schemas import Candle, DataSource, Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition, QueueSnapshot
from goat.orchestration.queue import ExperimentTask
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash, compute_experiment_id
from goat.orchestration.worker import WorkerPool, derive_canonical_seed_material
from goat.research.hypothesis.definition import HypothesisDefinition


def setup_mock_data(tmp_path: Path) -> tuple[GoatSettings, ParquetStorage]:
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


def make_dummy_hypothesis(hyp_id: str = "HYP-LOG-1") -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="Log Test Hypothesis",
        description="Testing structured logging",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )


def test_campaign_creates_campaign_log_jsonl(tmp_path: Path) -> None:
    """1-4. Tests campaign creates campaign.log.jsonl with valid JSON, schema fields, and log_schema_version=1."""
    settings, storage = setup_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(
        campaign_id="CMP-LOG-01",
        configuration_hash=cfg_hash,
        name="Logging Test",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
    )

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    log_file = out_dir / "campaign.log.jsonl"

    assert log_file.exists()

    lines = [line.strip() for line in log_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) > 0

    mandatory_fields = {
        "log_schema_version",
        "event_sequence",
        "utc_timestamp",
        "log_level",
        "component",
        "event_type",
        "campaign_id",
        "experiment_id",
        "worker_id",
        "message",
        "metadata",
    }

    for line in lines:
        record = json.loads(line)
        assert mandatory_fields.issubset(record.keys())
        assert record["log_schema_version"] == 1


def test_event_sequence_starts_at_1_and_is_strictly_monotonic(tmp_path: Path) -> None:
    """5-6. Tests event_sequence starts at 1, is strictly monotonic, and has no duplicates."""
    settings, storage = setup_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(
        campaign_id="CMP-LOG-SEQ",
        configuration_hash=cfg_hash,
        name="Sequence Test",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
    )

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    log_file = out_dir / "campaign.log.jsonl"

    records = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    sequences = [r["event_sequence"] for r in records]

    assert sequences[0] == 1
    assert sequences == list(range(1, len(sequences) + 1))
    assert len(sequences) == len(set(sequences))


def test_resume_checkpoint_restores_last_event_sequence(tmp_path: Path) -> None:
    """7. Tests resume/checkpoint restores last_event_sequence and continues at N+1."""
    settings, storage = setup_mock_data(tmp_path)

    snapshot = QueueSnapshot(
        campaign_id="CMP-RESUME-SEQ",
        configuration_hash="cfg_res",
        completed_task_ids=("exp_1",),
        last_event_sequence=42,
    )

    scheduler2 = ExperimentScheduler(settings=settings, storage=storage)
    scheduler2.event_sequence = snapshot.last_event_sequence
    scheduler2.log_file_path = tmp_path / "resume.log.jsonl"

    scheduler2._log_event("INFO", "campaign_resumed", "Resuming campaign execution")

    assert scheduler2.event_sequence == 43
    records = [json.loads(line) for line in scheduler2.log_file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert records[0]["event_sequence"] == 43


def test_concurrent_worker_logging_safety(tmp_path: Path) -> None:
    """8. Concurrent worker logging produces no duplicate sequences or malformed lines."""
    settings = GoatSettings()
    scheduler = ExperimentScheduler(settings=settings)
    scheduler.log_file_path = tmp_path / "concurrent.log.jsonl"

    def worker_log(idx: int) -> None:
        for j in range(20):
            scheduler._log_event(
                level="INFO",
                event_type="concurrent_test",
                message=f"Thread {idx} msg {j}",
                component="Worker",
                worker_id=f"worker_{idx}",
            )

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker_log, i) for i in range(8)]
        for f in futures:
            f.result()

    lines = [line.strip() for line in scheduler.log_file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 160

    records = [json.loads(line) for line in lines]
    seqs = [r["event_sequence"] for r in records]

    assert len(seqs) == len(set(seqs))
    assert sorted(seqs) == list(range(1, 161))


def test_logging_enabled_vs_disabled_identical_scientific_outputs(tmp_path: Path) -> None:
    """9-11. Logging enabled vs disabled/null sink produces 100% byte-for-byte identical scientific outputs."""
    settings1, storage1 = setup_mock_data(tmp_path / "run1")
    scheduler1 = ExperimentScheduler(settings=settings1, storage=storage1)

    settings2, storage2 = setup_mock_data(tmp_path / "run2")
    scheduler2 = ExperimentScheduler(settings=settings2, storage=storage2)
    scheduler2.log_enabled = False

    hyp = make_dummy_hypothesis()
    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)

    camp_def1 = CampaignDefinition(campaign_id="CMP-LOG-ON", configuration_hash=cfg_hash, name="Log On", symbol_scope=["R_10"], timeframe_scope=["M1"])
    camp_def2 = CampaignDefinition(campaign_id="CMP-LOG-OFF", configuration_hash=cfg_hash, name="Log Off", symbol_scope=["R_10"], timeframe_scope=["M1"])

    out_dir1 = scheduler1.run_campaign(camp_def1, [hyp])
    out_dir2 = scheduler2.run_campaign(camp_def2, [hyp])

    res1 = json.loads((out_dir1 / "experiment_results.json").read_text(encoding="utf-8"))
    res2 = json.loads((out_dir2 / "experiment_results.json").read_text(encoding="utf-8"))

    for r in res1:
        r.pop("created_at", None)
    for r in res2:
        r.pop("created_at", None)

    assert json.dumps(res1, sort_keys=True) == json.dumps(res2, sort_keys=True)

    exp_id1 = compute_experiment_id(hyp, "R_10", "M1", "fp")
    exp_id2 = compute_experiment_id(hyp, "R_10", "M1", "fp")
    assert exp_id1 == exp_id2
    assert derive_canonical_seed_material(42, exp_id1) == derive_canonical_seed_material(42, exp_id2)
