"""
Project GOAT v0.8 — Portfolio Core Enumerations
"""

from enum import Enum


class PositionSide(str, Enum):
    """Position side classification."""
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(str, Enum):
    """Lifecycle state of a position."""
    OPEN = "OPEN"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CLOSED = "CLOSED"


class PortfolioStatus(str, Enum):
    """Operational status of a portfolio."""
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    TERMINATED = "TERMINATED"


class CloseReason(str, Enum):
    """Reason for closing or partially closing a position."""
    MANUAL = "MANUAL"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    SIGNAL_EXIT = "SIGNAL_EXIT"
    PARTIAL_CLOSE = "PARTIAL_CLOSE"
    MARGIN_CALL = "MARGIN_CALL"
    RECONCILIATION_ADJUSTMENT = "RECONCILIATION_ADJUSTMENT"


class PortfolioAuditEventType(str, Enum):
    """Categories of portfolio audit trail events."""
    PORTFOLIO_CREATED = "PORTFOLIO_CREATED"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    PARTIAL_CLOSE = "PARTIAL_CLOSE"
    PRICE_UPDATED = "PRICE_UPDATED"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED"
    EXPOSURE_UPDATED = "EXPOSURE_UPDATED"
    PERFORMANCE_UPDATED = "PERFORMANCE_UPDATED"
    RECONCILIATION_PERFORMED = "RECONCILIATION_PERFORMED"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"


class ReconciliationMismatchType(str, Enum):
    """Types of discrepancies detected during broker reconciliation."""
    MISSING_POSITION = "MISSING_POSITION"
    DUPLICATE_POSITION = "DUPLICATE_POSITION"
    QUANTITY_MISMATCH = "QUANTITY_MISMATCH"
    PRICE_MISMATCH = "PRICE_MISMATCH"
    ACCOUNT_MISMATCH = "ACCOUNT_MISMATCH"
