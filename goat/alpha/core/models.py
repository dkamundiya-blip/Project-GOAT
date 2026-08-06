"""
Project GOAT v0.7 — Core Immutable Models for Scientific Alpha & Quantitative Edge Engine

Defines immutable Pydantic domain models:
- ScientificEdge (SED_<HEX16>)
- EdgeEvidence (EEV_<HEX16>)
- EdgeScore (ESC_<HEX16>)
- EdgeRanking (ERK_<HEX16>)
- EdgeExplainabilityRecord (EEX_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.alpha.core.enums import EdgeMaturity, EvidenceSourceType


class ScientificEdge(BaseModel):
    """Immutable model representing a candidate quantitative market edge."""

    edge_id: str = Field(
        ...,
        description="Unique edge ID formatted as SED_<HEX16>",
        pattern=r"^SED_[A-Fa-f0-9]{16}$",
    )
    title: str = Field(..., description="Descriptive title of the edge")
    description: str = Field(default="", description="Detailed narrative description")
    maturity: EdgeMaturity = Field(default=EdgeMaturity.NEW, description="Edge maturity classification stage")
    originating_hypotheses: list[str] = Field(default_factory=list, description="IDs of originating hypotheses")
    originating_validations: list[str] = Field(default_factory=list, description="IDs of originating validation runs")
    originating_clusters: list[str] = Field(default_factory=list, description="IDs of originating ResearchClusters")
    originating_patterns: list[str] = Field(default_factory=list, description="IDs of originating ResearchPatterns")
    originating_trends: list[str] = Field(default_factory=list, description="IDs of originating ResearchTrends")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence rating (0.0 to 1.0)")
    reproducibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Reproducibility rating (0.0 to 1.0)")
    robustness: float = Field(default=0.0, ge=0.0, le=1.0, description="Robustness rating (0.0 to 1.0)")
    stability: float = Field(default=0.0, ge=0.0, le=1.0, description="Stability rating (0.0 to 1.0)")
    discovery_timestamp: str = Field(..., description="ISO 8601 UTC discovery timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class EdgeEvidence(BaseModel):
    """Immutable model representing a scientific observation supporting an edge."""

    evidence_id: str = Field(
        ...,
        description="Unique edge evidence ID formatted as EEV_<HEX16>",
        pattern=r"^EEV_[A-Fa-f0-9]{16}$",
    )
    edge_id: str = Field(..., description="Target ScientificEdge ID (SED_<HEX16>)")
    source_type: EvidenceSourceType = Field(..., description="Evidence source type classification")
    source_reference: str = Field(..., description="Reference ID or identifier of the evidence source")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence confidence rating")
    reproducibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence reproducibility rating")
    explanation: str = Field(default="", description="Narrative explanation of how source supports edge")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class EdgeScore(BaseModel):
    """Immutable model containing multi-dimensional scoring for a candidate edge."""

    score_id: str = Field(
        ...,
        description="Unique score ID formatted as ESC_<HEX16>",
        pattern=r"^ESC_[A-Fa-f0-9]{16}$",
    )
    edge_id: str = Field(..., description="Target ScientificEdge ID (SED_<HEX16>)")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Scientific confidence rating")
    reproducibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Empirical reproducibility rating")
    robustness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Robustness rating")
    stability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Stability rating")
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence strength rating")
    scientific_quality: float = Field(default=0.0, ge=0.0, le=1.0, description="Scientific quality score")
    longevity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Longevity rating")
    conflict_penalty: float = Field(default=0.0, ge=0.0, le=1.0, description="Conflict penalty deduction")
    overall_edge_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Final aggregated overall edge quality score")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class EdgeRanking(BaseModel):
    """Immutable model representing deterministic ranking of candidate edges."""

    ranking_id: str = Field(
        ...,
        description="Unique ranking ID formatted as ERK_<HEX16>",
        pattern=r"^ERK_[A-Fa-f0-9]{16}$",
    )
    ranked_edges: list[str] = Field(default_factory=list, description="IDs of ScientificEdges in rank order")
    edge_scores: list[EdgeScore] = Field(default_factory=list, description="List of component EdgeScore objects")
    ranking_timestamp: str = Field(..., description="ISO 8601 UTC ranking timestamp")
    ranking_rules: list[str] = Field(default_factory=list, description="List of ranking rules applied")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class EdgeExplainabilityRecord(BaseModel):
    """Immutable model establishing complete scientific traceability for an edge."""

    explanation_id: str = Field(
        ...,
        description="Unique explanation ID formatted as EEX_<HEX16>",
        pattern=r"^EEX_[A-Fa-f0-9]{16}$",
    )
    edge_id: str = Field(..., description="Target ScientificEdge ID (SED_<HEX16>)")
    origin: str = Field(..., description="Primary originating domain or hypothesis ID")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    supporting_hypotheses: list[str] = Field(default_factory=list, description="IDs of supporting hypotheses")
    supporting_experiments: list[str] = Field(default_factory=list, description="IDs of supporting experiments")
    supporting_studies: list[str] = Field(default_factory=list, description="IDs of supporting studies")
    supporting_clusters: list[str] = Field(default_factory=list, description="IDs of supporting ResearchClusters")
    supporting_trends: list[str] = Field(default_factory=list, description="IDs of supporting ResearchTrends")
    supporting_reports: list[str] = Field(default_factory=list, description="IDs of supporting reports")
    scientific_explanation: str = Field(..., description="Narrative scientific explanation")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
