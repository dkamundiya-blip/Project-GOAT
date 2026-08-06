"""
Project GOAT v0.7 — Core Immutable Models for Market Regime Classification & Edge Applicability Engine

Defines immutable Pydantic domain models:
- MarketRegime (MRG_<HEX16>)
- ApplicabilityAssessment (APA_<HEX16>)
- RegimeRule (RGR_<HEX16>)
- ApplicabilityDecision (APD_<HEX16>)
- RegimeExplainabilityRecord (REX_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.regimes.core.enums import (
    EdgeActivationState,
    LiquidityState,
    ParticipationState,
    RegimeType,
    StructuralState,
    TrendState,
    VolatilityState,
)


class MarketRegime(BaseModel):
    """Immutable model representing a deterministic market regime classification."""

    regime_id: str = Field(
        ...,
        description="Unique regime ID formatted as MRG_<HEX16>",
        pattern=r"^MRG_[A-Fa-f0-9]{16}$",
    )
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    regime_type: RegimeType = Field(..., description="Primary market regime classification")
    volatility_state: VolatilityState = Field(default=VolatilityState.NORMAL, description="Volatility state classification")
    liquidity_state: LiquidityState = Field(default=LiquidityState.NORMAL, description="Liquidity state classification")
    participation_state: ParticipationState = Field(default=ParticipationState.BALANCED, description="Market participant classification")
    trend_state: TrendState = Field(default=TrendState.NEUTRAL, description="Trend direction state")
    momentum_state: str = Field(default="FLAT", description="Momentum acceleration state ('ACCELERATING', 'DECELERATING', 'FLAT')")
    structural_state: StructuralState = Field(default=StructuralState.CONSOLIDATION, description="Market structure state")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Classification confidence rating (0.0 to 1.0)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class RegimeRule(BaseModel):
    """Immutable model representing a deterministic regime classification rule."""

    rule_id: str = Field(
        ...,
        description="Unique rule ID formatted as RGR_<HEX16>",
        pattern=r"^RGR_[A-Fa-f0-9]{16}$",
    )
    name: str = Field(..., description="Descriptive name of rule")
    description: str = Field(default="", description="Detailed narrative description")
    priority: int = Field(default=50, ge=1, le=100, description="Rule evaluation priority (1-100)")
    deterministic_conditions: dict[str, Any] = Field(default_factory=dict, description="Deterministic metric conditions")
    expected_regime: RegimeType = Field(..., description="Regime type assigned when rule conditions match")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ApplicabilityAssessment(BaseModel):
    """Immutable model representing edge applicability assessment in a specific regime."""

    assessment_id: str = Field(
        ...,
        description="Unique assessment ID formatted as APA_<HEX16>",
        pattern=r"^APA_[A-Fa-f0-9]{16}$",
    )
    edge_id: str = Field(..., description="Target ScientificEdge ID (SED_<HEX16>)")
    regime_id: str = Field(..., description="Target MarketRegime ID (MRG_<HEX16>)")
    applicability: EdgeActivationState = Field(..., description="Assigned activation state")
    applicability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Applicability compatibility score (0.0 to 1.0)")
    activation_reason: str = Field(default="", description="Rationale for edge activation")
    suppression_reason: str = Field(default="", description="Rationale for edge suppression")
    supporting_rules: list[str] = Field(default_factory=list, description="IDs of matching RegimeRules")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ApplicabilityDecision(BaseModel):
    """Immutable model representing aggregated edge applicability decision across all edges."""

    decision_id: str = Field(
        ...,
        description="Unique decision ID formatted as APD_<HEX16>",
        pattern=r"^APD_[A-Fa-f0-9]{16}$",
    )
    active_edges: list[str] = Field(default_factory=list, description="IDs of ACTIVE ScientificEdges")
    suppressed_edges: list[str] = Field(default_factory=list, description="IDs of INACTIVE or REJECTED ScientificEdges")
    explanations: dict[str, str] = Field(default_factory=dict, description="Edge ID -> explanation string map")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class RegimeExplainabilityRecord(BaseModel):
    """Immutable model providing 100% scientific traceability for regime & applicability decisions."""

    explanation_id: str = Field(
        ...,
        description="Unique explanation ID formatted as REX_<HEX16>",
        pattern=r"^REX_[A-Fa-f0-9]{16}$",
    )
    regime_id: str = Field(..., description="Target MarketRegime ID (MRG_<HEX16>)")
    assessment_id: str = Field(..., description="Target ApplicabilityAssessment ID (APA_<HEX16>)")
    edge_id: str = Field(..., description="Target ScientificEdge ID (SED_<HEX16>)")
    detected_regime: str = Field(..., description="Detected regime classification name")
    supporting_rules: list[str] = Field(default_factory=list, description="IDs of matching RegimeRules")
    supporting_observations: dict[str, Any] = Field(default_factory=dict, description="Market observation metrics dictionary")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    scientific_explanation: str = Field(..., description="Detailed narrative scientific explanation")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
