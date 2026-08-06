"""
Project GOAT v0.9 — Dedicated Tests for Intelligence SQLite Repositories
"""

import sqlite3
import pytest

from goat.intelligence.core.canonical import (
    compute_institutional_recommendation_id,
    compute_intelligence_summary_id,
    compute_meta_analysis_id,
    compute_research_health_id,
    compute_research_insight_id,
    compute_research_trend_id,
)
from goat.intelligence.core.enums import (
    HealthStatus,
    InsightCategory,
    InsightImpact,
    RecommendationPriority,
    TrendDirection,
)
from goat.intelligence.core.models import (
    InstitutionalRecommendation,
    IntelligenceSummary,
    MetaAnalysis,
    ResearchHealth,
    ResearchInsight,
    ResearchTrend,
)
from goat.intelligence.persistence.sqlite import IntelligencePersistenceContext
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_sqlite_repository_roundtrips(index_type: SyntheticIndexType) -> None:
    db = IntelligencePersistenceContext(":memory:")

    # Pragma check
    cursor = db.conn.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1

    i_id, i_hash = compute_research_insight_id("HYPOTHESIS_SUCCESS", f"Title_{index_type.value}", "HIGH")
    insight = ResearchInsight(
        insight_id=i_id,
        category=InsightCategory.HYPOTHESIS_SUCCESS,
        impact=InsightImpact.HIGH,
        title=f"Title_{index_type.value}",
        findings_statement="Statement",
        confidence_level=0.95,
        supporting_data={"sym": index_type.value},
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=i_hash,
    )
    db.insights.save(insight)

    m_id, m_hash = compute_meta_analysis_id(f"Meta_{index_type.value}", 10, "2026-01-01T00:00:00Z")
    meta = MetaAnalysis(
        meta_analysis_id=m_id,
        analysis_title=f"Meta_{index_type.value}",
        sample_size=10,
        pooled_effect_size=0.15,
        heterogeneity_i2=5.0,
        p_value=0.01,
        key_findings=["Finding 1"],
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=m_hash,
    )
    db.meta_analyses.save(meta)

    t_id, t_hash = compute_research_trend_id(f"trend_{index_type.value}", "IMPROVING", "2026-01-01T00:00:00Z")
    trend = ResearchTrend(
        trend_id=t_id,
        metric_name=f"trend_{index_type.value}",
        direction=TrendDirection.IMPROVING,
        historical_values=[10.0, 20.0],
        percentage_change=100.0,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=t_hash,
    )
    db.trends.save(trend)

    r_id, r_hash = compute_institutional_recommendation_id("P1_URGENT", f"Topic_{index_type.value}", "2026-01-01T00:00:00Z")
    rec = InstitutionalRecommendation(
        recommendation_id=r_id,
        priority=RecommendationPriority.P1_URGENT,
        topic=f"Topic_{index_type.value}",
        rationale="Rationale",
        expected_utility=90.0,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=r_hash,
    )
    db.recommendations.save(rec)

    h_id, h_hash = compute_research_health_id("EXCELLENT", 90.0, "2026-01-01T00:00:00Z")
    health = ResearchHealth(
        health_id=h_id,
        health_score=90.0,
        status=HealthStatus.EXCELLENT,
        success_rate=0.80,
        efficiency_score=90.0,
        waste_percentage=10.0,
        diagnostics=["Diag"],
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=h_hash,
    )
    db.health.save(health)

    s_id, s_hash = compute_intelligence_summary_id("2026-01-01T00:00:00Z", 1, 1)
    summary = IntelligenceSummary(
        summary_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        total_insights=1,
        total_meta_analyses=1,
        total_recommendations=1,
        overall_health_score=90.0,
        insights_by_category={"HYPOTHESIS_SUCCESS": 1},
        recommendations_by_priority={"P1_URGENT": 1},
        metadata={},
        canonical_hash=s_hash,
    )
    db.summaries.save(summary)

    # Retrieval assertions
    fetched_i = db.insights.get_by_id(i_id)
    assert fetched_i is not None
    assert fetched_i.insight_id == i_id
    assert fetched_i.canonical_hash == i_hash

    fetched_m = db.meta_analyses.get_by_id(m_id)
    assert fetched_m is not None
    assert fetched_m.meta_analysis_id == m_id

    db.close()
