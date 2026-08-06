"""
Project GOAT v0.7 — Scientific Hypothesis Validation Enums

Defines ValidationState and DecisionType enums for the hypothesis validation lifecycle.
"""

from __future__ import annotations

from enum import Enum


class ValidationState(str, Enum):
    """Lifecycle states for scientific hypothesis validation."""

    PENDING = "pending"
    COLLECTING_EVIDENCE = "collecting_evidence"
    EVALUATING = "evaluating"
    DECIDED = "decided"
    ARCHIVED = "archived"


class DecisionType(str, Enum):
    """Final deterministic validation decision outcomes."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"
    NEEDS_MORE_DATA = "needs_more_data"
    INVALID_HYPOTHESIS = "invalid_hypothesis"
