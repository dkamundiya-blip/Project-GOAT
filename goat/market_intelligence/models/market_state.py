"""
Project GOAT Phase 4 — Market State Domain Model & Classification Enums

Defines strongly typed market state classifications (Trend, Volatility, Momentum, Regime, Liquidity)
and the immutable MarketState domain model.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class TrendState(str, Enum):
    """Directional trend classification."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"


class VolatilityLevel(str, Enum):
    """Volatility magnitude classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class MomentumState(str, Enum):
    """Momentum direction classification."""

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class RegimeState(str, Enum):
    """Structural regime classification."""

    TREND = "TREND"
    RANGE = "RANGE"
    EXPANSION = "EXPANSION"
    COMPRESSION = "COMPRESSION"


class LiquidityLevel(str, Enum):
    """Market liquidity classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class MarketState(BaseModel):
    """Immutable domain model representing classified market state across 5 core dimensions."""

    state_id: str = Field(
        ...,
        description="Unique market state ID formatted as MKS_<HEX16>",
        pattern=r"^MKS_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Canonical instrument symbol (e.g. VOLATILITY_100)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of classification")
    
    # Strongly typed dimension classifications
    trend: TrendState = Field(..., description="Trend direction: BULLISH, BEARISH, SIDEWAYS")
    volatility: VolatilityLevel = Field(..., description="Volatility level: LOW, MEDIUM, HIGH")
    momentum: MomentumState = Field(..., description="Momentum state: POSITIVE, NEGATIVE, NEUTRAL")
    regime: RegimeState = Field(..., description="Market regime: TREND, RANGE, EXPANSION, COMPRESSION")
    liquidity: LiquidityLevel = Field(..., description="Liquidity level: LOW, MEDIUM, HIGH")
    
    # Continuous metric scores [-1.0, 1.0] or >= 0.0
    trend_score: float = Field(default=0.0, description="Normalized trend strength score [-1.0, 1.0]")
    volatility_score: float = Field(default=0.0, description="Normalized volatility percentile / score [0.0, 1.0]")
    momentum_score: float = Field(default=0.0, description="Normalized momentum score [-1.0, 1.0]")
    liquidity_score: float = Field(default=0.0, description="Normalized liquidity score [0.0, 1.0]")

    checksum: str = Field(..., description="SHA-256 canonical digest of state fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_market_state_id(
    symbol: str,
    timestamp: str,
    trend: TrendState,
    volatility: VolatilityLevel,
    momentum: MomentumState,
    regime: RegimeState,
    liquidity: LiquidityLevel,
) -> tuple[str, str]:
    """Compute deterministic (state_id, canonical_hash) for MarketState.

    Returns:
        Tuple of (MKS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "liquidity": str(liquidity.value),
        "momentum": str(momentum.value),
        "regime": str(regime.value),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "trend": str(trend.value),
        "volatility": str(volatility.value),
    }
    digest = compute_canonical_sha256(payload)
    state_id = f"MKS_{digest[:16].upper()}"
    return state_id, digest.upper()
