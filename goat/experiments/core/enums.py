"""
Project GOAT v0.9 — Core Enums for Scientific Experiment Subsystem
"""

from enum import Enum


class ExperimentStatus(str, Enum):
    """Lifecycle status of a scientific experiment."""

    # v0.9 Statuses
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"

    # v0.7 Legacy Statuses (for backward compatibility with frozen steps)
    PROPOSED = "proposed"
    SCHEDULED = "scheduled"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ABORTED = "aborted"


class ExperimentType(str, Enum):
    """Classification of scientific experiment type."""

    SIMULATION = "SIMULATION"
    REPLAY = "REPLAY"
    LIVE_OBSERVATION = "LIVE_OBSERVATION"
    MANUAL = "MANUAL"
    WALK_FORWARD = "WALK_FORWARD"


class ExperimentPriority(str, Enum):
    """Execution scheduling priority rating."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
