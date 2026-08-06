"""
Project GOAT v0.8 — Core Immutable Domain Models for Market State Intelligence

Defines immutable Pydantic models:
- MarketState (MST_<HEX16>)
- VolatilityAssessment (VOL_<HEX16>)
- LiquidityAssessment (LIQ_<HEX16>)
- StructureAssessment (STR_<HEX16>)
- MarketQualityAssessment (MQA_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.marketstate.core.enums import (
    ActivityState,
    LiquidityState,
    QualityState,
    SpreadState,
    StructureState,
    TrendState,
    VolatilityState,
)


class VolatilityAssessment(BaseModel):
    """Immutable model representing market volatility measurement and classification."""

    assessment_id: str = Field(
        ...,
        description="Unique assessment ID formatted as VOL_<HEX16>",
        pattern=r"^VOL_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Target market instrument symbol")
    timeframe: str = Field(default="1M", description="Evaluation timeframe (1M, 5M, 1H, 1D)")
    realized_volatility: float = Field(..., ge=0.0, description="Measured realized volatility standard deviation")
    volatility_class: VolatilityState = Field(..., description="Volatility level classification enum")
    volatility_score: float = Field(..., ge=0.0, le=100.0, description="Normalized volatility score (0 to 100)")
    explanation: str = Field(..., description="Deterministic explanation of volatility rating")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class LiquidityAssessment(BaseModel):
    """Immutable model representing market liquidity, spread quality, and depth proxies."""

    assessment_id: str = Field(
        ...,
        description="Unique assessment ID formatted as LIQ_<HEX16>",
        pattern=r"^LIQ_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Target market instrument symbol")
    spread: float = Field(..., ge=0.0, description="Current bid/ask spread width")
    spread_quality: SpreadState = Field(..., description="Spread width classification enum")
    liquidity_score: float = Field(..., ge=0.0, le=100.0, description="Normalized liquidity score (0 to 100)")
    market_depth_proxy: float = Field(..., ge=0.0, description="Estimated tick frequency & depth proxy value")
    activity_state: ActivityState = Field(default=ActivityState.NORMAL, description="Tick activity state")
    liquidity_state: LiquidityState = Field(default=LiquidityState.NORMAL, description="Liquidity state enum")
    explanation: str = Field(..., description="Deterministic explanation of liquidity assessment")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class StructureAssessment(BaseModel):
    """Immutable model representing market price action structure and trend classification."""

    assessment_id: str = Field(
        ...,
        description="Unique assessment ID formatted as STR_<HEX16>",
        pattern=r"^STR_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Target market instrument symbol")
    structure_state: StructureState = Field(..., description="Market structure classification (BULLISH, BEARISH, RANGING)")
    trend_state: TrendState = Field(default=TrendState.SIDEWAYS, description="Trend direction classification")
    higher_highs: int = Field(default=0, ge=0, description="Count of higher high pivot points")
    lower_lows: int = Field(default=0, ge=0, description="Count of lower low pivot points")
    higher_lows: int = Field(default=0, ge=0, description="Count of higher low pivot points")
    lower_highs: int = Field(default=0, ge=0, description="Count of lower high pivot points")
    trend_strength: float = Field(..., ge=0.0, le=100.0, description="Trend strength rating (0 to 100)")
    explanation: str = Field(..., description="Deterministic explanation of structural classification")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class MarketQualityAssessment(BaseModel):
    """Immutable model representing market feed, stream, and validation quality evaluation."""

    assessment_id: str = Field(
        ...,
        description="Unique assessment ID formatted as MQA_<HEX16>",
        pattern=r"^MQA_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Target market instrument symbol")
    data_quality: QualityState = Field(..., description="Data validation quality status")
    stream_health: QualityState = Field(..., description="Stream telemetry health status")
    latency_quality: QualityState = Field(..., description="Socket latency quality status")
    replay_quality: QualityState = Field(..., description="Replay checksum integrity status")
    overall_quality: QualityState = Field(..., description="Consolidated quality state classification")
    explanation: str = Field(..., description="Deterministic explanation of quality rating")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class MarketState(BaseModel):
    """Immutable master model describing overall observable market state."""

    state_id: str = Field(
        ...,
        description="Unique market state ID formatted as MST_<HEX16>",
        pattern=r"^MST_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Target market instrument symbol")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of market state observation")
    trend_state: TrendState = Field(..., description="Current trend direction and strength")
    volatility_state: VolatilityState = Field(..., description="Current volatility level")
    liquidity_state: LiquidityState = Field(..., description="Current liquidity level")
    spread_state: SpreadState = Field(..., description="Current spread width status")
    activity_state: ActivityState = Field(..., description="Current tick activity level")
    structure_state: StructureState = Field(..., description="Current price action structure")
    overall_quality: QualityState = Field(default=QualityState.GOOD, description="Consolidated feed quality state")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Deterministic confidence score (0.0 to 1.0)")
    explanation: str = Field(..., description="Comprehensive deterministic explanation of market state")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Operational metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
