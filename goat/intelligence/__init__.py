"""
Project GOAT v0.9 — Institutional Research Intelligence & Meta-Analysis Engine Package
"""

from goat.intelligence.analytics.engine import ResearchAnalyticsEngine
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
from goat.intelligence.engine import MasterIntelligenceEngine
from goat.intelligence.insights.engine import InsightEngine
from goat.intelligence.meta.engine import MetaAnalysisEngine
from goat.intelligence.persistence.sqlite import (
    HealthRepository,
    InsightRepository,
    IntelligencePersistenceContext,
    MetaAnalysisRepository,
    RecommendationRepository,
    SummaryRepository,
    TrendRepository,
)
from goat.intelligence.recommendations.engine import RecommendationEngine
from goat.intelligence.reporting.reports import IntelligenceReportGenerator

__all__ = [
    # Enums
    "InsightCategory",
    "InsightImpact",
    "TrendDirection",
    "RecommendationPriority",
    "HealthStatus",
    # Domain Models
    "ResearchInsight",
    "MetaAnalysis",
    "ResearchTrend",
    "InstitutionalRecommendation",
    "ResearchHealth",
    "IntelligenceSummary",
    # Canonical Utilities
    "serialize_canonical_json",
    "compute_canonical_sha256",
    "compute_research_insight_id",
    "compute_meta_analysis_id",
    "compute_research_trend_id",
    "compute_institutional_recommendation_id",
    "compute_research_health_id",
    "compute_intelligence_summary_id",
    # Sub-Engines
    "ResearchAnalyticsEngine",
    "MetaAnalysisEngine",
    "InsightEngine",
    "RecommendationEngine",
    "MasterIntelligenceEngine",
    # Reporting & Persistence
    "IntelligenceReportGenerator",
    "InsightRepository",
    "MetaAnalysisRepository",
    "TrendRepository",
    "RecommendationRepository",
    "HealthRepository",
    "SummaryRepository",
    "IntelligencePersistenceContext",
]
