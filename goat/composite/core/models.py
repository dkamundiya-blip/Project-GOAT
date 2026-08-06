"""
Project GOAT v0.7 — Core Immutable Models for Composite Edge Synthesis Engine

Defines immutable Pydantic domain models:
- CompositeEdge (CMP_<HEX16>)
- CompositeEvidence (CEV_<HEX16>)
- CompositeScore (CSC_<HEX16>)
- CompositeRanking (CRK_<HEX16>)
- CompositeExplainabilityRecord (CEX_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class CompositeEdge(BaseModel):
    """Immutable model representing a synthesized composite quantitative market edge."""

    composite_id: str = Field(
        ...,
        description="Unique composite ID formatted as CMP_<HEX16>",
        pattern=r"^CMP_[A-Fa-f0-9]{16}$",
    )
    title: str = Field(..., description="Descriptive title of the composite edge")
    description: str = Field(default="", description="Detailed narrative description")
    participating_edges: list[str] = Field(default_factory=list, description="IDs of participating ScientificEdges (SED_<HEX16>)")
    participating_hypotheses: list[str] = Field(default_factory=list, description="IDs of originating hypotheses")
    participating_validations: list[str] = Field(default_factory=list, description="IDs of participating validation runs")
    participating_clusters: list[str] = Field(default_factory=list, description="IDs of participating ResearchClusters")
    participating_patterns: list[str] = Field(default_factory=list, description="IDs of participating ResearchPatterns")
    participating_regimes: list[str] = Field(default_factory=list, description="IDs of compatible MarketRegimes")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class CompositeEvidence(BaseModel):
    """Immutable model representing an evidence artifact supporting a CompositeEdge."""

    evidence_id: str = Field(
        ...,
        description="Unique composite evidence ID formatted as CEV_<HEX16>",
        pattern=r"^CEV_[A-Fa-f0-9]{16}$",
    )
    composite_id: str = Field(..., description="Target CompositeEdge ID (CMP_<HEX16>)")
    contributing_edge: str = Field(..., description="Source ScientificEdge ID (SED_<HEX16>)")
    contribution_strength: float = Field(default=0.0, ge=0.0, le=1.0, description="Contribution strength rating (0.0 to 1.0)")
    explanation: str = Field(default="", description="Narrative explanation of evidence contribution")
    supporting_sources: list[str] = Field(default_factory=list, description="IDs of supporting source artifacts")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class CompositeScore(BaseModel):
    """Immutable model containing multi-dimensional synergy and quality scoring for a CompositeEdge."""

    score_id: str = Field(
        ...,
        description="Unique composite score ID formatted as CSC_<HEX16>",
        pattern=r"^CSC_[A-Fa-f0-9]{16}$",
    )
    composite_id: str = Field(..., description="Target CompositeEdge ID (CMP_<HEX16>)")
    synergy_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Knowledge reinforcement synergy score")
    robustness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Structural robustness score")
    stability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Historical stability score")
    diversity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence diversity & breadth score")
    conflict_penalty: float = Field(default=0.0, ge=0.0, le=1.0, description="Conflict penalty deduction")
    explainability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Scientific explainability score")
    reproducibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Empirical reproducibility score")
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Aggregated overall composite quality score")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class CompositeRanking(BaseModel):
    """Immutable model representing deterministic ranking of CompositeEdges."""

    ranking_id: str = Field(
        ...,
        description="Unique ranking ID formatted as CRK_<HEX16>",
        pattern=r"^CRK_[A-Fa-f0-9]{16}$",
    )
    ranked_composites: list[str] = Field(default_factory=list, description="IDs of CompositeEdges in rank order")
    composite_scores: list[CompositeScore] = Field(default_factory=list, description="List of component CompositeScore objects")
    ranking_timestamp: str = Field(..., description="ISO 8601 UTC ranking timestamp")
    ranking_rules: list[str] = Field(default_factory=list, description="List of ranking rules applied")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class CompositeExplainabilityRecord(BaseModel):
    """Immutable model providing 100% scientific traceability for composite edge synthesis."""

    explanation_id: str = Field(
        ...,
        description="Unique explanation ID formatted as CEX_<HEX16>",
        pattern=r"^CEX_[A-Fa-f0-9]{16}$",
    )
    composite_id: str = Field(..., description="Target CompositeEdge ID (CMP_<HEX16>)")
    participating_edges: list[str] = Field(default_factory=list, description="IDs of participating ScientificEdges")
    supporting_hypotheses: list[str] = Field(default_factory=list, description="IDs of supporting hypotheses")
    supporting_validations: list[str] = Field(default_factory=list, description="IDs of supporting validation runs")
    supporting_knowledge: list[str] = Field(default_factory=list, description="IDs of supporting IntegratedKnowledge models")
    supporting_trends: list[str] = Field(default_factory=list, description="IDs of supporting ResearchTrends")
    supporting_regimes: list[str] = Field(default_factory=list, description="IDs of compatible MarketRegimes")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    scientific_explanation: str = Field(..., description="Primary narrative scientific explanation")
    compatibility_explanation: str = Field(default="", description="Explanation of edge compatibility and reinforcement")
    conflict_explanation: str = Field(default="", description="Explanation of conflict evaluation and resolution")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
