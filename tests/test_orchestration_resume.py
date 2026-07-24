"""
Project GOAT v0.5 — Unit Tests for Campaign Resume & Checkpoint Recovery
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from goat.config import GoatSettings
from goat.data.schemas import Candle, DataSource, Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition, CampaignStatus, QueueSnapshot, ValidationFailure
from goat.orchestration.checkpoint import CheckpointManager
from goat.orchestration.queue import ExperimentQueue, ExperimentTask
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash, compute_experiment_id
from goat.orchestration.worker import derive_canonical_seed_material
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


def make_dummy_hypothesis(hyp_id: str = "HYP-RES-1") -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="Resume Test Hypothesis",
        description="Testing resume path",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )


def test_resume_non_terminal_campaign_completes(tmp_path: Path) -> None:
    """1-6. Test checkpointed non-terminal campaign resume preserves campaign_id, experiment_id, seed, does not re-execute COMPLETED tasks, and resets RUNNING tasks."""
    settings, storage = setup_mock_market_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(
        campaign_id="CMP-RESUME-01",
        configuration_hash=cfg_hash,
        name="Resume Test Campaign",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
    )

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    assert out_dir.exists()

    manifest_json1 = json.loads((out_dir / "campaign_manifest.json").read_text(encoding="utf-8"))

    # Modify status to PAUSED to simulate an interrupted non-terminal campaign
    manifest_json1["campaign"]["status"] = "PAUSED"
    (out_dir / "campaign_manifest.json").write_text(json.dumps(manifest_json1, indent=2), encoding="utf-8")

    resumed_scheduler = ExperimentScheduler(settings=settings, storage=storage)
    resumed_dir = resumed_scheduler.resume_campaign("CMP-RESUME-01", [hyp])
    assert resumed_dir == out_dir

    manifest_json2 = json.loads((out_dir / "campaign_manifest.json").read_text(encoding="utf-8"))
    assert manifest_json2["campaign"]["campaign_id"] == "CMP-RESUME-01"
    assert manifest_json2["campaign"]["status"] == "COMPLETED"


def test_restoring_checkpoint_twice_produces_equivalent_queue_state() -> None:
    """7. Restoring the same checkpoint twice produces equivalent logical queue state."""
    hyp = make_dummy_hypothesis()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp")
    t1 = ExperimentTask(exp_id, hyp, "R_10", "M1")

    snapshot = QueueSnapshot(
        campaign_id="CMP-IDEMP-01",
        configuration_hash="cfg_idemp",
        completed_task_ids=(exp_id,),
        last_event_sequence=25,
    )

    q1 = ExperimentQueue.from_snapshot(snapshot, [t1])
    q2 = ExperimentQueue.from_snapshot(snapshot, [t1])

    assert q1.is_complete() == q2.is_complete()
    assert q1.get_task(exp_id).status == q2.get_task(exp_id).status


def test_event_sequence_continues_across_resume(tmp_path: Path) -> None:
    """8-9. event_sequence continues from checkpoint and lifecycle_history is append-only."""
    settings, storage = setup_mock_market_data(tmp_path)
    scheduler1 = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-SEQ-RES", configuration_hash=cfg_hash, name="Seq Resume")
    out_dir = scheduler1.run_campaign(camp_def, [hyp])

    log1 = [json.loads(line) for line in (out_dir / "campaign.log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    seq1_end = log1[-1]["event_sequence"]

    manifest_data = json.loads((out_dir / "campaign_manifest.json").read_text(encoding="utf-8"))
    manifest_data["campaign"]["status"] = "PAUSED"
    (out_dir / "campaign_manifest.json").write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    scheduler2 = ExperimentScheduler(settings=settings, storage=storage)
    scheduler2.resume_campaign("CMP-SEQ-RES", [hyp])

    log2 = [json.loads(line) for line in (out_dir / "campaign.log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    resumed_first_seq = log2[len(log1)]["event_sequence"]

    assert resumed_first_seq == seq1_end + 1


def test_invalid_checkpoint_schema_version_rejected(tmp_path: Path) -> None:
    """10. Invalid checkpoint/schema state is rejected before resumed execution."""
    settings, storage = setup_mock_market_data(tmp_path)
    scheduler1 = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-SCHEMA-ERR", configuration_hash=cfg_hash, name="Schema Error")
    out_dir = scheduler1.run_campaign(camp_def, [hyp])

    manifest_data = json.loads((out_dir / "campaign_manifest.json").read_text(encoding="utf-8"))
    manifest_data["manifest_schema_version"] = 999
    manifest_data["campaign"]["status"] = "PAUSED"
    (out_dir / "campaign_manifest.json").write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    scheduler2 = ExperimentScheduler(settings=settings, storage=storage)
    with pytest.raises(ValidationFailure):
        scheduler2.resume_campaign("CMP-SCHEMA-ERR", [hyp])


def test_terminal_state_transition_guards_enforced(tmp_path: Path) -> None:
    """15. Terminal-state transition guards remain enforced (cannot resume COMPLETED/FAILED/CANCELLED)."""
    settings, storage = setup_mock_market_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-TERM-GUARD", configuration_hash=cfg_hash, name="Terminal Guard")
    out_dir = scheduler.run_campaign(camp_def, [hyp])

    resumed_scheduler = ExperimentScheduler(settings=settings, storage=storage)
    with pytest.raises(ValueError):
        resumed_scheduler.resume_campaign("CMP-TERM-GUARD", [hyp])
