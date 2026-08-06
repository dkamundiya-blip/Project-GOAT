"""
Project GOAT v0.8 — Core Immutable Domain Models for Trade Lifecycle Engine

Defines immutable Pydantic V2 models using ConfigDict(frozen=True, extra="forbid"):
- TradeLifecycle (TRL_<HEX16>)
- TradeStateRecord (TST_<HEX16>)
- TradeEvent (TEV_<HEX16>)
- BrokerExecution (BEX_<HEX16>)
- PositionSnapshot (PSP_<HEX16>)
- LifecycleTransition (LTR_<HEX16>)
- LifecycleAudit (LAD_<HEX16>)
- LifecycleSummary (LSM_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.lifecycle.core.enums import (
    LifecycleAuditEventType,
    TradeEventType,
    TradeReconciliationMismatchType,
    TradeState,
)


class TradeLifecycle(BaseModel):
    """Immutable model representing a trade lifecycle record."""

    lifecycle_id: str = Field(
        ...,
        description="Unique lifecycle ID formatted as TRL_<HEX16>",
        pattern=r"^TRL_[A-Fa-f0-9]{16}$",
    )
    intent_id: str = Field(..., description="Associated ExecutionIntent ID")
    symbol: str = Field(..., description="Trading asset ticker symbol")
    side: str = Field(..., description="Order side (BUY, SELL, LONG, SHORT)")
    quantity: float = Field(..., gt=0.0, description="Order quantity / volume")
    position_id: str = Field(default="", description="Associated portfolio Position ID")
    broker_execution_id: str = Field(default="", description="Associated BrokerExecution ID")
    current_state: TradeState = Field(default=TradeState.CREATED, description="Current lifecycle state")
    previous_state: TradeState | None = Field(default=None, description="Previous lifecycle state")
    created_at: str = Field(..., description="ISO 8601 UTC timestamp of creation")
    updated_at: str = Field(..., description="ISO 8601 UTC timestamp of latest state update")
    closed_at: str | None = Field(default=None, description="ISO 8601 UTC timestamp of final closure")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class TradeStateRecord(BaseModel):
    """Immutable model representing a point-in-time trade state log entry."""

    state_id: str = Field(
        ...,
        description="Unique state record ID formatted as TST_<HEX16>",
        pattern=r"^TST_[A-Fa-f0-9]{16}$",
    )
    lifecycle_id: str = Field(..., description="Target TradeLifecycle ID")
    state: TradeState = Field(..., description="Recorded TradeState enum")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class TradeEvent(BaseModel):
    """Immutable model representing an append-only lifecycle event."""

    event_id: str = Field(
        ...,
        description="Unique trade event ID formatted as TEV_<HEX16>",
        pattern=r"^TEV_[A-Fa-f0-9]{16}$",
    )
    lifecycle_id: str = Field(..., description="Target TradeLifecycle ID")
    event_type: TradeEventType = Field(..., description="Event type classification enum")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    details: str = Field(..., description="Human-readable event details string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class BrokerExecution(BaseModel):
    """Immutable model representing broker execution fill telemetry."""

    execution_id: str = Field(
        ...,
        description="Unique broker execution ID formatted as BEX_<HEX16>",
        pattern=r"^BEX_[A-Fa-f0-9]{16}$",
    )
    intent_id: str = Field(..., description="Parent ExecutionIntent ID")
    broker_order_id: str = Field(..., description="Broker-assigned order ID")
    symbol: str = Field(..., description="Asset ticker symbol")
    side: str = Field(..., description="Order side")
    quantity: float = Field(..., gt=0.0, description="Executed fill quantity")
    price: float = Field(..., gt=0.0, description="Executed fill price")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of execution fill")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class PositionSnapshot(BaseModel):
    """Immutable model representing position state reference at a point in time."""

    snapshot_id: str = Field(
        ...,
        description="Unique position snapshot ID formatted as PSP_<HEX16>",
        pattern=r"^PSP_[A-Fa-f0-9]{16}$",
    )
    position_id: str = Field(..., description="Target Position ID")
    symbol: str = Field(..., description="Asset ticker symbol")
    side: str = Field(..., description="Position side (LONG, SHORT)")
    quantity: float = Field(..., ge=0.0, description="Position lot volume")
    entry_price: float = Field(..., ge=0.0, description="Average entry price")
    current_price: float = Field(..., ge=0.0, description="Mark-to-market price")
    unrealized_pnl: float = Field(default=0.0, description="Current unrealized P/L")
    realized_pnl: float = Field(default=0.0, description="Cumulative realized P/L")
    status: str = Field(default="OPEN", description="Position status string")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class LifecycleTransition(BaseModel):
    """Immutable model representing a validated state machine transition entry."""

    transition_id: str = Field(
        ...,
        description="Unique transition ID formatted as LTR_<HEX16>",
        pattern=r"^LTR_[A-Fa-f0-9]{16}$",
    )
    lifecycle_id: str = Field(..., description="Target TradeLifecycle ID")
    from_state: TradeState = Field(..., description="Source state enum")
    to_state: TradeState = Field(..., description="Destination state enum")
    reason: str = Field(..., description="Explanation for transition")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class LifecycleAudit(BaseModel):
    """Immutable audit trail record for trade lifecycle transitions and events."""

    audit_id: str = Field(
        ...,
        description="Unique audit ID formatted as LAD_<HEX16>",
        pattern=r"^LAD_[A-Fa-f0-9]{16}$",
    )
    lifecycle_id: str = Field(..., description="Target TradeLifecycle ID")
    event_type: LifecycleAuditEventType = Field(..., description="Audit event type enum")
    previous_state: TradeState | None = Field(default=None, description="Previous state")
    new_state: TradeState = Field(..., description="New state")
    reason: str = Field(..., description="Detailed rationale")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    execution_ref: str = Field(default="", description="Execution intent or broker execution reference")
    broker_ref: str = Field(default="", description="Broker profile or order reference")
    portfolio_ref: str = Field(default="", description="Portfolio or position reference")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class LifecycleSummary(BaseModel):
    """Immutable summary record for trade lifecycle subsystem metrics."""

    summary_id: str = Field(
        ...,
        description="Unique summary ID formatted as LSM_<HEX16>",
        pattern=r"^LSM_[A-Fa-f0-9]{16}$",
    )
    total_trades: int = Field(..., ge=0, description="Total lifecycles created")
    open_trades: int = Field(..., ge=0, description="Active open trade lifecycles")
    closed_trades: int = Field(..., ge=0, description="Completed closed trade lifecycles")
    cancelled_trades: int = Field(..., ge=0, description="Cancelled trade lifecycles")
    rejected_trades: int = Field(..., ge=0, description="Rejected trade lifecycles")
    failed_trades: int = Field(..., ge=0, description="Failed trade lifecycles")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class TradeReconciliationItem(BaseModel):
    """Immutable record describing a trade lifecycle reconciliation discrepancy."""

    item_id: str = Field(..., description="Discrepancy item identifier")
    mismatch_type: TradeReconciliationMismatchType = Field(..., description="Discrepancy category enum")
    lifecycle_id: str = Field(default="", description="Associated TradeLifecycle ID")
    symbol: str = Field(default="", description="Asset symbol")
    broker_value: Any = Field(default=None, description="Value from broker state")
    portfolio_value: Any = Field(default=None, description="Value from portfolio state")
    lifecycle_value: Any = Field(default=None, description="Value from lifecycle state")
    description: str = Field(..., description="Detailed explanation of discrepancy")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")

    model_config = ConfigDict(frozen=True, extra="forbid")
