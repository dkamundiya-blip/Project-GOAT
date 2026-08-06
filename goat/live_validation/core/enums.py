"""
Project GOAT v0.9 — Core Enums for Controlled Live Scientific Validation Subsystem
"""

from enum import Enum


class ValidationStatus(str, Enum):
    """Lifecycle status of a live validation session or candidate."""

    PENDING = "PENDING"
    ELIGIBLE = "ELIGIBLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class ValidationDecisionOutcome(str, Enum):
    """Scientific decision outcome derived during live validation."""

    SUPPORTED = "SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    FAILED = "FAILED"
    PROMOTION_RECOMMENDED = "PROMOTION_RECOMMENDED"
    RETIREMENT_RECOMMENDED = "RETIREMENT_RECOMMENDED"


class MonitoringStatus(str, Enum):
    """Real-time execution monitoring health status."""

    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
