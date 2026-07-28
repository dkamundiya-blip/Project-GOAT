"""
Project GOAT v0.6 — Edge Reporting Error Taxonomy

Defines explicit exception hierarchy for ValidationReport construction, identity calculation,
cryptographic integrity verification, and evidence package persistence.
"""

from __future__ import annotations


class EdgeReportingError(Exception):
    """Base exception for all Edge Reporting errors."""


class ReportBuildError(EdgeReportingError):
    """Raised when a ValidationReport cannot be constructed from persisted data."""


class ReportIntegrityError(EdgeReportingError):
    """Raised when scientific identity, evidence payload hash, or stage progression fails verification."""


class ReportIdentityError(EdgeReportingError):
    """Raised when RPT_<HEX16> identity computation or recomputation fails."""


class EvidenceIntegrityError(EdgeReportingError):
    """Raised when atomic evidence payload hash (EVP_) or ID (EVD_) fails validation."""


class UnsupportedReportSchemaError(EdgeReportingError):
    """Raised when report_schema_version or package_schema_version is unsupported or incompatible."""


class SecurityViolationError(EdgeReportingError):
    """Raised when path traversal or forbidden character injection is detected."""


class PackageIntegrityError(EdgeReportingError):
    """Raised when evidence package manifest, file checksum, or structural verification fails."""


class PackageCollisionError(EdgeReportingError):
    """Raised when attempting to overwrite an existing conflicting scientific evidence package."""
