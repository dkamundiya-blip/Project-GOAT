"""
Project GOAT v0.9 — Dedicated Tests for Intelligence Domain Models & Canonical Hashing
"""

import pytest
from pydantic import ValidationError

from goat.intelligence.core.canonical import (
    compute_canonical_sha256,
    compute_institutional_recommendation_id,
    compute_intelligence_summary_id,
    compute_meta_analysis_id,
    compute_research_health_id,
    compute_research_insight_id,
    compute_research_trend_id,
    serialize_canonical_json,
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
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
CATEGORIES = list(InsightCategory)
IMPACTS = list(InsightImpact)
DIRECTIONS = list(TrendDirection)
PRIORITIES = list(RecommendationPriority)
HEALTH_STATUSES = list(HealthStatus)
VERSIONS = ["1.0.0", "1.1.0", "2.0.0"]
CONFIDENCES = [0.10, 0.30, 0.50, 0.70, 0.85, 0.90, 0.95, 0.99]
TITLE_TAGS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("cat", CATEGORIES)
@pytest.mark.parametrize("imp", IMPACTS)
@pytest.mark.parametrize("conf", CONFIDENCES)
@pytest.mark.parametrize("tag", TITLE_TAGS[:3])
def test_research_insight_model_matrix(
    index_type: SyntheticIndexType, cat: InsightCategory, imp: InsightImpact, conf: float, tag: str
) -> None:
    title = f"Insight {index_type.value} {cat.value} {tag}"
    i_id, h_digest = compute_research_insight_id(cat.value, title, imp.value)

    insight = ResearchInsight(
        insight_id=i_id,
        category=cat,
        impact=imp,
        title=title,
        findings_statement=f"Findings statement for {title}",
        confidence_level=conf,
        supporting_data={"sym": index_type.value, "tag": tag},
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=h_digest,
    )

    assert insight.insight_id.startswith("RIN_")
    assert insight.canonical_hash == h_digest
    assert insight.category == cat
    assert insight.impact == imp

    with pytest.raises(ValidationError):
        insight.confidence_level = 1.5  # type: ignore


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("sample_size", [1, 5, 10, 25, 50, 100, 250, 500, 1000])
@pytest.mark.parametrize("ver", VERSIONS)
def test_meta_analysis_model_matrix(index_type: SyntheticIndexType, sample_size: int, ver: str) -> None:
    title = f"Meta Analysis {index_type.value}"
    m_id, h_digest = compute_meta_analysis_id(title, sample_size, "2026-01-01T00:00:00Z", version=ver)

    meta = MetaAnalysis(
        meta_analysis_id=m_id,
        analysis_title=title,
        sample_size=sample_size,
        pooled_effect_size=0.15,
        heterogeneity_i2=12.5,
        p_value=0.01,
        key_findings=["Key finding 1"],
        timestamp="2026-01-01T00:00:00Z",
        metadata={"version": ver},
        canonical_hash=h_digest,
    )

    assert meta.meta_analysis_id.startswith("MTA_")
    assert meta.canonical_hash == h_digest


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("change", [-50.0, -10.0, 0.0, 10.0, 50.0, 100.0, 200.0])
@pytest.mark.parametrize("ver", VERSIONS)
def test_research_trend_model(direction: TrendDirection, change: float, ver: str) -> None:
    t_id, h_digest = compute_research_trend_id("metric_x", direction.value, "2026-01-01T00:00:00Z", version=ver)

    trend = ResearchTrend(
        trend_id=t_id,
        metric_name="metric_x",
        direction=direction,
        historical_values=[10.0, 20.0],
        percentage_change=change,
        timestamp="2026-01-01T00:00:00Z",
        metadata={"version": ver},
        canonical_hash=h_digest,
    )

    assert trend.trend_id.startswith("TRD_")
    assert trend.canonical_hash == h_digest


@pytest.mark.parametrize("prio", PRIORITIES)
@pytest.mark.parametrize("utility", [10.0, 20.0, 40.0, 60.0, 80.0, 95.0, 99.0])
@pytest.mark.parametrize("index_type", INDICES)
def test_institutional_recommendation_model(prio: RecommendationPriority, utility: float, index_type: SyntheticIndexType) -> None:
    topic = f"Topic {index_type.value}"
    r_id, h_digest = compute_institutional_recommendation_id(prio.value, topic, "2026-01-01T00:00:00Z")

    rec = InstitutionalRecommendation(
        recommendation_id=r_id,
        priority=prio,
        topic=topic,
        rationale="Scientific Rationale",
        expected_utility=utility,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=h_digest,
    )

    assert rec.recommendation_id.startswith("REC_")
    assert rec.canonical_hash == h_digest


@pytest.mark.parametrize("status", HEALTH_STATUSES)
@pytest.mark.parametrize("score", [10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 100.0])
@pytest.mark.parametrize("ver", VERSIONS)
def test_research_health_model(status: HealthStatus, score: float, ver: str) -> None:
    h_id, h_digest = compute_research_health_id(status.value, score, "2026-01-01T00:00:00Z", version=ver)

    health = ResearchHealth(
        health_id=h_id,
        health_score=score,
        status=status,
        success_rate=0.50,
        efficiency_score=75.0,
        waste_percentage=25.0,
        diagnostics=["Diagnostic A"],
        timestamp="2026-01-01T00:00:00Z",
        metadata={"version": ver},
        canonical_hash=h_digest,
    )

    assert health.health_id.startswith("RHL_")
    assert health.canonical_hash == h_digest


@pytest.mark.parametrize("cnt", [0, 5, 25, 100, 500, 1000, 5000])
def test_intelligence_summary_model(cnt: int) -> None:
    s_id, h_digest = compute_intelligence_summary_id("2026-01-01T00:00:00Z", cnt, cnt)

    summary = IntelligenceSummary(
        summary_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        total_insights=cnt,
        total_meta_analyses=cnt,
        total_recommendations=cnt,
        overall_health_score=85.0,
        insights_by_category={"HYPOTHESIS_SUCCESS": cnt},
        recommendations_by_priority={"P1_URGENT": cnt},
        metadata={},
        canonical_hash=h_digest,
    )

    assert summary.summary_id.startswith("ISM_")
    assert summary.canonical_hash == h_digest
