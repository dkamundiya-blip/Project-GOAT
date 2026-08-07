"""
Project GOAT Phase 4 — Market Statistics Domain Model

Defines the immutable MarketStatistics model for continuous statistical calculation.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class MarketStatistics(BaseModel):
    """Immutable domain model representing continuous streaming market statistics."""

    stat_id: str = Field(
        ...,
        description="Unique statistics record ID formatted as MST_<HEX16>",
        pattern=r"^MST_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Canonical instrument symbol (e.g. VOLATILITY_100)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of calculation")
    window_size: int = Field(..., gt=0, description="Rolling window size in bars/ticks")
    
    # Statistical measures
    atr: float = Field(default=0.0, ge=0.0, description="Average True Range")
    true_range: float = Field(default=0.0, ge=0.0, description="Latest True Range")
    rolling_volatility: float = Field(default=0.0, ge=0.0, description="Rolling Volatility (Standard deviation of returns)")
    standard_deviation: float = Field(default=0.0, ge=0.0, description="Standard deviation of prices")
    variance: float = Field(default=0.0, ge=0.0, description="Variance of prices")
    average_tick_rate: float = Field(default=0.0, ge=0.0, description="Average tick arrival rate (ticks / second)")
    average_candle_size: float = Field(default=0.0, ge=0.0, description="Average candle price range")
    
    # Spread statistics
    mean_spread: float = Field(default=0.0, ge=0.0, description="Average spread in window")
    min_spread: float = Field(default=0.0, ge=0.0, description="Minimum spread in window")
    max_spread: float = Field(default=0.0, ge=0.0, description="Maximum spread in window")
    spread_variance: float = Field(default=0.0, ge=0.0, description="Variance of spread in window")
    
    # Price action & momentum metrics
    market_speed: float = Field(default=0.0, ge=0.0, description="Market velocity (price movement per second)")
    rolling_high: float = Field(..., gt=0.0, description="Rolling highest price in window")
    rolling_low: float = Field(..., gt=0.0, description="Rolling lowest price in window")
    rolling_vwap: float = Field(default=0.0, ge=0.0, description="Volume-Weighted Average Price in window")
    
    checksum: str = Field(..., description="SHA-256 canonical digest of core fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_market_statistics_id(
    symbol: str,
    timestamp: str,
    window_size: int,
    atr: float,
    rolling_volatility: float,
    rolling_vwap: float,
) -> tuple[str, str]:
    """Compute deterministic (stat_id, canonical_hash) for MarketStatistics.

    Returns:
        Tuple of (MST_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "atr": round(float(atr), 8),
        "rolling_volatility": round(float(rolling_volatility), 8),
        "rolling_vwap": round(float(rolling_vwap), 8),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "window_size": int(window_size),
    }
    digest = compute_canonical_sha256(payload)
    stat_id = f"MST_{digest[:16].upper()}"
    return stat_id, digest.upper()
