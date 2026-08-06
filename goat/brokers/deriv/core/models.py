"""
Project GOAT v0.8 — Core Immutable Domain Models for Deriv Production Adapter

Defines immutable Pydantic models:
- DerivSession (DRS_<HEX16>)
- DerivAuthentication (DAT_<HEX16>)
- DerivAccountSnapshot (DAC_<HEX16>)
- DerivMarketSubscription (DMS_<HEX16>)
- DerivOrderPayload (DOP_<HEX16>)
- DerivExecutionResponse (DER_<HEX16>)
- DerivHeartbeat (DHB_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.deriv.core.enums import DerivContractType, DerivDurationUnit


class DerivSession(BaseModel):
    """Immutable model describing Deriv session telemetry and server connection state."""

    session_id: str = Field(..., description="Unique session ID formatted as DRS_<HEX16>", pattern=r"^DRS_[A-Fa-f0-9]{16}$")
    broker_id: str = Field(default="BRK_DERIV", description="Target broker ID")
    status: ConnectionStatus = Field(..., description="Connection status enum")
    server_time: str = Field(..., description="ISO 8601 UTC timestamp of Deriv server time")
    ping_ms: float = Field(default=0.0, ge=0.0, description="WebSocket round-trip ping latency in ms")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class DerivAuthentication(BaseModel):
    """Immutable model representing Deriv API token authentication state."""

    auth_id: str = Field(..., description="Unique auth ID formatted as DAT_<HEX16>", pattern=r"^DAT_[A-Fa-f0-9]{16}$")
    app_id: int = Field(..., ge=1, description="Deriv registered App ID")
    token_hash: str = Field(..., description="SHA-256 hash digest of API token (raw token NEVER stored)")
    is_authenticated: bool = Field(..., description="True if Deriv authorize request succeeded")
    user_id: str = Field(default="", description="Deriv user ID")
    email: str = Field(default="", description="Deriv user email string")
    currency: str = Field(default="USD", description="Account currency string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class DerivAccountSnapshot(BaseModel):
    """Immutable model representing Deriv account balance snapshot."""

    snapshot_id: str = Field(..., description="Unique snapshot ID formatted as DAC_<HEX16>", pattern=r"^DAC_[A-Fa-f0-9]{16}$")
    login_id: str = Field(..., description="Deriv account login ID (e.g. CR123456)")
    currency: str = Field(..., description="Base denomination currency ISO code")
    balance: float = Field(..., ge=0.0, description="Account balance")
    equity: float = Field(..., ge=0.0, description="Account equity")
    margin: float = Field(default=0.0, ge=0.0, description="Used margin")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class DerivMarketSubscription(BaseModel):
    """Immutable model representing Deriv market data stream subscription."""

    subscription_id: str = Field(..., description="Unique subscription ID formatted as DMS_<HEX16>", pattern=r"^DMS_[A-Fa-f0-9]{16}$")
    symbol: str = Field(..., description="Target market symbol")
    request_id: int = Field(..., ge=1, description="WebSocket request tracking ID")
    is_active: bool = Field(..., description="True if subscription is active")
    stream_id: str = Field(default="", description="Deriv subscription stream hash ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class DerivOrderPayload(BaseModel):
    """Immutable model representing a translated Deriv order proposal/buy payload."""

    payload_id: str = Field(..., description="Unique payload ID formatted as DOP_<HEX16>", pattern=r"^DOP_[A-Fa-f0-9]{16}$")
    intent_id: str = Field(..., description="Source GOAT order intent ID")
    symbol: str = Field(..., description="Target asset symbol")
    amount: float = Field(..., gt=0.0, description="Order stake / volume amount")
    contract_type: DerivContractType = Field(..., description="Deriv contract type enum")
    duration: int = Field(default=5, ge=1, description="Contract duration value")
    duration_unit: DerivDurationUnit = Field(default=DerivDurationUnit.TICKS, description="Duration unit enum")
    barrier: str | None = Field(default=None, description="Optional price barrier string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class DerivExecutionResponse(BaseModel):
    """Immutable model representing a Deriv execution purchase response."""

    execution_id: str = Field(..., description="Unique execution ID formatted as DER_<HEX16>", pattern=r"^DER_[A-Fa-f0-9]{16}$")
    contract_id: str = Field(..., description="Deriv contract ID")
    buy_price: float = Field(..., ge=0.0, description="Purchase price amount")
    payout: float = Field(default=0.0, ge=0.0, description="Contract payout amount")
    status: str = Field(default="PURCHASED", description="Deriv execution status string")
    transaction_id: str = Field(default="", description="Deriv transaction ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class DerivHeartbeat(BaseModel):
    """Immutable model representing Deriv ping/pong heartbeat measurement."""

    heartbeat_id: str = Field(..., description="Unique heartbeat ID formatted as DHB_<HEX16>", pattern=r"^DHB_[A-Fa-f0-9]{16}$")
    ping_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of ping send")
    pong_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of pong receipt")
    roundtrip_ms: float = Field(..., ge=0.0, description="Ping/pong round-trip latency in ms")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
