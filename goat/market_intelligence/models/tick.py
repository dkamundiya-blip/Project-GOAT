"""
Project GOAT Phase 4 — Recorded Tick Domain Model

Defines the immutable RecordedTick model for recording incoming websocket market ticks.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class RecordedTick(BaseModel):
    """Immutable domain model for a recorded market price tick."""

    tick_id: str = Field(
        ...,
        description="Unique recorded tick ID formatted as RTK_<HEX16>",
        pattern=r"^RTK_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Canonical market symbol (e.g. VOLATILITY_100)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of tick occurrence")
    bid: float = Field(..., gt=0.0, description="Current bid price")
    ask: float = Field(..., gt=0.0, description="Current ask price")
    mid_price: float = Field(..., gt=0.0, description="Calculated mid price (bid + ask) / 2")
    spread: float = Field(..., ge=0.0, description="Price spread (ask - bid)")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Calculated ingestion latency in milliseconds")
    sequence_number: int = Field(..., ge=0, description="Monotonically increasing tick sequence index")
    source: str = Field(default="WEBSOCKET", description="Originating feed source")
    checksum: str = Field(..., description="SHA-256 canonical digest of tick core fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_recorded_tick_id(
    symbol: str,
    bid: float,
    ask: float,
    mid_price: float,
    timestamp: str,
    sequence_number: int,
    source: str = "WEBSOCKET",
) -> tuple[str, str]:
    """Compute deterministic (tick_id, canonical_hash) for RecordedTick.

    Returns:
        Tuple of (RTK_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "ask": round(float(ask), 8),
        "bid": round(float(bid), 8),
        "mid_price": round(float(mid_price), 8),
        "sequence_number": int(sequence_number),
        "source": str(source).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    tick_id = f"RTK_{digest[:16].upper()}"
    return tick_id, digest.upper()
