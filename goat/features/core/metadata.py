"""
Project GOAT v0.7 — Feature Metadata Specification

Defines the immutable FeatureMetadata domain model tracking mathematical specifications,
dependencies, computational footprint, provenance, Scientific Feature Fingerprint (FPT_<HEX64>),
and Feature Capability Contracts (Step 4.1B-R2).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.features.core.contracts import (
    ComputationalConstraints,
    ExecutionCostMetadata,
    FeatureCapabilityContract,
    FeatureInputContract,
    FeatureOutputContract,
)
from goat.features.core.enums import (
    DataType,
    DeprecationStatus,
    DeterminismClass,
    StationarityType,
    TaxonomyCategory,
)


class FeatureMetadata(BaseModel):
    """Immutable metadata record for a registered GOAT feature."""

    # Registry Identity
    feature_id: str = Field(
        ...,
        description="Unique Feature ID formatted as FEAT_<HEX16>",
        pattern=r"^FEAT_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(
        ...,
        description="Cryptographic SHA-256 hash of AST, parameters, and types",
        pattern=r"^[A-Fa-f0-9]{64}$",
    )

    # Scientific Feature Identity (Step 4.1B-R1)
    scientific_fingerprint: str = Field(
        ...,
        description="Permanent scientific identity formatted as FPT_<HEX64>",
        pattern=r"^FPT_[A-Fa-f0-9]{64}$",
    )
    fingerprint_version: str = Field(
        default="1.0.0",
        description="Fingerprint specification version",
    )
    fingerprint_algorithm: str = Field(
        default="SHA256_CANONICAL_V1",
        description="Canonical hashing algorithm employed",
    )
    fingerprint_timestamp: str = Field(
        ...,
        description="ISO-8601 UTC timestamp when fingerprint was computed",
    )
    fingerprint_verified: bool = Field(
        default=True,
        description="Fail-closed verification status of scientific fingerprint",
    )

    # Capability Contracts & Computational Constraints (Step 4.1B-R2)
    capabilities: FeatureCapabilityContract = Field(
        default_factory=FeatureCapabilityContract,
        description="Immutable capability declarations",
    )
    constraints: ComputationalConstraints = Field(
        default_factory=ComputationalConstraints,
        description="Immutable history and window constraints",
    )
    output_contract: FeatureOutputContract = Field(
        default_factory=FeatureOutputContract,
        description="Immutable output dimensionality and shape contract",
    )
    input_contract: FeatureInputContract = Field(
        default_factory=FeatureInputContract,
        description="Immutable input column and market requirements",
    )
    cost_metadata: ExecutionCostMetadata = Field(
        default_factory=ExecutionCostMetadata,
        description="Descriptive computational complexity metrics",
    )

    # Definition & Classification
    name: str = Field(..., description="Human-readable feature name")
    version: str = Field(..., description="Semantic version string (e.g. 1.0.0)")
    taxonomy_category: TaxonomyCategory = Field(..., description="Primary taxonomy classification")
    taxonomy_subcategory: str = Field(default="general", description="Fine-grained taxonomy subcategory")
    dependencies: list[str] = Field(default_factory=list, description="List of upstream feature IDs required")
    mathematical_definition: str = Field(..., description="LaTeX mathematical formula representation")
    algorithmic_spec: str = Field(..., description="Algorithmic pseudocode or step-by-step description")
    input_requirements: dict[str, Any] = Field(
        default_factory=dict,
        description="Minimum history depth, required columns, data resolution",
    )
    output_type: DataType = Field(default=DataType.FLOAT64, description="Output data type classification")
    value_range: tuple[float | None, float | None] = Field(
        default=(None, None),
        description="Theoretical minimum and maximum output boundaries (None indicates infinity)",
    )
    computational_cost: dict[str, Any] = Field(
        default_factory=dict,
        description="Time complexity and memory footprint metrics",
    )
    determinism_class: DeterminismClass = Field(
        default=DeterminismClass.IEEE_754_STRICT,
        description="Numerical determinism certification",
    )
    applicable_instruments: list[str] = Field(
        default_factory=lambda: ["ALL"],
        description="Applicable asset classes or instrument identifiers",
    )
    applicable_timeframes: list[str] = Field(
        default_factory=lambda: ["ALL"],
        description="Applicable sampling bar resolutions",
    )
    creation_timestamp: str = Field(..., description="ISO-8601 UTC creation timestamp")
    provenance_generator: str = Field(..., description="Author or generator subroutine identifier")
    expected_stationarity: StationarityType = Field(
        default=StationarityType.STATIONARY,
        description="Expected statistical stationarity property",
    )
    known_failure_modes: list[str] = Field(
        default_factory=list,
        description="Scenarios where calculation may fail or break mathematically",
    )
    deprecation_status: DeprecationStatus = Field(
        default=DeprecationStatus.ACTIVE,
        description="Operational lifecycle status",
    )

    class Config:
        frozen = True
        extra = "forbid"
