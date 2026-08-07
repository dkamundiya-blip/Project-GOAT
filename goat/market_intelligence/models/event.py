"""
Project GOAT Phase 4 — Market Event Domain Model & Event Categories

Defines market event classification types and the immutable MarketEvent model.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class IntelligenceEventType(str, Enum):
    """Supported market event categories for automated event detection."""

    LARGE_SPIKE = "LARGE_SPIKE"
    CRASH = "CRASH"
    EXTREME_CANDLE = "EXTREME_CANDLE"
    VOLATILITY_EXPANSION = "VOLATILITY_EXPANSION"
    VOLATILITY_CONTRACTION = "VOLATILITY_CONTRACTION"
    GAP = "GAP"
    SPREAD_ANOMALY = "SPREAD_ANOMALY"
    CONNECTION_INTERRUPTION = "CONNECTION_INTERRUPTION"
    MARKET_PAUSE = "MARKET_PAUSE"


class MarketEvent(BaseModel):
    """Immutable domain model representing a detected market anomaly or structural event."""

    event_id: str = Field(
        ...,
        description="Unique market event ID formatted as MKE_<HEX16>",
        pattern=r"^MKE_[A-Fa-f0-9]{16}$",
    )
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of event occurrence")
    symbol: str = Field(..., description="Canonical instrument symbol (e.g. VOLATILITY_100)")
    event_type: IntelligenceEventType = Field(..., description="Category of detected event")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of detection [0.0, 1.0]")
    checksum: str = Field(..., description="SHA-256 canonical digest of event fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Detailed context & metrics")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_market_event_id(
    symbol: str,
    timestamp: str,
    event_type: IntelligenceEventType,
    confidence: float,
) -> tuple[str, str]:
    """Compute deterministic (event_id, canonical_hash) for MarketEvent.

    Returns:
        Tuple of (MKE_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "confidence": round(float(confidence), 4),
        "event_type": str(event_type.value),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    event_id = f"MKE_{digest[:16].upper()}"
    return event_id, digest.upper()
