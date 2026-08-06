"""
Project GOAT v0.8 — Core Immutable Domain Models for Broker Abstraction Framework

Defines immutable Pydantic models:
- BrokerProfile (BRK_<HEX16>)
- BrokerConnection (BCN_<HEX16>)
- BrokerAccount (BAC_<HEX16>)
- BrokerOrderIntent (BOI_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.brokers.core.enums import (
    BrokerType,
    ConnectionStatus,
    OrderSide,
    OrderType,
    TimeInForce,
)


class BrokerProfile(BaseModel):
    """Immutable model describing broker metadata and architectural capabilities."""

    broker_id: str = Field(
        ...,
        description="Unique broker ID formatted as BRK_<HEX16>",
        pattern=r"^BRK_[A-Fa-f0-9]{16}$",
    )
    broker_name: str = Field(..., description="Human-readable broker name (e.g., Deriv Synthetic Indices)")
    broker_type: BrokerType = Field(..., description="Broker technology category enum")
    api_version: str = Field(default="v3", description="Broker API specification version")
    supported_assets: list[str] = Field(default_factory=list, description="List of supported symbol strings")
    supported_order_types: list[OrderType] = Field(default_factory=list, description="List of supported order types")
    supports_streaming: bool = Field(default=True, description="True if broker supports real-time market data streaming")
    supports_positions: bool = Field(default=True, description="True if broker supports position tracking")
    supports_history: bool = Field(default=True, description="True if broker supports historical bar downloading")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class BrokerConnection(BaseModel):
    """Immutable model representing active broker session telemetry and connection health."""

    connection_id: str = Field(
        ...,
        description="Unique connection ID formatted as BCN_<HEX16>",
        pattern=r"^BCN_[A-Fa-f0-9]{16}$",
    )
    broker_id: str = Field(..., description="Target broker profile ID")
    status: ConnectionStatus = Field(..., description="Connection status enum")
    connected_at: str = Field(..., description="ISO 8601 UTC timestamp of connection establishment")
    disconnected_at: str | None = Field(default=None, description="ISO 8601 UTC timestamp of disconnection")
    heartbeat_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of last received heartbeat")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Measured socket round-trip latency in milliseconds")
    reconnect_attempts: int = Field(default=0, ge=0, description="Counter of reconnection attempts")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Operational connection metadata")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class BrokerAccount(BaseModel):
    """Immutable model representing broker trading account balance, margin, and leverage state."""

    account_id: str = Field(
        ...,
        description="Unique account ID formatted as BAC_<HEX16>",
        pattern=r"^BAC_[A-Fa-f0-9]{16}$",
    )
    broker_id: str = Field(..., description="Target broker profile ID")
    account_type: str = Field(default="REAL", description="Account classification (REAL, DEMO, VIRTUAL)")
    account_currency: str = Field(default="USD", description="Base denomination currency ISO code")
    balance: float = Field(..., ge=0.0, description="Account cash balance")
    equity: float = Field(..., ge=0.0, description="Current net account equity (balance + unrealized PnL)")
    margin: float = Field(default=0.0, ge=0.0, description="Used margin capital")
    free_margin: float = Field(..., ge=0.0, description="Available unencumbered capital for margin trading")
    leverage: float = Field(default=1.0, ge=1.0, description="Account maximum leverage ratio")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class BrokerOrderIntent(BaseModel):
    """Immutable model representing an unexecuted execution order intent request structure."""

    intent_id: str = Field(
        ...,
        description="Unique order intent ID formatted as BOI_<HEX16>",
        pattern=r"^BOI_[A-Fa-f0-9]{16}$",
    )
    broker_id: str = Field(..., description="Target broker profile ID")
    symbol: str = Field(..., description="Target trading asset symbol")
    side: OrderSide = Field(..., description="Order side enum (BUY, SELL)")
    quantity: float = Field(..., gt=0.0, description="Requested order volume / lot size")
    order_type: OrderType = Field(default=OrderType.MARKET, description="Order execution type enum")
    time_in_force: TimeInForce = Field(default=TimeInForce.GTC, description="Time-in-force policy enum")
    stop_loss: float | None = Field(default=None, ge=0.0, description="Optional stop loss price level")
    take_profit: float | None = Field(default=None, ge=0.0, description="Optional take profit price level")
    comment: str = Field(default="", description="Optional order tag or strategy identification string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
