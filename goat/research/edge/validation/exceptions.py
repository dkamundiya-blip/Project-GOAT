"""
Project GOAT v0.6 — Validation Engine Exception Taxonomy

Defines explicit error taxonomy for multi-stage edge validation operations.
"""

from __future__ import annotations


class EdgeValidationError(Exception):
    """Base exception for all edge validation failures."""


class StageValidationError(EdgeValidationError):
    """Raised when a specific validation stage fails execution or input checks."""


class InsufficientEvidenceError(EdgeValidationError):
    """Raised when sample count or observations are insufficient to evaluate evidence."""


class MultiplicityFamilyError(EdgeValidationError):
    """Raised when candidate family registration or FDR multiplicity coordination fails."""


class TemporalLeakageError(EdgeValidationError):
    """Raised when non-causal temporal or forward-outcome leakage is detected."""


class HoldoutAccessError(EdgeValidationError):
    """Raised when sealed holdout partition access is attempted without authorization or out of sequence."""


class ValidationStateError(EdgeValidationError):
    """Raised when an illegal validation lifecycle state transition is attempted."""


class EvidenceGenerationError(EdgeValidationError):
    """Raised when atomic evidence record generation fails structural validation."""
