"""
Project GOAT v0.9 — Dedicated Tests for Research Analytics Engine
"""

import pytest

from goat.intelligence.analytics.engine import ResearchAnalyticsEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_research_analytics_hypothesis_success_rates(index_type: SyntheticIndexType) -> None:
    analytics = ResearchAnalyticsEngine()
    records = [
        {"category": f"CAT_{index_type.value}", "status": "PASSED"},
        {"category": f"CAT_{index_type.value}", "status": "REJECTED"},
        {"category": f"CAT_{index_type.value}", "status": "PROMOTED"},
        {"category": f"CAT_{index_type.value}", "status": "REJECTED"},
    ]

    rates = analytics.analyze_hypothesis_success_rates(records)
    cat_key = f"CAT_{index_type.value}"
    assert cat_key in rates
    assert rates[cat_key] == 0.50


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_research_analytics_experiment_efficiency(index_type: SyntheticIndexType) -> None:
    analytics = ResearchAnalyticsEngine()
    exp_records = [
        {"duration_seconds": 100, "is_conclusive": True, "symbol": index_type.value},
        {"duration_seconds": 200, "is_conclusive": True, "symbol": index_type.value},
        {"duration_seconds": 300, "is_conclusive": False, "symbol": index_type.value},
    ]

    res = analytics.analyze_experiment_efficiency(exp_records)
    assert res["total_experiments"] == 3
    assert res["conclusive_experiments_count"] == 2
    assert res["efficiency_score"] == 66.67


@pytest.mark.parametrize("index_type", INDICES[:5])
def test_research_analytics_health(index_type: SyntheticIndexType) -> None:
    analytics = ResearchAnalyticsEngine()
    hyp_records = [{"category": "VOLATILITY", "status": "PASSED"}]
    exp_records = [{"duration_seconds": 100, "is_conclusive": True}]
    inv_records = [{"regime": "HIGH_VOLATILITY"}]

    health = analytics.compute_research_health(hyp_records, exp_records, inv_records)
    assert health.health_id.startswith("RHL_")
    assert health.health_score > 0.0
    assert len(health.diagnostics) == 3
