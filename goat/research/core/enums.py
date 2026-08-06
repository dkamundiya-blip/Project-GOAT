"""
Project GOAT v0.9 — Core Enums for Scientific Research & Hypothesis Subsystem
"""

from enum import Enum


class HypothesisStatus(str, Enum):
    """Lifecycle status of a scientific hypothesis."""

    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"
    RETIRED = "RETIRED"


class HypothesisPriority(str, Enum):
    """Priority classification for hypothesis evaluation."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceLevel(str, Enum):
    """Scientific evidence hierarchy level (Level 0 through Level 5)."""

    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
