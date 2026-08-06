"""
Project GOAT v0.9 — Research Intelligence Core Package
"""

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

__all__ = [
    "HealthStatus",
    "InsightCategory",
    "InsightImpact",
    "InstitutionalRecommendation",
    "IntelligenceSummary",
    "MetaAnalysis",
    "RecommendationPriority",
    "ResearchHealth",
    "ResearchInsight",
    "ResearchTrend",
    "TrendDirection",
    "compute_canonical_sha256",
    "compute_institutional_recommendation_id",
    "compute_intelligence_summary_id",
    "compute_meta_analysis_id",
    "compute_research_health_id",
    "compute_research_insight_id",
    "compute_research_trend_id",
    "serialize_canonical_json",
]
