"""
Project GOAT v1.0 — Immutable Live Quote Model

Defines LiveQuote model summarizing current real-time state per instrument.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LiveQuote(BaseModel):
    """Immutable real-time market quote snapshot for an instrument."""

    symbol: str = Field(..., description="Canonical symbol ID (e.g. VOLATILITY_100)")
    deriv_ws_symbol: str = Field(..., description="Deriv WS API symbol name (e.g. R_100)")
    live_price: float = Field(default=0.0, description="Latest mid quote price")
    bid: float = Field(default=0.0, description="Latest bid price")
    ask: float = Field(default=0.0, description="Latest ask price")
    spread: float = Field(default=0.0, description="Bid-ask spread")
    connection_status: str = Field(default="DISCONNECTED", description="Connection status string")
    latency_ms: float = Field(default=0.0, description="Latest latency measurement in ms")
    tick_frequency: float = Field(default=0.0, description="Average ticks per second")
    streaming_status: str = Field(default="IDLE", description="STREAMING / STALE / IDLE / ERROR")
    last_tick_time: str = Field(default="", description="ISO timestamp of last received tick")
    total_ticks: int = Field(default=0, ge=0, description="Total ticks ingested for symbol")

    class Config:
        frozen = True
        extra = "forbid"
