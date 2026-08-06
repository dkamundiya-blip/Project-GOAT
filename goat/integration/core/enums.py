"""
Project GOAT v0.7 — Scientific Knowledge Integration & Evidence Graph Enums

Defines deterministic enums for knowledge node types, relationship types, conflict types, and severities.
"""

from enum import Enum


class KnowledgeNodeType(str, Enum):
    """Supported types of knowledge graph nodes."""

    HYPOTHESIS = "HYPOTHESIS"
    VALIDATION = "VALIDATION"
    EXPERIMENT = "EXPERIMENT"
    EVIDENCE = "EVIDENCE"
    THEORY = "THEORY"
    FINDING = "FINDING"
    FEATURE = "FEATURE"
    STUDY = "STUDY"
    PROGRAM = "PROGRAM"


class KnowledgeRelationship(str, Enum):
    """Deterministic relationships between knowledge nodes."""

    SUPPORTS = "SUPPORTS"
    EXTENDS = "EXTENDS"
    REFINES = "REFINES"
    GENERALIZES = "GENERALIZES"
    SPECIALIZES = "SPECIALIZES"
    CONTRADICTS = "CONTRADICTS"
    SUPERSEDES = "SUPERSEDES"
    DUPLICATES = "DUPLICATES"


class ConflictType(str, Enum):
    """Deterministic scientific conflict classifications."""

    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    DUPLICATED = "DUPLICATED"
    SUPERSEDED = "SUPERSEDED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ConflictSeverity(str, Enum):
    """Severity ratings for scientific conflict records."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
