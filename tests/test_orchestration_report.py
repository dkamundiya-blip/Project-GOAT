"""
Project GOAT v0.5 — Unit Tests for Reporting & Output Abstraction Layer
"""

import json
from pathlib import Path
import pytest

from goat.orchestration.campaign import (
    CampaignManifest,
    CampaignStatus,
)
from goat.orchestration.report import (
    CampaignReportGenerator,
    JsonReportGenerator,
    MarkdownReportGenerator,
)
from goat.research.hypothesis.result import HypothesisResult


def test_markdown_and_json_report_generation(tmp_path) -> None:
    """Test MarkdownReportGenerator and JsonReportGenerator produce expected artifacts."""
    manifest = CampaignManifest(
        campaign={"campaign_id": "CMP-REP-01", "name": "Report Campaign", "status": "COMPLETED"},
        configuration={"configuration_hash": "cfg_rep_01", "fdr_alpha": 0.05},
        research_provenance={"dataset_fingerprint": "fp_rep_01"},
    )

    res1 = HypothesisResult(
        hypothesis_id="HYP-REP-1",
        version="1.0.0",
        dataset_fingerprint="fp_rep_01",
        partition="train",
        symbol="R_10",
        timeframe="M1",
        conditional_sample_count=150,
        baseline_sample_count=300,
        validation_status="SUPPORTED",
        edge_score={"total_score": 82.5},
        adjusted_q_value=0.001,
        effect_size=0.45,
    )

    statistics = {
        "campaign_id": "CMP-REP-01",
        "total_experiments": 1,
        "completed_count": 1,
        "supported_edges": 1,
    }

    md_gen = MarkdownReportGenerator()
    json_gen = JsonReportGenerator(report_schema_version=1)

    md_file = md_gen.generate(manifest, [res1], statistics, tmp_path)
    json_file = json_gen.generate(manifest, [res1], statistics, tmp_path)

    assert md_file.exists()
    assert json_file.exists()

    md_text = md_file.read_text(encoding="utf-8")
    assert "CMP-REP-01" in md_text
    assert "Supported Edges" in md_text
    assert "HYP-REP-1" in md_text

    json_data = json.loads(json_file.read_text(encoding="utf-8"))
    assert json_data["report_schema_version"] == 1
    assert json_data["campaign"]["campaign_id"] == "CMP-REP-01"
    assert len(json_data["results"]) == 1


def test_partial_progress_reporting_on_failure(tmp_path) -> None:
    """Test report generation on FAILED campaign renders warning banner."""
    manifest = CampaignManifest(
        campaign={"campaign_id": "CMP-FAILED-01", "name": "Failed Campaign", "status": "FAILED"},
        configuration={"configuration_hash": "cfg_failed_01"},
        research_provenance={"dataset_fingerprint": "fp_failed"},
    )

    md_gen = MarkdownReportGenerator()
    md_file = md_gen.generate(manifest, [], {"total_experiments": 5, "completed_count": 2}, tmp_path)

    md_text = md_file.read_text(encoding="utf-8")
    assert "Campaign Terminated Early" in md_text
    assert "FAILED" in md_text
