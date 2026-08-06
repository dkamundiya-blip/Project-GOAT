"""
Project GOAT v0.7 — Composite Edge & Portfolio Intelligence Enums

Defines deterministic enums for synthesis modes, conflict severity, and ranking strategies.
"""

from enum import Enum


class SynthesisMode(str, Enum):
    """Modes of composite edge synthesis."""

    PAIRWISE = "PAIRWISE"
    MULTI_EDGE = "MULTI_EDGE"
    REGIME_TARGETED = "REGIME_TARGETED"


class ConflictSeverity(str, Enum):
    """Severity levels of detected conflicts between participating edges."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL_REJECTION = "CRITICAL_REJECTION"


class RankingStrategy(str, Enum):
    """Deterministic ranking strategies for CompositeEdges."""

    OVERALL_QUALITY = "OVERALL_QUALITY"
    SYNERGY_FIRST = "SYNERGY_FIRST"
    DIVERSITY_WEIGHTED = "DIVERSITY_WEIGHTED"
    CONTRADICTION_PENALIZED = "CONTRADICTION_PENALIZED"
