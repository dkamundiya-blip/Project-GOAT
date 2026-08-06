"""
Project GOAT v0.7 — Scientific Meta-Analysis Enums

Defines deterministic enums for cluster types, pattern categories, trend directions, and domain statuses.
"""

from enum import Enum


class ClusterType(str, Enum):
    """Supported types of deterministic research clusters."""

    THEME = "THEME"
    VALIDATION = "VALIDATION"
    EVIDENCE = "EVIDENCE"
    EXPERIMENT = "EXPERIMENT"
    STUDY = "STUDY"
    KNOWLEDGE = "KNOWLEDGE"


class PatternCategory(str, Enum):
    """Classifications of discovered research patterns."""

    RECURRING_EVIDENCE = "RECURRING_EVIDENCE"
    RECURRING_RELATIONSHIP = "RECURRING_RELATIONSHIP"
    FREQUENTLY_VALIDATED = "FREQUENTLY_VALIDATED"
    LONG_TERM_REPRODUCIBILITY = "LONG_TERM_REPRODUCIBILITY"
    STABLE_OBSERVATION = "STABLE_OBSERVATION"
    SCIENTIFIC_ANOMALY = "SCIENTIFIC_ANOMALY"
    WEAK_EVIDENCE_REGION = "WEAK_EVIDENCE_REGION"
    EMERGING_DOMAIN = "EMERGING_DOMAIN"


class TrendDirection(str, Enum):
    """Directions for research trends."""

    GROWING = "GROWING"
    DECLINING = "DECLINING"
    STABLE = "STABLE"
    CONFLICTING = "CONFLICTING"
    UNRESOLVED = "UNRESOLVED"
    DORMANT = "DORMANT"


class ResearchDomainStatus(str, Enum):
    """Maturity classifications of research domains."""

    EMERGING = "EMERGING"
    MATURING = "MATURING"
    STABLE = "STABLE"
    CONTRADICTED = "CONTRADICTED"
    DORMANT = "DORMANT"
