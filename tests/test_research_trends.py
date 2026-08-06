"""
Project GOAT v0.9 — Dedicated Tests for Research Trends
"""

import pytest

from goat.intelligence.analytics.engine import ResearchAnalyticsEngine
from goat.intelligence.core.enums import TrendDirection
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize(
    "vals, expected_direction",
    [
        ([10.0, 20.0, 30.0], TrendDirection.IMPROVING),
        ([30.0, 20.0, 10.0], TrendDirection.DECLINING),
        ([10.0, 10.1, 10.2], TrendDirection.STABLE),
    ],
)
def test_research_trend_computation(
    index_type: SyntheticIndexType, vals: list[float], expected_direction: TrendDirection
) -> None:
    analytics = ResearchAnalyticsEngine()
    metric_name = f"metric_{index_type.value}"

    trend = analytics.compute_trend(metric_name, vals)
    assert trend.trend_id.startswith("TRD_")
    assert trend.metric_name == metric_name
    assert trend.direction == expected_direction
