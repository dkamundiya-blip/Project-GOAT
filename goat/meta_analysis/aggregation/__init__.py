"""
Project GOAT v0.7 — Meta-Analysis Aggregation Package
"""

from goat.meta_analysis.aggregation.intelligence import ResearchIntelligenceEngine
from goat.meta_analysis.aggregation.summary import ScientificSummaryEngine
from goat.meta_analysis.aggregation.trends import TrendAnalysisEngine

__all__ = [
    "TrendAnalysisEngine",
    "ResearchIntelligenceEngine",
    "ScientificSummaryEngine",
]
