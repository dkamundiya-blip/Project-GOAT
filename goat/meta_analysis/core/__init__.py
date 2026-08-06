"""
Project GOAT v0.7 — Meta-Analysis Core Package
"""

from goat.meta_analysis.core.canonical import (
    compute_cluster_id,
    compute_meta_analysis_id,
    compute_metrics_id,
    compute_pattern_id,
    compute_summary_id,
    compute_trend_id,
    serialize_canonical_json,
)
from goat.meta_analysis.core.enums import (
    ClusterType,
    PatternCategory,
    ResearchDomainStatus,
    TrendDirection,
)
from goat.meta_analysis.core.models import (
    MetaAnalysisResult,
    ResearchCluster,
    ResearchIntelligenceMetrics,
    ResearchPattern,
    ResearchTrend,
    ScientificSummary,
)

__all__ = [
    "ClusterType",
    "PatternCategory",
    "TrendDirection",
    "ResearchDomainStatus",
    "ResearchCluster",
    "ResearchPattern",
    "ResearchTrend",
    "ScientificSummary",
    "ResearchIntelligenceMetrics",
    "MetaAnalysisResult",
    "compute_cluster_id",
    "compute_pattern_id",
    "compute_trend_id",
    "compute_summary_id",
    "compute_metrics_id",
    "compute_meta_analysis_id",
    "serialize_canonical_json",
]
