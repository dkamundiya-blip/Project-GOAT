"""
Project GOAT v0.7 — Scientific Meta-Analysis & Research Intelligence Engine Package

Public API Exports for Step 5.9.
"""

from goat.meta_analysis.aggregation import (
    ResearchIntelligenceEngine,
    ScientificSummaryEngine,
    TrendAnalysisEngine,
)
from goat.meta_analysis.clustering import ClusterEngine
from goat.meta_analysis.core import (
    ClusterType,
    MetaAnalysisResult,
    PatternCategory,
    ResearchCluster,
    ResearchDomainStatus,
    ResearchIntelligenceMetrics,
    ResearchPattern,
    ResearchTrend,
    ScientificSummary,
    TrendDirection,
    compute_cluster_id,
    compute_meta_analysis_id,
    compute_metrics_id,
    compute_pattern_id,
    compute_summary_id,
    compute_trend_id,
    serialize_canonical_json,
)
from goat.meta_analysis.engine import ScientificMetaAnalysisEngine
from goat.meta_analysis.patterns import PatternDiscoveryEngine
from goat.meta_analysis.persistence import (
    ClusterRepository,
    MetaAnalysisRepository,
    PatternRepository,
    ReportRepository,
    SummaryRepository,
    TrendRepository,
    init_meta_analysis_db,
)
from goat.meta_analysis.reporting import (
    MetaAnalysisReport,
    ResearchClusterReport,
    ResearchPatternReport,
    ResearchTrendReport,
    ScientificSummaryReport,
)

__all__ = [
    # Core Models & Enums
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
    # Identifiers & Canonical Hashing
    "compute_cluster_id",
    "compute_pattern_id",
    "compute_trend_id",
    "compute_summary_id",
    "compute_metrics_id",
    "compute_meta_analysis_id",
    "serialize_canonical_json",
    # Meta-Analysis Engine & Coordinators
    "ScientificMetaAnalysisEngine",
    "ClusterEngine",
    "PatternDiscoveryEngine",
    "TrendAnalysisEngine",
    "ResearchIntelligenceEngine",
    "ScientificSummaryEngine",
    # Reports
    "MetaAnalysisReport",
    "ResearchClusterReport",
    "ResearchPatternReport",
    "ResearchTrendReport",
    "ScientificSummaryReport",
    # Repositories & Database
    "init_meta_analysis_db",
    "ClusterRepository",
    "PatternRepository",
    "TrendRepository",
    "SummaryRepository",
    "MetaAnalysisRepository",
    "ReportRepository",
]
