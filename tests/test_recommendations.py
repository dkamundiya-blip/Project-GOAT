"""
Project GOAT v0.9 — Dedicated Tests for Scientific Research Recommendations Engine
"""

import pytest

from goat.intelligence.core.enums import (
    InsightCategory,
    InsightImpact,
    RecommendationPriority,
)
from goat.intelligence.insights.engine import InsightEngine
from goat.intelligence.recommendations.engine import RecommendationEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
PRIORITIES = list(RecommendationPriority)
UTILITIES = [5.0, 15.0, 25.0, 45.0, 65.0, 85.0, 95.0, 100.0]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("prio", PRIORITIES)
@pytest.mark.parametrize("utility", UTILITIES)
def test_recommendation_engine_generate_matrix(
    index_type: SyntheticIndexType, prio: RecommendationPriority, utility: float
) -> None:
    rec_engine = RecommendationEngine()
    topic = f"Research Topic {index_type.value}"

    rec = rec_engine.generate_recommendation(
        topic=topic,
        rationale="Scientific rationale for prioritizing research.",
        priority=prio,
        expected_utility=utility,
    )

    assert rec.recommendation_id.startswith("REC_")
    assert rec.topic == topic
    assert rec.priority == prio
    assert rec.expected_utility == utility


@pytest.mark.parametrize("index_type", INDICES)
def test_recommendation_engine_formulate_from_insights(index_type: SyntheticIndexType) -> None:
    i_engine = InsightEngine()
    r_engine = RecommendationEngine()

    insight = i_engine.generate_insight(
        category=InsightCategory.HYPOTHESIS_SUCCESS,
        title="High Success Category",
        findings_statement="Category A performed exceptionally well.",
        impact=InsightImpact.HIGH,
        confidence_level=0.95,
        supporting_data={"category": index_type.value, "success_rate": 0.85},
    )

    recs = r_engine.formulate_recommendations_from_insights([insight])
    assert len(recs) == 1
    rec = recs[0]
    assert rec.recommendation_id.startswith("REC_")
    assert index_type.value in rec.topic
