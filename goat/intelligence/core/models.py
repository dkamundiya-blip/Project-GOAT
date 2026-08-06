"""
Project GOAT v0.9 — Immutable Pydantic V2 Domain Models for Institutional Research Intelligence Subsystem
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.intelligence.core.enums import (
    HealthStatus,
    InsightCategory,
    InsightImpact,
    RecommendationPriority,
    TrendDirection,
)


class ResearchInsight(BaseModel):
    """Immutable Explainable Institutional Research Insight."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    insight_id: str = Field(..., description="Deterministic insight ID with prefix RIN_")
    category: InsightCategory = Field(..., description="Classification of research insight")
    impact: InsightImpact = Field(..., description="Severity / impact tier")
    title: str = Field(..., description="Short descriptive title of insight")
    findings_statement: str = Field(..., description="Full explainable scientific findings statement")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Statistical confidence in insight")
    supporting_data: dict[str, Any] = Field(default_factory=dict, description="Supporting empirical metrics")
    timestamp: str = Field(..., description="ISO-8601 timestamp of insight generation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class MetaAnalysis(BaseModel):
    """Immutable Meta-Analysis Container for Higher-Order Research Patterns."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    meta_analysis_id: str = Field(..., description="Deterministic meta-analysis ID with prefix MTA_")
    analysis_title: str = Field(..., description="Descriptive title of meta-analysis study")
    sample_size: int = Field(..., ge=0, description="Total completed studies / experiments analyzed")
    pooled_effect_size: float = Field(..., description="Pooled meta-analysis effect size")
    heterogeneity_i2: float = Field(..., ge=0.0, le=100.0, description="I2 heterogeneity index percentage")
    p_value: float = Field(..., ge=0.0, le=1.0, description="Meta-analytic statistical significance")
    key_findings: list[str] = Field(default_factory=list, description="Extracted higher-order findings")
    timestamp: str = Field(..., description="ISO-8601 creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class ResearchTrend(BaseModel):
    """Immutable Research Productivity / Efficiency Trend."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    trend_id: str = Field(..., description="Deterministic trend ID with prefix TRD_")
    metric_name: str = Field(..., description="Name of tracked research metric (e.g. hypothesis_pass_rate)")
    direction: TrendDirection = Field(..., description="Directional movement of metric")
    historical_values: list[float] = Field(default_factory=list, description="Historical trajectory data points")
    percentage_change: float = Field(..., description="Percentage change over historical period")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class InstitutionalRecommendation(BaseModel):
    """Immutable Recommendation for Future Scientific Research Priorities."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    recommendation_id: str = Field(..., description="Deterministic recommendation ID with prefix REC_")
    priority: RecommendationPriority = Field(..., description="Research priority tier")
    topic: str = Field(..., description="Target scientific research topic / domain")
    rationale: str = Field(..., description="Scientific rationale explaining why this research should be prioritized")
    expected_utility: float = Field(..., ge=0.0, le=100.0, description="Estimated research utility score")
    timestamp: str = Field(..., description="ISO-8601 creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class ResearchHealth(BaseModel):
    """Immutable Overall Institutional Research Health Assessment."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    health_id: str = Field(..., description="Deterministic health ID with prefix RHL_")
    health_score: float = Field(..., ge=0.0, le=100.0, description="Overall institutional research health score (0..100)")
    status: HealthStatus = Field(..., description="Research health status tier")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Aggregate hypothesis success rate")
    efficiency_score: float = Field(..., ge=0.0, le=100.0, description="Experiment efficiency score")
    waste_percentage: float = Field(..., ge=0.0, le=100.0, description="Estimated research time waste percentage")
    diagnostics: list[str] = Field(default_factory=list, description="Diagnostic statements")
    timestamp: str = Field(..., description="ISO-8601 assessment timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class IntelligenceSummary(BaseModel):
    """Immutable Executive Summary of Institutional Research Intelligence."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(..., description="Deterministic summary ID with prefix ISM_")
    timestamp: str = Field(..., description="ISO-8601 summary timestamp")
    total_insights: int = Field(default=0, ge=0, description="Total research insights generated")
    total_meta_analyses: int = Field(default=0, ge=0, description="Total meta-analyses performed")
    total_recommendations: int = Field(default=0, ge=0, description="Total scientific research recommendations")
    overall_health_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Current institutional research health score")
    insights_by_category: dict[str, int] = Field(default_factory=dict, description="Insight counts by InsightCategory")
    recommendations_by_priority: dict[str, int] = Field(default_factory=dict, description="Recommendation counts by priority")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")
