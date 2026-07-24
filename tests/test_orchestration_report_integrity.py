"""
Project GOAT v0.5 — Unit Tests for Report Generation Artifact Integrity (P1-03)
"""

import json
from pathlib import Path
import sys
from unittest.mock import patch
import pandas as pd
import pytest

from goat.config import GoatSettings
from goat.data.schemas import Candle, DataSource, Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition, InfrastructureFailure
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash
from goat.research.hypothesis.definition import HypothesisDefinition
from scripts.run_campaign import main


def setup_integrity_mock_data(tmp_path: Path) -> tuple[GoatSettings, ParquetStorage]:
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


def make_dummy_hypothesis(hyp_id: str = "HYP-INT-1") -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="Integrity Test Hypothesis",
        description="Testing report generation artifact integrity",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )


def test_valid_artifacts_regenerate_reports(tmp_path: Path) -> None:
    """1, 10. Valid persisted artifacts regenerate reports deterministically and successfully."""
    settings, storage = setup_integrity_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-INT-VALID", configuration_hash=cfg_hash, name="Integrity Valid")

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    md_report1 = (out_dir / "report.md").read_text(encoding="utf-8")

    # Regenerate reports
    resumed_dir = scheduler.generate_reports("CMP-INT-VALID")
    md_report2 = (resumed_dir / "report.md").read_text(encoding="utf-8")

    assert resumed_dir == out_dir
    assert md_report1 == md_report2


def test_missing_manifest_fails_explicitly(tmp_path: Path) -> None:
    """5, 7. Missing required campaign_manifest.json fails explicitly with InfrastructureFailure."""
    settings, storage = setup_integrity_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-INT-NOMANIFEST", configuration_hash=cfg_hash, name="No Manifest")

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    (out_dir / "campaign_manifest.json").unlink()

    with pytest.raises(InfrastructureFailure, match="Required campaign manifest artifact missing"):
        scheduler.generate_reports("CMP-INT-NOMANIFEST")


def test_malformed_manifest_fails_explicitly(tmp_path: Path) -> None:
    """6, 7. Malformed campaign_manifest.json fails explicitly."""
    settings, storage = setup_integrity_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-INT-BADMANIFEST", configuration_hash=cfg_hash, name="Bad Manifest")

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    (out_dir / "campaign_manifest.json").write_text("{CORRUPTED_JSON_NOT_VALID", encoding="utf-8")

    with pytest.raises(InfrastructureFailure, match="Corrupted or invalid campaign manifest artifact"):
        scheduler.generate_reports("CMP-INT-BADMANIFEST")


def test_missing_required_results_when_completed_tasks_exist_fails(tmp_path: Path) -> None:
    """2, 8. Missing required experiment_results.json when completed tasks exist fails explicitly and never converts to []."""
    settings, storage = setup_integrity_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-INT-NORESULTS", configuration_hash=cfg_hash, name="No Results")

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    (out_dir / "experiment_results.json").unlink()

    with pytest.raises(InfrastructureFailure, match="Missing required experiment results artifact"):
        scheduler.generate_reports("CMP-INT-NORESULTS")


def test_malformed_results_json_fails_explicitly(tmp_path: Path) -> None:
    """3, 4, 8. Malformed or schema-invalid experiment_results.json fails explicitly and is never silently converted to []."""
    settings, storage = setup_integrity_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-INT-BADRESULTS", configuration_hash=cfg_hash, name="Bad Results")

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    (out_dir / "experiment_results.json").write_text("[{'invalid_schema': 123}]", encoding="utf-8")

    with pytest.raises(InfrastructureFailure, match="Corrupted or invalid experiment results artifact"):
        scheduler.generate_reports("CMP-INT-BADRESULTS")


def test_failed_regeneration_does_not_overwrite_valid_report(tmp_path: Path) -> None:
    """9. A failed regeneration does not replace a previously valid final report with a partial report."""
    settings, storage = setup_integrity_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-INT-PRESERVE", configuration_hash=cfg_hash, name="Preserve Report")

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    original_md = (out_dir / "report.md").read_text(encoding="utf-8")

    # Corrupt results JSON so regeneration will fail
    (out_dir / "experiment_results.json").write_text("{CORRUPTED}", encoding="utf-8")

    with pytest.raises(InfrastructureFailure):
        scheduler.generate_reports("CMP-INT-PRESERVE")

    # Verify original report.md remains untouched
    assert (out_dir / "report.md").read_text(encoding="utf-8") == original_md


def test_cli_report_surfaces_failure(tmp_path: Path) -> None:
    """11. CLI report surfaces artifact integrity failures rather than silently reporting success."""
    settings = setup_integrity_mock_data(tmp_path)[0]

    with patch("scripts.run_campaign.GoatSettings", return_value=settings):
        # Run campaign
        with patch.object(sys, "argv", ["run_campaign.py", "launch", "--symbols", "R_10", "--timeframes", "M1"]):
            main()

        camp_id = list(settings.get_campaign_data_dir().iterdir())[0].name
        manifest_path = settings.get_campaign_data_dir() / camp_id / "campaign_manifest.json"
        manifest_path.write_text("{CORRUPTED_JSON", encoding="utf-8")

        with patch.object(sys, "argv", ["run_campaign.py", "report", "--campaign-id", camp_id]):
            with pytest.raises(InfrastructureFailure, match="Corrupted or invalid campaign manifest"):
                main()


def test_failed_campaign_report_contains_warning(tmp_path: Path) -> None:
    """12. FAILED/CANCELLED partial-progress reporting continues to work when inputs are valid."""
    settings, storage = setup_integrity_mock_data(tmp_path)
    scheduler = ExperimentScheduler(settings=settings, storage=storage)
    hyp = make_dummy_hypothesis()

    cfg_hash = compute_configuration_hash([hyp], ["R_10"], ["M1"], master_seed=42, fdr_alpha=0.05)
    camp_def = CampaignDefinition(campaign_id="CMP-INT-PARTIAL", configuration_hash=cfg_hash, name="Partial Report")

    out_dir = scheduler.run_campaign(camp_def, [hyp])
    manifest_data = json.loads((out_dir / "campaign_manifest.json").read_text(encoding="utf-8"))
    manifest_data["campaign"]["status"] = "FAILED"
    (out_dir / "campaign_manifest.json").write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    resumed_dir = scheduler.generate_reports("CMP-INT-PARTIAL")
    md_content = (resumed_dir / "report.md").read_text(encoding="utf-8")

    assert "Campaign Terminated Early" in md_content
    assert "Status is `FAILED`" in md_content
