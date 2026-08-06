"""
Project GOAT v0.7 — Feature Registry Models

Defines immutable RegistryRecord and RegistryAuditEvent models tracking scientific identities,
metadata, capability contracts, registration status, and audit provenance.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field

from goat.features.core.contracts import (
    ComputationalConstraints,
    ExecutionCostMetadata,
    FeatureCapabilityContract,
    FeatureInputContract,
    FeatureOutputContract,
)
from goat.features.core.enums import DeprecationStatus
from goat.features.core.metadata import FeatureMetadata


class RegistrationStatus(str, enum.Enum):
    """Operational status of feature registration."""
    PENDING = "pending"
    REGISTERED = "registered"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


class ValidationStatus(str, enum.Enum):
    """Quality gate validation status."""
    UNVALIDATED = "unvalidated"
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONALLY_PASSED = "conditionally_passed"


class RegistryRecord(BaseModel):
    """Immutable record stored in GOAT's Feature Registry."""

    feature_id: str = Field(..., description="Unique Feature ID (FEAT_<HEX16>)")
    scientific_fingerprint: str = Field(..., description="Scientific Feature Fingerprint (FPT_<HEX64>)")
    canonical_hash: str = Field(..., description="SHA-256 canonical AST hash digest")
    semantic_version: str = Field(..., description="Semantic version string (e.g. 1.0.0)")

    feature_metadata: FeatureMetadata = Field(..., description="Full immutable FeatureMetadata record")
    capability_contract: FeatureCapabilityContract = Field(..., description="Feature capability contract")
    input_contract: FeatureInputContract = Field(..., description="Input schema and asset constraints")
    output_contract: FeatureOutputContract = Field(..., description="Output shape and dtype contract")
    execution_constraints: ComputationalConstraints = Field(..., description="History and lookback bounds")

    dependency_spec: list[str] = Field(default_factory=list, description="List of upstream Feature IDs")
    registration_timestamp: str = Field(..., description="ISO-8601 UTC registration timestamp")
    registry_version: str = Field(default="1.0.0", description="Registry schema version")
    registration_status: RegistrationStatus = Field(
        default=RegistrationStatus.REGISTERED,
        description="Registration lifecycle status",
    )
    deprecation_state: DeprecationStatus = Field(
        default=DeprecationStatus.ACTIVE,
        description="Operational deprecation status",
    )
    validation_status: ValidationStatus = Field(
        default=ValidationStatus.UNVALIDATED,
        description="Quality gate validation status",
    )
    registry_provenance: str = Field(default="system", description="Source or author of registration")
    registry_notes: str = Field(default="", description="Audit or scientific research notes")

    class Config:
        frozen = True
        extra = "forbid"


class RegistryAuditEvent(BaseModel):
    """Immutable append-only audit event record."""

    event_id: str = Field(..., description="Unique audit event ID")
    feature_id: str = Field(..., description="Target Feature ID")
    scientific_fingerprint: str = Field(..., description="Scientific Feature Fingerprint")
    event_type: str = Field(..., description="Type of event (REGISTER, DEPRECATE, VALIDATE, MIGRATE)")
    timestamp: str = Field(..., description="ISO-8601 UTC event timestamp")
    actor: str = Field(default="system", description="Entity initiating event")
    details: dict[str, Any] = Field(default_factory=dict, description="Event metadata details")

    class Config:
        frozen = True
        extra = "forbid"
