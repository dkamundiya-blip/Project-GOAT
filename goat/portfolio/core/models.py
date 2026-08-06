"""
Project GOAT v0.8 — Core Immutable Domain Models for Portfolio Engine

Defines immutable Pydantic models:
- Portfolio (PTF_<HEX16>)
- Position (POS_<HEX16>)
- ClosedPosition (CLS_<HEX16>)
- PortfolioSnapshot (PSN_<HEX16>)
- ExposureSummary (EXP_<HEX16>)
- PerformanceSummary (PER_<HEX16>)
- AccountSnapshot (ACC_<HEX16>)
- PortfolioAudit (PAD_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.portfolio.core.enums import (
    CloseReason,
    PortfolioAuditEventType,
    PortfolioStatus,
    PositionSide,
    PositionStatus,
    ReconciliationMismatchType,
)


class Portfolio(BaseModel):
    """Immutable model representing a top-level canonical portfolio configuration and state."""

    portfolio_id: str = Field(
        ...,
        description="Unique portfolio ID formatted as PTF_<HEX16>",
        pattern=r"^PTF_[A-Fa-f0-9]{16}$",
    )
    account_id: str = Field(..., description="Associated broker account ID")
    portfolio_name: str = Field(..., description="Human-readable portfolio name")
    currency: str = Field(default="USD", description="Base currency code")
    initial_balance: float = Field(..., ge=0.0, description="Initial starting cash balance")
    created_at: str = Field(..., description="ISO 8601 UTC timestamp of creation")
    status: PortfolioStatus = Field(default=PortfolioStatus.ACTIVE, description="Portfolio state enum")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class Position(BaseModel):
    """Immutable model representing an active open or partially closed position."""

    position_id: str = Field(
        ...,
        description="Unique position ID formatted as POS_<HEX16>",
        pattern=r"^POS_[A-Fa-f0-9]{16}$",
    )
    portfolio_id: str = Field(..., description="Parent portfolio ID")
    intent_id: str = Field(default="", description="Source execution intent ID")
    symbol: str = Field(..., description="Asset ticker symbol")
    side: PositionSide = Field(..., description="Position side enum (LONG, SHORT)")
    quantity: float = Field(..., gt=0.0, description="Current open net volume / lot quantity")
    initial_quantity: float = Field(..., gt=0.0, description="Original opened quantity")
    entry_price: float = Field(..., gt=0.0, description="Volume-weighted average entry price")
    current_price: float = Field(..., gt=0.0, description="Latest market price mark")
    stop_loss: float | None = Field(default=None, ge=0.0, description="Stop loss level")
    take_profit: float | None = Field(default=None, ge=0.0, description="Take profit level")
    opened_at: str = Field(..., description="ISO 8601 UTC timestamp of position opening")
    updated_at: str = Field(..., description="ISO 8601 UTC timestamp of latest price/quantity update")
    unrealized_pnl: float = Field(default=0.0, description="Current unrealized P/L")
    realized_pnl: float = Field(default=0.0, description="Accumulated realized P/L from partial closes")
    margin_used: float = Field(default=0.0, ge=0.0, description="Margin allocated to this position")
    status: PositionStatus = Field(default=PositionStatus.OPEN, description="Position status enum")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ClosedPosition(BaseModel):
    """Immutable model representing a fully closed position or closed partial lot."""

    closed_position_id: str = Field(
        ...,
        description="Unique closed position ID formatted as CLS_<HEX16>",
        pattern=r"^CLS_[A-Fa-f0-9]{16}$",
    )
    position_id: str = Field(..., description="Source parent position ID")
    portfolio_id: str = Field(..., description="Parent portfolio ID")
    symbol: str = Field(..., description="Asset ticker symbol")
    side: PositionSide = Field(..., description="Position side enum")
    quantity: float = Field(..., gt=0.0, description="Closed volume / lot quantity")
    entry_price: float = Field(..., gt=0.0, description="Average entry price of closed quantity")
    exit_price: float = Field(..., gt=0.0, description="Execution exit price")
    opened_at: str = Field(..., description="ISO 8601 UTC timestamp when position opened")
    closed_at: str = Field(..., description="ISO 8601 UTC timestamp when closed")
    realized_pnl: float = Field(..., description="Net realized profit / loss")
    close_reason: CloseReason = Field(default=CloseReason.MANUAL, description="Reason for closure")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class PortfolioSnapshot(BaseModel):
    """Immutable point-in-time state snapshot of portfolio metrics."""

    snapshot_id: str = Field(
        ...,
        description="Unique snapshot ID formatted as PSN_<HEX16>",
        pattern=r"^PSN_[A-Fa-f0-9]{16}$",
    )
    portfolio_id: str = Field(..., description="Target portfolio ID")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of snapshot")
    balance: float = Field(..., ge=0.0, description="Current realized cash balance")
    equity: float = Field(..., ge=0.0, description="Total portfolio equity (balance + unrealized PnL)")
    used_margin: float = Field(..., ge=0.0, description="Total margin currently tied up in open positions")
    free_margin: float = Field(..., ge=0.0, description="Unencumbered margin available")
    unrealized_pnl: float = Field(..., description="Total open unrealized P/L")
    realized_pnl: float = Field(..., description="Total cumulative realized P/L")
    open_positions_count: int = Field(..., ge=0, description="Number of active open positions")
    closed_positions_count: int = Field(..., ge=0, description="Number of closed positions")
    net_exposure: float = Field(..., description="Net dollar value exposure (Long - Short)")
    gross_exposure: float = Field(..., ge=0.0, description="Gross dollar value exposure (Long + Short)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExposureSummary(BaseModel):
    """Immutable summary of portfolio risk exposure metrics."""

    exposure_id: str = Field(
        ...,
        description="Unique exposure summary ID formatted as EXP_<HEX16>",
        pattern=r"^EXP_[A-Fa-f0-9]{16}$",
    )
    portfolio_id: str = Field(..., description="Target portfolio ID")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_long_exposure: float = Field(..., ge=0.0, description="Sum of long position mark values")
    total_short_exposure: float = Field(..., ge=0.0, description="Sum of short position mark values")
    net_exposure: float = Field(..., description="Net exposure (Long - Short)")
    gross_exposure: float = Field(..., ge=0.0, description="Gross exposure (Long + Short)")
    account_utilization: float = Field(..., ge=0.0, description="Account margin utilization fraction (Used Margin / Equity)")
    instrument_exposures: dict[str, float] = Field(default_factory=dict, description="Per-symbol net exposure dictionary")
    risk_concentration: dict[str, float] = Field(default_factory=dict, description="Per-symbol fraction of total gross exposure")
    max_instrument_concentration: float = Field(default=0.0, ge=0.0, le=1.0, description="Max concentration percentage for single symbol")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class PerformanceSummary(BaseModel):
    """Immutable summary of portfolio historical performance metrics."""

    performance_id: str = Field(
        ...,
        description="Unique performance summary ID formatted as PER_<HEX16>",
        pattern=r"^PER_[A-Fa-f0-9]{16}$",
    )
    portfolio_id: str = Field(..., description="Target portfolio ID")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_trades: int = Field(..., ge=0, description="Total number of closed positions/lots")
    winning_trades: int = Field(..., ge=0, description="Count of profitable trades")
    losing_trades: int = Field(..., ge=0, description="Count of loss-making trades")
    win_rate: float = Field(..., ge=0.0, le=1.0, description="Win rate ratio (winning / total)")
    loss_rate: float = Field(..., ge=0.0, le=1.0, description="Loss rate ratio (losing / total)")
    realized_pnl: float = Field(..., description="Total realized profit/loss")
    unrealized_pnl: float = Field(..., description="Total open unrealized profit/loss")
    total_pnl: float = Field(..., description="Total net profit/loss (realized + unrealized)")
    average_winner: float = Field(default=0.0, description="Average gain per winning trade")
    average_loser: float = Field(default=0.0, description="Average loss per losing trade")
    largest_winner: float = Field(default=0.0, description="Maximum single-trade profit")
    largest_loser: float = Field(default=0.0, description="Maximum single-trade loss")
    profit_factor: float = Field(default=0.0, ge=0.0, description="Gross profits divided by gross losses")
    expectancy: float = Field(default=0.0, description="Statistical profit expectancy per trade")
    running_drawdown: float = Field(default=0.0, ge=0.0, description="Current drawdown amount from peak equity")
    max_drawdown: float = Field(default=0.0, ge=0.0, description="Maximum historical drawdown amount")
    portfolio_return: float = Field(default=0.0, description="Return fraction relative to initial balance")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class AccountSnapshot(BaseModel):
    """Immutable snapshot of broker account financial metrics from portfolio perspective."""

    account_snapshot_id: str = Field(
        ...,
        description="Unique account snapshot ID formatted as ACC_<HEX16>",
        pattern=r"^ACC_[A-Fa-f0-9]{16}$",
    )
    portfolio_id: str = Field(..., description="Target portfolio ID")
    account_id: str = Field(..., description="Target broker account ID")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    balance: float = Field(..., ge=0.0, description="Realized cash balance")
    equity: float = Field(..., ge=0.0, description="Net equity (balance + unrealized PnL)")
    used_margin: float = Field(..., ge=0.0, description="Used margin capital")
    free_margin: float = Field(..., ge=0.0, description="Available free margin")
    margin_level: float = Field(default=0.0, ge=0.0, description="Margin level percentage (equity / used_margin * 100)")
    portfolio_value: float = Field(..., ge=0.0, description="Total portfolio marked value")
    buying_power: float = Field(..., ge=0.0, description="Available buying power capital")
    utilization_rate: float = Field(default=0.0, ge=0.0, description="Margin utilization percentage")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class PortfolioAudit(BaseModel):
    """Immutable audit trail log entry for portfolio lifecycle events."""

    audit_id: str = Field(
        ...,
        description="Unique portfolio audit entry ID formatted as PAD_<HEX16>",
        pattern=r"^PAD_[A-Fa-f0-9]{16}$",
    )
    portfolio_id: str = Field(..., description="Target portfolio ID")
    event_type: PortfolioAuditEventType = Field(..., description="Audit event classification enum")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    details: str = Field(..., description="Human-readable event details string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ReconciliationItem(BaseModel):
    """Immutable record of an individual reconciliation finding or discrepancy."""

    item_id: str = Field(..., description="Discrepancy item identifier")
    mismatch_type: ReconciliationMismatchType = Field(..., description="Mismatch type enum")
    symbol: str = Field(default="", description="Associated asset symbol")
    broker_value: Any = Field(default=None, description="Reported value from broker state")
    portfolio_value: Any = Field(default=None, description="Calculated value from GOAT portfolio state")
    description: str = Field(..., description="Detailed explanation of discrepancy")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")

    class Config:
        frozen = True
        extra = "forbid"
