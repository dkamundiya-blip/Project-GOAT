"""
Project GOAT v0.6 — Edge Intelligence & Validation Enums

Defines strongly typed enums required by SPEC.3 architecture.
"""

from __future__ import annotations

import enum


class EdgeScope(str, enum.Enum):
    """Scope applicability of a quantitative candidate edge."""

    UNIVERSAL = "UNIVERSAL"
    MARKET_SPECIFIC = "MARKET_SPECIFIC"
    TIMEFRAME_SPECIFIC = "TIMEFRAME_SPECIFIC"
    REGIME_SPECIFIC = "REGIME_SPECIFIC"
    COMPOSITE = "COMPOSITE"


class EdgeLifecycleStatus(str, enum.Enum):
    """Lifecycle status of a candidate edge in the research registry."""

    CANDIDATE = "CANDIDATE"
    UNDER_VALIDATION = "UNDER_VALIDATION"
    VALIDATED = "VALIDATED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    RETIRED = "RETIRED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ValidationStageOutcome(str, enum.Enum):
    """Four-state evaluation outcome of an individual validation stage."""

    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class EvidenceDimensionType(str, enum.Enum):
    """Dimension type classification of an atomic evidence observation."""

    DISCOVERY = "DISCOVERY"
    OOS = "OOS"
    WALK_FORWARD_FOLD = "WALK_FORWARD_FOLD"
    PARAMETER_NEIGHBOR = "PARAMETER_NEIGHBOR"
    REGIME = "REGIME"
    REPLICATION = "REPLICATION"
    CONFIRMATORY = "CONFIRMATORY"


class MultiplicityStrategy(str, enum.Enum):
    """Statistical procedure used for multiplicity and FDR control across families."""

    BENJAMINI_HOCHBERG = "BENJAMINI_HOCHBERG"
    BONFERRONI = "BONFERRONI"
    HOLM = "HOLM"
    NONE_ONLY_IF_SINGLE_PRESPECIFIED_TEST = "NONE_ONLY_IF_SINGLE_PRESPECIFIED_TEST"


class MetaAnalysisMethod(str, enum.Enum):
    """Statistical procedure used for cross-context meta-analysis combination."""

    FISHER_COMBINED_PROBABILITY = "FISHER_COMBINED_PROBABILITY"
    STOUFFER_Z_SCORE = "STOUFFER_Z_SCORE"
