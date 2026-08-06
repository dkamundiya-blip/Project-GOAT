"""
Project GOAT v0.9 — Dedicated Tests for Master Intelligence Engine
"""

import pytest

from goat.intelligence.engine import MasterIntelligenceEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_master_intelligence_engine_workflow(index_type: SyntheticIndexType) -> None:
    engine = MasterIntelligenceEngine(":memory:")

    hyp_records = [
        {"category": index_type.value, "status": "PASSED"},
        {"category": index_type.value, "status": "REJECTED"},
    ]
    exp_records = [
        {"duration_seconds": 120, "is_conclusive": True, "effect_size": 0.15, "sample_size": 50},
    ]
    inv_records = [
        {"regime": "HIGH_VOLATILITY"},
    ]

    health, insights, recs, meta = engine.evaluate_research_intelligence(
        hypotheses_records=hyp_records,
        experiment_records=exp_records,
        invalidation_records=inv_records,
        timestamp_str="2026-01-01T00:00:00Z",
    )

    assert health.health_id.startswith("RHL_")
    assert len(insights) >= 1
    assert len(recs) >= 1
    assert meta.meta_analysis_id.startswith("MTA_")

    summary = engine.generate_summary("2026-01-01T00:00:00Z")
    assert summary.summary_id.startswith("ISM_")
    assert summary.total_insights >= 1
    assert summary.total_recommendations >= 1

    engine.close()


def test_master_intelligence_multi_symbol() -> None:
    engine = MasterIntelligenceEngine(":memory:")
    symbols = ["VOLATILITY_10", "BOOM_1000", "CRASH_500", "JUMP_75", "STEP_INDEX"]

    hyp_records = [{"category": sym, "status": "PASSED"} for sym in symbols]
    exp_records = [{"duration_seconds": 150, "is_conclusive": True, "effect_size": 0.20, "sample_size": 100} for _ in symbols]
    inv_records = [{"regime": "SIDEWAYS"} for _ in symbols]

    health, insights, recs, meta = engine.evaluate_research_intelligence(
        hypotheses_records=hyp_records,
        experiment_records=exp_records,
        invalidation_records=inv_records,
    )

    summary = engine.generate_summary()
    assert summary.total_insights > 0
    assert summary.total_recommendations > 0
    assert summary.total_meta_analyses == 1

    engine.close()
