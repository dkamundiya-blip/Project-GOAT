"""
Project GOAT v0.8 — Core Immutable Domain Models for Market Data Infrastructure

Defines immutable Pydantic models:
- MarketTick (MTK_<HEX16>)
- MarketCandle (MCD_<HEX16>)
- MarketStreamState (MSS_<HEX16>)
- MarketGap (MGP_<HEX16>)
- ReplaySnapshot (RPS_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.marketdata.core.enums import (
    GapReason,
    MarketTimeframe,
    StreamConnectionStatus,
)


class MarketTick(BaseModel):
    """Immutable model representing a normalized live market price tick."""

    tick_id: str = Field(
        ...,
        description="Unique tick ID formatted as MTK_<HEX16>",
        pattern=r"^MTK_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Market instrument ticker symbol (e.g. R_100, EURUSD)")
    broker: str = Field(default="DERIV", description="Originating broker platform identifier")
    bid: float = Field(..., gt=0.0, description="Current bid price")
    ask: float = Field(..., gt=0.0, description="Current ask price")
    spread: float = Field(..., ge=0.0, description="Spread between ask and bid prices (ask - bid)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp string of tick occurrence")
    sequence_number: int = Field(..., ge=0, description="Monotonically increasing sequence index")
    source_latency: float = Field(default=0.0, ge=0.0, description="Network/ingestion latency in milliseconds")
    checksum: str = Field(..., description="SHA-256 canonical digest of tick fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    @property
    def mid_price(self) -> float:
        """Calculates mid price (bid + ask) / 2."""
        return round((self.bid + self.ask) / 2.0, 8)

    class Config:
        frozen = True
        extra = "forbid"


class MarketCandle(BaseModel):
    """Immutable model representing an aggregated OHLCV candle bar."""

    candle_id: str = Field(
        ...,
        description="Unique candle ID formatted as MCD_<HEX16>",
        pattern=r"^MCD_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Market instrument ticker symbol")
    timeframe: MarketTimeframe = Field(..., description="Candle aggregation timeframe (1S, 1M, 5M, 1H, 1D)")
    open: float = Field(..., gt=0.0, description="Opening price of the candle interval")
    high: float = Field(..., gt=0.0, description="Highest price during the candle interval")
    low: float = Field(..., gt=0.0, description="Lowest price during the candle interval")
    close: float = Field(..., gt=0.0, description="Closing price of the candle interval")
    volume: float = Field(default=0.0, ge=0.0, description="Trading volume or tick count in bar")
    open_timestamp: str = Field(..., description="ISO 8601 UTC timestamp string of candle open")
    close_timestamp: str = Field(..., description="ISO 8601 UTC timestamp string of candle close")
    completed: bool = Field(default=True, description="True if candle is fully closed, False if forming bar")
    checksum: str = Field(..., description="SHA-256 canonical digest of candle fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    @property
    def is_bullish(self) -> bool:
        """Returns True if close >= open."""
        return self.close >= self.open

    @property
    def range(self) -> float:
        """Returns candle price range (high - low)."""
        return round(self.high - self.low, 8)

    class Config:
        frozen = True
        extra = "forbid"


class MarketStreamState(BaseModel):
    """Immutable model representing the real-time operational state of a market stream."""

    stream_id: str = Field(
        ...,
        description="Unique stream state ID formatted as MSS_<HEX16>",
        pattern=r"^MSS_[A-Fa-f0-9]{16}$",
    )
    broker: str = Field(default="DERIV", description="Broker platform identifier")
    symbol: str = Field(..., description="Target market symbol")
    connection_status: StreamConnectionStatus = Field(
        default=StreamConnectionStatus.CONNECTED,
        description="Current stream connection health status",
    )
    heartbeat_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of last verified heartbeat")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Measured round-trip socket latency in ms")
    packets_received: int = Field(default=0, ge=0, description="Total valid packets received")
    packets_dropped: int = Field(default=0, ge=0, description="Total malformed/dropped packets")
    reconnect_count: int = Field(default=0, ge=0, description="Total reconnect attempts performed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Operational metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class MarketGap(BaseModel):
    """Immutable model representing a detected sequence or timestamp gap in market stream."""

    gap_id: str = Field(
        ...,
        description="Unique gap ID formatted as MGP_<HEX16>",
        pattern=r"^MGP_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Target market instrument symbol")
    start_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of gap start")
    end_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of gap resolution")
    missing_packets: int = Field(default=1, ge=1, description="Estimated number of missing ticks/packets")
    reason: GapReason = Field(..., description="Root cause description enum for the gap")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary with context")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ReplaySnapshot(BaseModel):
    """Immutable model representing a point-in-time state snapshot for deterministic replay."""

    replay_id: str = Field(
        ...,
        description="Unique replay snapshot ID formatted as RPS_<HEX16>",
        pattern=r"^RPS_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Target market instrument symbol")
    replay_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of snapshot capture")
    replay_checksum: str = Field(..., description="Cumulative SHA-256 checksum digest of replayed sequence")
    snapshot_reference: str = Field(..., description="Pointer ID to underlying state / tick repository range")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
