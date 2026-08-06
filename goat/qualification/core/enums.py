"""
Project GOAT v0.7 — Scientific Qualification & Decision Readiness Enums

Defines deterministic enums for qualification states, readiness levels, gate categories, and blocking conditions.
"""

from enum import Enum


class QualificationState(str, Enum):
    """Deterministic qualification states for scientific edges/composites."""

    QUALIFIED = "QUALIFIED"
    DISQUALIFIED = "DISQUALIFIED"
    CONDITIONAL_QUALIFICATION = "CONDITIONAL_QUALIFICATION"


class ReadinessLevel(str, Enum):
    """Deterministic decision readiness levels (authorizes future phases only—NOT live trading)."""

    NOT_READY = "NOT_READY"
    EARLY_RESEARCH = "EARLY_RESEARCH"
    EXPERIMENTAL = "EXPERIMENTAL"
    CANDIDATE = "CANDIDATE"
    READY_FOR_SIMULATION = "READY_FOR_SIMULATION"
    READY_FOR_FORWARD_TESTING = "READY_FOR_FORWARD_TESTING"


class GateCategory(str, Enum):
    """Classifications of qualification gates."""

    EVIDENCE = "EVIDENCE"
    KNOWLEDGE = "KNOWLEDGE"
    STABILITY = "STABILITY"
    REPRODUCIBILITY = "REPRODUCIBILITY"
    CONFLICT = "CONFLICT"
    REGIME = "REGIME"
    EXPLAINABILITY = "EXPLAINABILITY"
    CONFIDENCE = "CONFIDENCE"
    MATURITY = "MATURITY"
    DATA = "DATA"


class BlockingConditionType(str, Enum):
    """Classifications of blocking conditions preventing decision readiness advancement."""

    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    WEAK_REPRODUCIBILITY = "WEAK_REPRODUCIBILITY"
    INCOMPLETE_EXPLAINABILITY = "INCOMPLETE_EXPLAINABILITY"
    LOW_SCIENTIFIC_CONFIDENCE = "LOW_SCIENTIFIC_CONFIDENCE"
    REGIME_MISMATCH = "REGIME_MISMATCH"
    COMPOSITE_INSTABILITY = "COMPOSITE_INSTABILITY"
    KNOWLEDGE_GAPS = "KNOWLEDGE_GAPS"
    INCOMPLETE_VALIDATION = "INCOMPLETE_VALIDATION"
