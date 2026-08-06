"""
Project GOAT v0.9 — Core Enums for Statistical Evaluation Subsystem
"""

from enum import Enum


class EvaluationStatus(str, Enum):
    """Lifecycle status of a statistical evaluation process."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class ScientificDecision(str, Enum):
    """Scientific decision regarding a hypothesis based on statistical evidence."""

    SUPPORTED = "SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REJECTED = "REJECTED"
    REQUIRES_MORE_DATA = "REQUIRES_MORE_DATA"


class EvaluationConfidence(str, Enum):
    """Qualitative confidence rating of statistical evaluation."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
