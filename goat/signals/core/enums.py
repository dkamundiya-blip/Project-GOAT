"""
Project GOAT v0.7 — Scientific Signal Engine Enums

Defines deterministic enums for signal direction, lifecycle state, payload format, and execution status.
"""

from enum import Enum


class SignalDirection(str, Enum):
    """Trading direction for generated signals."""

    BUY = "BUY"
    SELL = "SELL"
    FLAT = "FLAT"


class SignalLifecycleState(str, Enum):
    """Deterministic state machine levels for trading signal lifecycle."""

    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    READY_FOR_DELIVERY = "READY_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"
    INVALIDATED = "INVALIDATED"


class PayloadFormat(str, Enum):
    """Supported deterministic payload formatting targets."""

    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    NOTIFICATION = "NOTIFICATION"
    WEBHOOK = "WEBHOOK"
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"
    PUSH = "PUSH"


class ExecutionStatus(str, Enum):
    """Evaluation state for signal execution readiness."""

    READY = "READY"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
