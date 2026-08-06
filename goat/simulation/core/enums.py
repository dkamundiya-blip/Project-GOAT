"""
Project GOAT v0.7 — Scientific Simulation & Walk-Forward Validation Enums

Defines deterministic enums for validation status, simulation run status, and attribution categories.
"""

from enum import Enum


class ValidationStatus(str, Enum):
    """Deterministic validation decision status for scientific simulation & walk-forward results."""

    FAILED = "FAILED"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    VALIDATED = "VALIDATED"
    HIGH_CONFIDENCE_VALIDATED = "HIGH_CONFIDENCE_VALIDATED"


class SimulationRunStatus(str, Enum):
    """Deterministic status for simulation run execution."""

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AttributionCategory(str, Enum):
    """Classifications of performance contribution components."""

    EDGE = "EDGE"
    COMPOSITE = "COMPOSITE"
    REGIME = "REGIME"
    EVIDENCE = "EVIDENCE"
    KNOWLEDGE = "KNOWLEDGE"
    HYPOTHESIS = "HYPOTHESIS"
    VALIDATION = "VALIDATION"
