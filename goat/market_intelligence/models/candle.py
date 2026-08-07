"""
Project GOAT Phase 4 — Intelligence Candle Domain Model & Timeframe Enum

Defines IntelligenceCandle domain model and IntelligenceTimeframe supporting 12 timeframes:
1s, 5s, 15s, 30s, 1m, 2m, 5m, 15m, 30m, 1h, 4h, 1d.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class IntelligenceTimeframe(str, Enum):
    """Supported multi-resolution aggregation timeframes for Universal Candle Builder."""

    S1 = "1s"
    S5 = "5s"
    S15 = "15s"
    S30 = "30s"
    M1 = "1m"
    M2 = "2m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


TIMEFRAME_SECONDS: dict[str, int] = {
    "1s": 1,
    "5s": 5,
    "15s": 15,
    "30s": 30,
    "1m": 60,
    "2m": 120,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


class IntelligenceCandle(BaseModel):
    """Immutable domain model representing an aggregated OHLCV candle bar."""

    candle_id: str = Field(
        ...,
        description="Unique candle ID formatted as ICD_<HEX16>",
        pattern=r"^ICD_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Canonical instrument symbol (e.g. VOLATILITY_100)")
    timeframe: IntelligenceTimeframe = Field(..., description="Candle timeframe resolution")
    open: float = Field(..., gt=0.0, description="Opening tick price")
    high: float = Field(..., gt=0.0, description="Highest tick price in window")
    low: float = Field(..., gt=0.0, description="Lowest tick price in window")
    close: float = Field(..., gt=0.0, description="Closing tick price")
    volume: float = Field(default=0.0, ge=0.0, description="Tick count in candle window")
    open_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of candle open boundary")
    close_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of candle close boundary")
    completed: bool = Field(default=True, description="True if candle is fully closed, False if forming")
    checksum: str = Field(..., description="SHA-256 canonical digest of core candle fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    @property
    def is_bullish(self) -> bool:
        """True if close >= open."""
        return self.close >= self.open

    @property
    def price_range(self) -> float:
        """Returns high - low range."""
        return round(self.high - self.low, 8)

    class Config:
        frozen = True
        extra = "forbid"


def compute_intelligence_candle_id(
    symbol: str,
    timeframe: str,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    open_timestamp: str,
    close_timestamp: str,
) -> tuple[str, str]:
    """Compute deterministic (candle_id, canonical_hash) for IntelligenceCandle.

    Returns:
        Tuple of (ICD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "close": round(float(close_price), 8),
        "close_timestamp": str(close_timestamp).strip(),
        "high": round(float(high_price), 8),
        "low": round(float(low_price), 8),
        "open": round(float(open_price), 8),
        "open_timestamp": str(open_timestamp).strip(),
        "symbol": str(symbol).strip().upper(),
        "timeframe": str(timeframe).strip().lower(),
    }
    digest = compute_canonical_sha256(payload)
    candle_id = f"ICD_{digest[:16].upper()}"
    return candle_id, digest.upper()
