"""
Project GOAT v1.0 — Immutable Live Tick Model

Defines LiveTick domain model with deterministic canonical SHA-256 ID generation.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class LiveTick(BaseModel):
    """Immutable model representing a normalized live streaming market price tick."""

    tick_id: str = Field(
        ...,
        description="Unique tick ID formatted as LTK_<HEX16>",
        pattern=r"^LTK_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Canonical instrument symbol (e.g. VOLATILITY_100)")
    price: float = Field(..., gt=0.0, description="Current spot price / mid quote price")
    bid: float = Field(..., gt=0.0, description="Current bid price")
    ask: float = Field(..., gt=0.0, description="Current ask price")
    spread: float = Field(..., ge=0.0, description="Price spread (ask - bid)")
    epoch_timestamp: int = Field(..., ge=0, description="Unix epoch timestamp in seconds from provider")
    arrival_timestamp: str = Field(..., description="ISO 8601 UTC timestamp string of local arrival")
    sequence_number: int = Field(..., ge=0, description="Monotonically increasing tick sequence index")
    connection_id: str = Field(default="DEFAULT", description="Identifier of active WebSocket connection")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Calculated arrival latency in milliseconds")
    checksum: str = Field(..., description="SHA-256 canonical digest of tick core fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_live_tick_id(
    symbol: str,
    price: float,
    bid: float,
    ask: float,
    epoch_timestamp: int,
    sequence_number: int,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (tick_id, canonical_hash) for LiveTick.

    Returns:
        Tuple of (LTK_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "ask": round(float(ask), 8),
        "bid": round(float(bid), 8),
        "epoch_timestamp": int(epoch_timestamp),
        "price": round(float(price), 8),
        "sequence_number": int(sequence_number),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    tick_id = f"LTK_{digest[:16].upper()}"
    return tick_id, digest.upper()
