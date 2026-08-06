"""
Project GOAT v0.7 — Core Immutable Models for Meta-Analysis & Research Intelligence Engine

Defines immutable Pydantic domain models:
- ResearchCluster (RCL_<HEX16>)
- ResearchPattern (RPT_<HEX16>)
- ResearchTrend (RTD_<HEX16>)
- ScientificSummary (SCS_<HEX16>)
- ResearchIntelligenceMetrics (RIM_<HEX16>)
- MetaAnalysisResult (MAR_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.meta_analysis.core.enums import ClusterType, PatternCategory, TrendDirection


class ResearchCluster(BaseModel):
    """Immutable representation of a deterministic scientific research cluster."""

    cluster_id: str = Field(
        ...,
        description="Unique cluster ID formatted as RCL_<HEX16>",
        pattern=r"^RCL_[A-Fa-f0-9]{16}$",
    )
    title: str = Field(..., description="Descriptive title of cluster")
    description: str = Field(default="", description="Narrative summary")
    cluster_type: ClusterType = Field(default=ClusterType.THEME, description="Type of clustering applied")
    participating_nodes: list[str] = Field(default_factory=list, description="IDs of participating KnowledgeNodes")
    participating_validations: list[str] = Field(default_factory=list, description="IDs of participating validation runs")
    participating_hypotheses: list[str] = Field(default_factory=list, description="IDs of participating hypotheses")
    participating_experiments: list[str] = Field(default_factory=list, description="IDs of participating experiments")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Cluster confidence score (0.0 to 1.0)")
    reproducibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Cluster reproducibility rating (0.0 to 1.0)")
    consistency: float = Field(default=0.0, ge=0.0, le=1.0, description="Internal consistency rating (0.0 to 1.0)")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ResearchPattern(BaseModel):
    """Immutable representation of a discovered recurring scientific pattern."""

    pattern_id: str = Field(
        ...,
        description="Unique pattern ID formatted as RPT_<HEX16>",
        pattern=r"^RPT_[A-Fa-f0-9]{16}$",
    )
    pattern_name: str = Field(..., description="Descriptive name of pattern")
    description: str = Field(default="", description="Detailed narrative description")
    category: PatternCategory = Field(default=PatternCategory.RECURRING_EVIDENCE, description="Pattern category")
    evidence: list[str] = Field(default_factory=list, description="List of supporting evidence artifact IDs")
    frequency: int = Field(default=1, ge=1, description="Observed recurrence frequency count")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence rating")
    supporting_clusters: list[str] = Field(default_factory=list, description="IDs of supporting ResearchClusters")
    supporting_validations: list[str] = Field(default_factory=list, description="IDs of supporting validation runs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ResearchTrend(BaseModel):
    """Immutable representation of a scientific research trend."""

    trend_id: str = Field(
        ...,
        description="Unique trend ID formatted as RTD_<HEX16>",
        pattern=r"^RTD_[A-Fa-f0-9]{16}$",
    )
    topic: str = Field(..., description="Research topic / domain name")
    direction: TrendDirection = Field(..., description="Trend direction classification")
    strength: float = Field(default=0.0, ge=0.0, le=1.0, description="Trend strength rating (0.0 to 1.0)")
    persistence: float = Field(default=0.0, ge=0.0, le=1.0, description="Trend persistence score (0.0 to 1.0)")
    evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ScientificSummary(BaseModel):
    """Immutable executive scientific summary of meta-analysis findings."""

    summary_id: str = Field(
        ...,
        description="Unique summary ID formatted as SCS_<HEX16>",
        pattern=r"^SCS_[A-Fa-f0-9]{16}$",
    )
    validated_knowledge_count: int = Field(default=0, ge=0, description="Count of validated knowledge nodes")
    integrated_knowledge_count: int = Field(default=0, ge=0, description="Count of integrated knowledge objects")
    conflict_count: int = Field(default=0, ge=0, description="Count of detected conflicts")
    cluster_count: int = Field(default=0, ge=0, description="Count of research clusters")
    pattern_count: int = Field(default=0, ge=0, description="Count of discovered patterns")
    trend_count: int = Field(default=0, ge=0, description="Count of active research trends")
    strongest_research_areas: list[str] = Field(default_factory=list, description="List of strongest research areas")
    weakest_research_areas: list[str] = Field(default_factory=list, description="List of weakest research areas")
    outstanding_contradictions: list[str] = Field(default_factory=list, description="IDs of unresolved conflicts")
    future_investigation_recommendations: list[str] = Field(default_factory=list, description="Recommended next steps")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ResearchIntelligenceMetrics(BaseModel):
    """Immutable set of research intelligence metrics."""

    metrics_id: str = Field(
        ...,
        description="Unique metrics ID formatted as RIM_<HEX16>",
        pattern=r"^RIM_[A-Fa-f0-9]{16}$",
    )
    knowledge_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Knowledge density metric")
    evidence_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence density metric")
    validation_stability: float = Field(default=0.0, ge=0.0, le=1.0, description="Validation stability rating")
    consensus_stability: float = Field(default=0.0, ge=0.0, le=1.0, description="Consensus stability rating")
    research_breadth: float = Field(default=0.0, ge=0.0, description="Research domain breadth score")
    research_depth: float = Field(default=0.0, ge=0.0, description="Research structural depth score")
    knowledge_maturity: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall knowledge maturity rating")
    scientific_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall scientific confidence rating")
    timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class MetaAnalysisResult(BaseModel):
    """Immutable root result of a scientific meta-analysis execution."""

    analysis_id: str = Field(
        ...,
        description="Unique meta-analysis result ID formatted as MAR_<HEX16>",
        pattern=r"^MAR_[A-Fa-f0-9]{16}$",
    )
    analyzed_knowledge_states: list[str] = Field(default_factory=list, description="IDs of analyzed knowledge objects/versions")
    clusters: list[ResearchCluster] = Field(default_factory=list, description="List of generated ResearchClusters")
    patterns: list[ResearchPattern] = Field(default_factory=list, description="List of discovered ResearchPatterns")
    trends: list[ResearchTrend] = Field(default_factory=list, description="List of generated ResearchTrends")
    contradictions: list[dict[str, Any]] = Field(default_factory=list, description="List of contradiction summaries")
    scientific_summary: ScientificSummary = Field(..., description="Executive ScientificSummary model")
    intelligence_metrics: ResearchIntelligenceMetrics = Field(..., description="ResearchIntelligenceMetrics model")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall meta-analysis confidence rating")
    reproducibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall meta-analysis reproducibility rating")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
