"""
Project GOAT v0.5 — Unit Tests for CLI Interface
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
from goat.orchestration.campaign import CampaignDefinition
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash
from goat.research.hypothesis.definition import HypothesisDefinition
from scripts.run_campaign import main


def setup_cli_mock_data(tmp_path: Path) -> GoatSettings:
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
    return settings


def test_cli_help(capsys) -> None:
    """Test CLI parser help screen output."""
    with patch.object(sys, "argv", ["run_campaign.py", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "launch" in captured.out
    assert "status" in captured.out
    assert "resume" in captured.out
    assert "cancel" in captured.out
    assert "report" in captured.out


def test_cli_launch_and_status(tmp_path: Path, capsys) -> None:
    """Test CLI launch subcommand executes campaign and status returns persisted state."""
    settings = setup_cli_mock_data(tmp_path)

    with patch("scripts.run_campaign.GoatSettings", return_value=settings):
        # 1. CLI Launch
        with patch.object(sys, "argv", ["run_campaign.py", "launch", "--symbols", "R_10", "--timeframes", "M1", "--workers", "2"]):
            main()

        captured_launch = capsys.readouterr().out
        assert "PROJECT GOAT v0.5 — EXPERIMENT CAMPAIGN LAUNCH" in captured_launch
        assert "CAMPAIGN EXECUTION COMPLETED" in captured_launch

        # Find created campaign_id directory
        camp_dirs = list(settings.get_campaign_data_dir().iterdir())
        assert len(camp_dirs) == 1
        camp_id = camp_dirs[0].name

        # 2. CLI Status
        with patch.object(sys, "argv", ["run_campaign.py", "status", "--campaign-id", camp_id]):
            main()

        captured_status = capsys.readouterr().out
        assert "PROJECT GOAT v0.5 — CAMPAIGN STATUS" in captured_status
        assert camp_id in captured_status
        assert "COMPLETED" in captured_status


def test_cli_cancel_and_report(tmp_path: Path, capsys) -> None:
    """Test CLI cancel and report subcommands delegate to orchestrator."""
    settings = setup_cli_mock_data(tmp_path)

    with patch("scripts.run_campaign.GoatSettings", return_value=settings):
        # Launch campaign first
        with patch.object(sys, "argv", ["run_campaign.py", "launch", "--symbols", "R_10", "--timeframes", "M1"]):
            main()

        camp_id = list(settings.get_campaign_data_dir().iterdir())[0].name
        capsys.readouterr()  # Clear launch output

        # CLI Report (regenerates report.md and report.json without re-running experiments)
        with patch.object(sys, "argv", ["run_campaign.py", "report", "--campaign-id", camp_id]):
            main()

        captured_report = capsys.readouterr().out
        assert "CAMPAIGN REPORT GENERATION" in captured_report
        assert "Reports regenerated cleanly" in captured_report

        # Modify manifest to PAUSED to test CLI cancel
        manifest_path = settings.get_campaign_data_dir() / camp_id / "campaign_manifest.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_data["campaign"]["status"] = "PAUSED"
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        # CLI Cancel
        with patch.object(sys, "argv", ["run_campaign.py", "cancel", "--campaign-id", camp_id]):
            main()

        captured_cancel = capsys.readouterr().out
        assert "CAMPAIGN CANCEL" in captured_cancel
        assert "Campaign cancelled cleanly" in captured_cancel


def test_cli_resume(tmp_path: Path, capsys) -> None:
    """Test CLI resume invokes actual resume path."""
    settings = setup_cli_mock_data(tmp_path)

    with patch("scripts.run_campaign.GoatSettings", return_value=settings):
        # Launch campaign
        with patch.object(sys, "argv", ["run_campaign.py", "launch", "--symbols", "R_10", "--timeframes", "M1"]):
            main()

        camp_id = list(settings.get_campaign_data_dir().iterdir())[0].name
        capsys.readouterr()

        # Set status to PAUSED to simulate non-terminal campaign
        manifest_path = settings.get_campaign_data_dir() / camp_id / "campaign_manifest.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_data["campaign"]["status"] = "PAUSED"
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        # CLI Resume
        with patch.object(sys, "argv", ["run_campaign.py", "resume", "--campaign-id", camp_id]):
            main()

        captured_resume = capsys.readouterr().out
        assert "CAMPAIGN RESUME" in captured_resume
        assert "Resumed campaign output directory" in captured_resume
