"""
Project GOAT v0.9 — Institutional Research Intelligence Enums
"""

from enum import Enum


class InsightCategory(str, Enum):
    """Classification of Institutional Research Insights."""
    HYPOTHESIS_SUCCESS = "HYPOTHESIS_SUCCESS"
    EXPERIMENT_EFFICIENCY = "EXPERIMENT_EFFICIENCY"
    REGIME_INVALIDATION = "REGIME_INVALIDATION"
    EVIDENCE_PREDICTIVITY = "EVIDENCE_PREDICTIVITY"
    RESEARCH_WASTE = "RESEARCH_WASTE"
    EDGE_LONGEVITY = "EDGE_LONGEVITY"


class InsightImpact(str, Enum):
    """Severity or Impact Level of Research Insight."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TrendDirection(str, Enum):
    """Directional Trend of Research Productivity / Health."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    VOLATILE = "VOLATILE"


class RecommendationPriority(str, Enum):
    """Scientific Research Recommendation Priority Tier."""
    P1_URGENT = "P1_URGENT"
    P2_HIGH = "P2_HIGH"
    P3_MEDIUM = "P3_MEDIUM"
    P4_LOW = "P4_LOW"


class HealthStatus(str, Enum):
    """Institutional Research Health Classification."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MARGINAL = "MARGINAL"
    AT_RISK = "AT_RISK"
