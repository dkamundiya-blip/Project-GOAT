"""
Project GOAT v0.9 — Dedicated Tests for Intelligence Report Generator
"""

import json
import pytest

from goat.intelligence.core.canonical import (
    compute_institutional_recommendation_id,
    compute_intelligence_summary_id,
    compute_meta_analysis_id,
    compute_research_health_id,
    compute_research_insight_id,
)
from goat.intelligence.core.enums import (
    HealthStatus,
    InsightCategory,
    InsightImpact,
    RecommendationPriority,
)
from goat.intelligence.core.models import (
    InstitutionalRecommendation,
    IntelligenceSummary,
    MetaAnalysis,
    ResearchHealth,
    ResearchInsight,
)
from goat.intelligence.reporting.reports import IntelligenceReportGenerator
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_intelligence_reporting_generator(index_type: SyntheticIndexType) -> None:
    reporter = IntelligenceReportGenerator()

    i_id, i_hash = compute_research_insight_id("HYPOTHESIS_SUCCESS", "Top Category", "HIGH")
    insight = ResearchInsight(
        insight_id=i_id,
        category=InsightCategory.HYPOTHESIS_SUCCESS,
        impact=InsightImpact.HIGH,
        title="Top Category",
        findings_statement=f"Findings statement for {index_type.value}",
        confidence_level=0.95,
        supporting_data={"sym": index_type.value},
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=i_hash,
    )

    m_id, m_hash = compute_meta_analysis_id("Meta Study", 10, "2026-01-01T00:00:00Z")
    meta = MetaAnalysis(
        meta_analysis_id=m_id,
        analysis_title="Meta Study",
        sample_size=10,
        pooled_effect_size=0.15,
        heterogeneity_i2=10.0,
        p_value=0.01,
        key_findings=["Finding 1"],
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=m_hash,
    )

    h_id, h_hash = compute_research_health_id("EXCELLENT", 90.0, "2026-01-01T00:00:00Z")
    health = ResearchHealth(
        health_id=h_id,
        health_score=90.0,
        status=HealthStatus.EXCELLENT,
        success_rate=0.80,
        efficiency_score=95.0,
        waste_percentage=10.0,
        diagnostics=["Diag 1"],
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=h_hash,
    )

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

    ins_rep = reporter.generate_insight_report(insight)
    meta_rep = reporter.generate_meta_analysis_report(meta)
    health_rep = reporter.generate_research_health_report(health)
    exec_rep = reporter.generate_executive_report(summary)

    assert "# INSTITUTIONAL RESEARCH INSIGHT REPORT" in ins_rep
    assert "# INSTITUTIONAL META-ANALYSIS REPORT" in meta_rep
    assert "# INSTITUTIONAL RESEARCH HEALTH REPORT" in health_rep
    assert "# INSTITUTIONAL RESEARCH INTELLIGENCE EXECUTIVE REPORT" in exec_rep

    json_str = reporter.export_canonical_json(insight)
    data = json.loads(json_str)
    assert data["insight_id"] == insight.insight_id
    assert data["canonical_hash"] == insight.canonical_hash
