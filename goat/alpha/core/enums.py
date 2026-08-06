"""
Project GOAT v0.7 — Scientific Alpha & Quantitative Edge Enums

Defines deterministic enums for edge maturity levels, evidence sources, and ranking rules.
"""

from enum import Enum


class EdgeMaturity(str, Enum):
    """Deterministic maturity stages for candidate quantitative edges."""

    NEW = "NEW"
    EXPERIMENTAL = "EXPERIMENTAL"
    EMERGING = "EMERGING"
    VALIDATED = "VALIDATED"
    MATURE = "MATURE"
    FOUNDATIONAL = "FOUNDATIONAL"


class EvidenceSourceType(str, Enum):
    """Source classifications for edge supporting evidence."""

    VALIDATION = "VALIDATION"
    CLUSTER = "CLUSTER"
    PATTERN = "PATTERN"
    TREND = "TREND"
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT = "EXPERIMENT"
    STUDY = "STUDY"
    META_ANALYSIS = "META_ANALYSIS"


class RankingRuleType(str, Enum):
    """Deterministic ranking rules applied during edge ranking."""

    OVERALL_QUALITY = "OVERALL_QUALITY"
    REPRODUCIBILITY_FIRST = "REPRODUCIBILITY_FIRST"
    MATURITY_WEIGHTED = "MATURITY_WEIGHTED"
    CONTRADICTION_PENALIZED = "CONTRADICTION_PENALIZED"
