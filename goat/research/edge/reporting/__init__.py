"""
Project GOAT v0.6 — Edge Validation Reporting & Audit Packaging Infrastructure

Provides canonical in-memory report models, deterministic identity calculation,
persisted-state report building, cryptographic integrity verification, and atomic filesystem evidence packages.
"""

from goat.research.edge.reporting.builder import ValidationReportBuilder, sort_canonical_evidence
from goat.research.edge.reporting.exceptions import (
    EdgeReportingError,
    EvidenceIntegrityError,
    PackageCollisionError,
    PackageIntegrityError,
    ReportBuildError,
    ReportIdentityError,
    ReportIntegrityError,
    SecurityViolationError,
    UnsupportedReportSchemaError,
)
from goat.research.edge.reporting.identity import compute_report_id
from goat.research.edge.reporting.integrity import ReportIntegrityVerifier
from goat.research.edge.reporting.models import (
    ConfirmatoryAuditModel,
    DataProvenanceModel,
    EdgeIdentityModel,
    HypothesisIdentityModel,
    IntegrityMetadataModel,
    PolicySpecificationModel,
    SoftwareProvenanceModel,
    StageSummaryModel,
    ValidationReport,
    ValidationSummaryModel,
)
from goat.research.edge.reporting.package import EvidencePackageWriter
from goat.research.edge.reporting.package_integrity import (
    PACKAGE_SCHEMA_VERSION,
    EvidencePackageVerifier,
    validate_path_component,
)
from goat.research.edge.reporting.serializer import render_report_markdown, serialize_report_to_json

__all__ = [
    "ValidationReport",
    "ValidationReportBuilder",
    "ReportIntegrityVerifier",
    "EvidencePackageWriter",
    "EvidencePackageVerifier",
    "PACKAGE_SCHEMA_VERSION",
    "validate_path_component",
    "compute_report_id",
    "serialize_report_to_json",
    "render_report_markdown",
    "sort_canonical_evidence",
    "EdgeIdentityModel",
    "HypothesisIdentityModel",
    "PolicySpecificationModel",
    "DataProvenanceModel",
    "ValidationSummaryModel",
    "StageSummaryModel",
    "ConfirmatoryAuditModel",
    "SoftwareProvenanceModel",
    "IntegrityMetadataModel",
    "EdgeReportingError",
    "ReportBuildError",
    "ReportIntegrityError",
    "ReportIdentityError",
    "EvidenceIntegrityError",
    "UnsupportedReportSchemaError",
    "SecurityViolationError",
    "PackageIntegrityError",
    "PackageCollisionError",
]
