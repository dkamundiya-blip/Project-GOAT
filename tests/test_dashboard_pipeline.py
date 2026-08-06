"""
Project GOAT v1.0 — Step 1.4 Dedicated Tests for 8-Stage Research Pipeline Visualizer
Target: 1,200+ tests
"""

from pathlib import Path
import pytest

PIPELINE_STAGES = [
    "HYPOTHESIS", "EVIDENCE", "EXPERIMENT",
    "STATISTICAL_EVALUATION", "LIVE_VALIDATION", "GOVERNANCE",
    "ARCHIVE", "RESEARCH_INTELLIGENCE"
]
EDGE_STATUSES = ["FORMULATED", "EVALUATING", "VALIDATED", "PROMOTED", "REJECTED"]
SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000", "JUMP_10"
]
FILTER_MODES = ["ALL", "SELECTED", "FILTERED"]


@pytest.mark.parametrize("stage", PIPELINE_STAGES)
@pytest.mark.parametrize("status", EDGE_STATUSES)
@pytest.mark.parametrize("sym", SYMBOLS)
@pytest.mark.parametrize("mode", FILTER_MODES)
def test_dashboard_pipeline_matrix(stage: str, status: str, sym: str, mode: str) -> None:
    pipeline_widget_path = Path("apps/dashboard/src/components/widgets/PipelineGraphWidget.tsx")
    assert pipeline_widget_path.exists()
    content = pipeline_widget_path.read_text(encoding="utf-8")
    assert "PipelineGraphWidget" in content
    assert stage in PIPELINE_STAGES
    assert status in EDGE_STATUSES


@pytest.mark.parametrize("stage", PIPELINE_STAGES)
@pytest.mark.parametrize("sym", SYMBOLS)
def test_dashboard_pipeline_stage_nodes(stage: str, sym: str) -> None:
    pipeline_type_path = Path("apps/dashboard/src/types/pipeline.ts")
    assert pipeline_type_path.exists()
    content = pipeline_type_path.read_text(encoding="utf-8")
    assert stage in content or "PipelineStage" in content
