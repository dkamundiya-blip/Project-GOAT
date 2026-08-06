"""
Project GOAT v0.7 — Evidence Synthesis Enums

Defines ContradictionSeverity and ReplicationQuality enums for scientific evidence synthesis.
"""

from __future__ import annotations

from enum import Enum


class ContradictionSeverity(str, Enum):
    """Severity classification of an evidence contradiction finding."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReplicationQuality(str, Enum):
    """Quality classification of a scientific evidence replication."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXACT = "exact"
