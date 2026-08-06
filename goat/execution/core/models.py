"""
Project GOAT v0.8 — Core Immutable Domain Models for Production Execution Engine

Defines immutable Pydantic models:
- ExecutionIntent (EXI_<HEX16>)
- ExecutionRequest (EXR_<HEX16>)
- ExecutionDecision (EXD_<HEX16>)
- ExecutionLifecycle (EXL_<HEX16>)
- ExecutionAudit (EXA_<HEX16>)
- ExecutionFailure (EXF_<HEX16>)
- ExecutionSummary (EXS_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.execution.core.enums import AuditEventType, ExecutionFailureCategory, ExecutionState


class ExecutionIntent(BaseModel):
    """Immutable model representing a canonical execution intent."""

    intent_id: str = Field(..., description="Unique intent ID formatted as EXI_<HEX16>", pattern=r"^EXI_[A-Fa-f0-9]{16}$")
    signal_id: str = Field(..., description="Qualified input scientific signal ID")
    sizing_decision_id: str = Field(..., description="Risk position sizing decision ID")
    allocation_id: str = Field(..., description="Capital allocation ID")
    broker_id: str = Field(..., description="Target broker profile ID")
    symbol: str = Field(..., description="Target asset ticker symbol")
    side: OrderSide = Field(..., description="Order side enum (BUY, SELL)")
    quantity: float = Field(..., gt=0.0, description="Execution volume amount")
    order_type: OrderType = Field(default=OrderType.MARKET, description="Order type enum")
    time_in_force: TimeInForce = Field(default=TimeInForce.GTC, description="Time-in-force enum")
    stop_loss: float | None = Field(default=None, ge=0.0, description="Optional stop loss level")
    take_profit: float | None = Field(default=None, ge=0.0, description="Optional take profit level")
    status: ExecutionState = Field(default=ExecutionState.CREATED, description="Execution state enum")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionRequest(BaseModel):
    """Immutable model representing a dispatched broker request payload container."""

    request_id: str = Field(..., description="Unique request ID formatted as EXR_<HEX16>", pattern=r"^EXR_[A-Fa-f0-9]{16}$")
    intent_id: str = Field(..., description="Parent ExecutionIntent ID")
    broker_id: str = Field(..., description="Target broker profile ID")
    payload_dict: dict[str, Any] = Field(default_factory=dict, description="Dispatched broker order intent payload")
    dispatched_at: str = Field(..., description="ISO 8601 UTC timestamp of dispatch")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionDecision(BaseModel):
    """Immutable model representing execution validation decision result."""

    decision_id: str = Field(..., description="Unique decision ID formatted as EXD_<HEX16>", pattern=r"^EXD_[A-Fa-f0-9]{16}$")
    intent_id: str = Field(..., description="Target ExecutionIntent ID")
    approved: bool = Field(..., description="True if execution validation rules passed")
    explanation: str = Field(..., description="Explanation string of decision rationale")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of decision")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionLifecycle(BaseModel):
    """Immutable model representing a lifecycle state transition log entry."""

    lifecycle_id: str = Field(..., description="Unique lifecycle entry ID formatted as EXL_<HEX16>", pattern=r"^EXL_[A-Fa-f0-9]{16}$")
    intent_id: str = Field(..., description="Target ExecutionIntent ID")
    state: ExecutionState = Field(..., description="New execution state enum")
    previous_state: ExecutionState | None = Field(default=None, description="Previous execution state enum")
    transition_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of transition")
    explanation: str = Field(..., description="Explanation string for state transition")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionAudit(BaseModel):
    """Immutable model representing an audit trail log entry."""

    audit_id: str = Field(..., description="Unique audit entry ID formatted as EXA_<HEX16>", pattern=r"^EXA_[A-Fa-f0-9]{16}$")
    intent_id: str = Field(..., description="Target ExecutionIntent ID")
    event_type: AuditEventType = Field(..., description="Audit event category enum")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of audit event")
    details: str = Field(..., description="Detailed description string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionFailure(BaseModel):
    """Immutable model representing a execution failure event."""

    failure_id: str = Field(..., description="Unique failure ID formatted as EXF_<HEX16>", pattern=r"^EXF_[A-Fa-f0-9]{16}$")
    intent_id: str = Field(..., description="Target ExecutionIntent ID")
    error_code: str = Field(..., description="Machine-readable error code string")
    category: ExecutionFailureCategory = Field(..., description="Failure category classification enum")
    reason: str = Field(..., description="Human-readable failure explanation")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of failure")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionSummary(BaseModel):
    """Immutable model representing aggregated execution metrics."""

    summary_id: str = Field(..., description="Unique summary ID formatted as EXS_<HEX16>", pattern=r"^EXS_[A-Fa-f0-9]{16}$")
    total_intents: int = Field(..., ge=0, description="Total execution intents created")
    dispatched_count: int = Field(..., ge=0, description="Total requests dispatched")
    filled_count: int = Field(..., ge=0, description="Total executions filled")
    rejected_count: int = Field(..., ge=0, description="Total executions rejected")
    failed_count: int = Field(..., ge=0, description="Total execution failures")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of summary generation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
