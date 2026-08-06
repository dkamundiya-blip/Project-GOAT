"""
Project GOAT v0.9 — Dedicated Tests for Institutional Research Health Assessment
"""

import pytest

from goat.intelligence.analytics.engine import ResearchAnalyticsEngine
from goat.intelligence.core.enums import HealthStatus
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_research_health_scoring(index_type: SyntheticIndexType) -> None:
    analytics = ResearchAnalyticsEngine()

    hyp_records = [
        {"category": index_type.value, "status": "PASSED"},
        {"category": index_type.value, "status": "PASSED"},
    ]
    exp_records = [
        {"duration_seconds": 100, "is_conclusive": True},
    ]
    inv_records = []

    health = analytics.compute_research_health(hyp_records, exp_records, inv_records)
    assert health.health_id.startswith("RHL_")
    assert health.status in (HealthStatus.EXCELLENT, HealthStatus.GOOD)
    assert health.success_rate == 1.0
    assert health.health_score >= 80.0
