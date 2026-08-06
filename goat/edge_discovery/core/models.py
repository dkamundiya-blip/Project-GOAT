"""
Project GOAT v0.9 — Immutable Pydantic V2 Domain Models for Edge Discovery Subsystem
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.edge_discovery.core.enums import (
    EdgeCategory,
    NoveltyStatus,
    PatternType,
    QualityTier,
    RejectionReason,
    ValidationStatus,
)


class EdgePattern(BaseModel):
    """Immutable Discovered Recurring Statistical Pattern."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    pattern_id: str = Field(..., description="Deterministic pattern ID with prefix EPT_")
    pattern_type: PatternType = Field(..., description="Classification of statistical pattern")
    symbol: str = Field(..., description="Target symbol identifier")
    sample_size: int = Field(..., ge=1, description="Number of observed historical occurrences")
    effect_size: float = Field(..., description="Measured statistical effect size")
    statistical_significance: float = Field(..., ge=0.0, le=1.0, description="P-value or confidence measure")
    regime_consistency: float = Field(..., ge=0.0, le=1.0, description="Cross-regime consistency ratio")
    observation_ids: list[str] = Field(default_factory=list, description="Associated microstructure observation IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class PatternCluster(BaseModel):
    """Immutable Cluster of Similar Edge Patterns."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    cluster_id: str = Field(..., description="Deterministic cluster ID with prefix CLS_")
    cluster_name: str = Field(..., description="Descriptive name of cluster")
    pattern_ids: list[str] = Field(..., min_length=1, description="List of grouped pattern IDs")
    centroid_pattern_id: str = Field(..., description="Pattern ID representing cluster centroid")
    intra_cluster_similarity: float = Field(..., ge=0.0, le=1.0, description="Mean similarity within cluster")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class NoveltyAssessment(BaseModel):
    """Immutable Novelty Assessment of Discovered Edge Candidate."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    assessment_id: str = Field(..., description="Deterministic assessment ID with prefix NOV_")
    candidate_id: str = Field(..., description="Assessed candidate ID")
    max_similarity_score: float = Field(..., ge=0.0, le=1.0, description="Maximum similarity to archived edges")
    closest_archived_edge_id: str | None = Field(default=None, description="ID of most similar archived edge")
    status: NoveltyStatus = Field(..., description="Novelty status classification")
    is_novel: bool = Field(..., description="Boolean indicating if candidate passes novelty filter")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class EdgeScore(BaseModel):
    """Immutable Quality Score for Candidate Edge."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    score_id: str = Field(..., description="Deterministic score ID with prefix SCR_")
    candidate_id: str = Field(..., description="Scored candidate edge ID")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Composite institutional quality score 0..100")
    support_score: float = Field(..., ge=0.0, le=100.0, description="Sample size & observation support score")
    stability_score: float = Field(..., ge=0.0, le=100.0, description="Statistical stability score")
    consistency_score: float = Field(..., ge=0.0, le=100.0, description="Regime consistency score")
    robustness_score: float = Field(..., ge=0.0, le=100.0, description="Cross-regime robustness score")
    live_compatibility_score: float = Field(..., ge=0.0, le=100.0, description="Live validation compatibility")
    quality_tier: QualityTier = Field(..., description="Classified quality tier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class EdgeCandidate(BaseModel):
    """Immutable Candidate Quantitative Edge Discovered by Mining Engine."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate_id: str = Field(..., description="Deterministic candidate ID with prefix EDC_")
    name: str = Field(..., description="Descriptive name of quantitative candidate edge")
    category: EdgeCategory = Field(..., description="Category classification of quantitative edge")
    symbol: str = Field(..., description="Target asset or synthetic index symbol")
    pattern_ids: list[str] = Field(..., min_length=1, description="Associated statistical pattern IDs")
    hypothesis_statement: str = Field(..., description="Scientific proposition statement")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Statistical confidence level")
    observation_count: int = Field(..., ge=1, description="Total supporting observations count")
    timestamp: str = Field(..., description="ISO-8601 discovery timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class DiscoveryDecision(BaseModel):
    """Immutable Protocol Validation Decision for Candidate Edge."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(..., description="Deterministic decision ID with prefix DSC_")
    candidate_id: str = Field(..., description="Evaluated candidate edge ID")
    status: ValidationStatus = Field(..., description="Validation outcome status")
    rejection_reason: RejectionReason = Field(default=RejectionReason.NONE, description="Rejection reason if rejected")
    novelty_assessment_id: str = Field(..., description="Referenced NoveltyAssessment ID")
    score_id: str = Field(..., description="Referenced EdgeScore ID")
    timestamp: str = Field(..., description="ISO-8601 decision timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class DiscoverySummary(BaseModel):
    """Immutable Executive Summary of Quantitative Edge Discovery Run."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(..., description="Deterministic summary ID with prefix DSM_")
    timestamp: str = Field(..., description="ISO-8601 summary timestamp")
    total_patterns: int = Field(default=0, ge=0, description="Total mined patterns")
    total_clusters: int = Field(default=0, ge=0, description="Total pattern clusters")
    total_candidates: int = Field(default=0, ge=0, description="Total candidate edges discovered")
    total_validated: int = Field(default=0, ge=0, description="Total edges passing validation protocol")
    total_rejected: int = Field(default=0, ge=0, description="Total rejected candidate edges")
    category_counts: dict[str, int] = Field(default_factory=dict, description="Candidate count breakdown by category")
    tier_counts: dict[str, int] = Field(default_factory=dict, description="Validated edge count breakdown by tier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")
