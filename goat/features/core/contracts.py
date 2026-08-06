"""
Project GOAT v0.7 — Feature Capability Contracts & Computational Reproducibility

Defines immutable capability declarations, computational constraints, input/output contracts,
execution cost metadata, and fail-closed validation logic for GOAT features.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.features.core.enums import DataType, DeterminismClass


class FeatureCapabilityContract(BaseModel):
    """Immutable declaration of feature computational execution capabilities."""

    supports_vectorized_execution: bool = Field(
        default=True,
        description="Whether feature supports high-speed SIMD/vectorized array computation",
    )
    supports_streaming_execution: bool = Field(
        default=False,
        description="Whether feature supports single-bar incremental streaming updates",
    )
    requires_fixed_window: bool = Field(
        default=False,
        description="Whether calculation strictly requires a fixed historical bar count",
    )
    supports_incremental_update: bool = Field(
        default=False,
        description="Whether internal state can be updated incrementally without full recomputation",
    )
    requires_complete_history: bool = Field(
        default=False,
        description="Whether calculation requires complete historical dataset without truncation",
    )
    deterministic_execution: bool = Field(
        default=True,
        description="Guarantees exact bitwise deterministic outputs across runs",
    )
    pure_function: bool = Field(
        default=True,
        description="Function has zero side effects and depends solely on input parameters",
    )
    parallel_safe: bool = Field(
        default=True,
        description="Calculation can be safely executed across parallel thread/process workers",
    )
    cacheable: bool = Field(
        default=True,
        description="Intermediate outputs can be cached across sub-graph evaluation DAGs",
    )
    window_size_policy: str = Field(
        default="fixed",
        description="Window policy classification: 'fixed', 'rolling', or 'expanding'",
    )

    class Config:
        frozen = True
        extra = "forbid"


class ComputationalConstraints(BaseModel):
    """Immutable computational constraints and history depth requirements."""

    minimum_history: int = Field(
        default=1,
        ge=1,
        description="Minimum number of historical bars required for valid calculation",
    )
    maximum_history: int | None = Field(
        default=None,
        description="Maximum historical bar limit (None indicates no upper limit)",
    )
    fixed_window: int | None = Field(
        default=None,
        description="Exact fixed window bar depth required if requires_fixed_window is True",
    )
    rolling_window: int | None = Field(
        default=None,
        description="Rolling window lookback depth N",
    )
    expanding_window: bool = Field(
        default=False,
        description="Whether window expands monotonically from bar 0 to bar t",
    )
    lookback_required: int = Field(
        default=0,
        ge=0,
        description="Number of past bars needed before producing valid non-null outputs",
    )
    warmup_period: int = Field(
        default=0,
        ge=0,
        description="Initial bar count before output reaches numerical stability",
    )

    class Config:
        frozen = True
        extra = "forbid"


class FeatureOutputContract(BaseModel):
    """Immutable declaration of feature output structure and numerical policies."""

    output_dimension: str = Field(
        default="vector",
        description="Output dimensionality: 'scalar', 'vector', or 'matrix'",
    )
    dtype: DataType = Field(
        default=DataType.FLOAT64,
        description="Numpy output data type",
    )
    shape_constraints: str = Field(
        default="(N,)",
        description="Formal output array shape constraint string",
    )
    missing_value_policy: str = Field(
        default="zero_fill",
        description="Policy for missing bar data: 'zero_fill', 'propagate', 'drop', or 'raise_error'",
    )
    nan_policy: str = Field(
        default="zero_fill",
        description="Policy for NaN values: 'zero_fill', 'propagate', or 'raise_error'",
    )
    infinity_policy: str = Field(
        default="clip",
        description="Policy for +/- Inf values: 'clip', 'propagate', or 'raise_error'",
    )
    units: str | None = Field(
        default=None,
        description="Measurement units if applicable (e.g. 'ratio', 'currency', 'volatility')",
    )

    class Config:
        frozen = True
        extra = "forbid"


class FeatureInputContract(BaseModel):
    """Immutable specification of feature input schema and asset requirements."""

    required_fields: list[str] = Field(
        default_factory=lambda: ["close"],
        description="Required OHLCV column names in input market data window",
    )
    optional_fields: list[str] = Field(
        default_factory=list,
        description="Optional input column names",
    )
    supported_frequencies: list[str] = Field(
        default_factory=lambda: ["ALL"],
        description="Supported sampling frequencies (e.g. ['5m', '1h', '1d'])",
    )
    supported_market_types: list[str] = Field(
        default_factory=lambda: ["ALL"],
        description="Supported market types (e.g. ['SPOT', 'FUTURES'])",
    )
    supported_asset_classes: list[str] = Field(
        default_factory=lambda: ["ALL"],
        description="Supported asset classes (e.g. ['FX', 'CRYPTO', 'EQUITIES'])",
    )
    supported_timeframes: list[str] = Field(
        default_factory=lambda: ["ALL"],
        description="Supported bar timeframes",
    )

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionCostMetadata(BaseModel):
    """Descriptive execution cost and complexity metadata."""

    expected_complexity: str = Field(
        default="O(N)",
        description="Big-O algorithmic time complexity notation",
    )
    memory_complexity: str = Field(
        default="O(N)",
        description="Big-O memory footprint notation",
    )
    estimated_allocation_behaviour: str = Field(
        default="single_allocation",
        description="Memory allocation profile: 'single_allocation', 'reallocation', or 'zero_copy'",
    )
    cache_suitability: bool = Field(
        default=True,
        description="Suitability for in-memory cache storage",
    )
    deterministic_computational_class: DeterminismClass = Field(
        default=DeterminismClass.IEEE_754_STRICT,
        description="Determinism level certification",
    )

    class Config:
        frozen = True
        extra = "forbid"


def validate_feature_capability_contract(metadata: Any) -> bool:
    """Validate that a feature's capability declarations and constraints are consistent.

    Fail-closed validation rules:
    - Streaming execution cannot require complete history.
    - Rolling window policy requires lookback_required > 0.
    - Scalar output dimension cannot have vector shape '(N,)'.
    - Fixed window requirement requires fixed_window setting > 0.

    Returns:
        True if valid. Raises ValueError if inconsistent.
    """
    caps = getattr(metadata, "capabilities", None)
    constraints = getattr(metadata, "constraints", None)
    out_contract = getattr(metadata, "output_contract", None)

    if caps is None or constraints is None or out_contract is None:
        raise ValueError("Missing capability contract, constraints, or output_contract in metadata")

    # Rule 1: Streaming execution vs complete history contradiction
    if caps.supports_streaming_execution and caps.requires_complete_history:
        raise ValueError("Inconsistent capability contract: streaming execution cannot require complete history")

    # Rule 2: Rolling window policy vs lookback
    if caps.window_size_policy == "rolling" and constraints.lookback_required == 0:
        raise ValueError("Inconsistent capability contract: rolling window policy requires lookback_required > 0")

    # Rule 3: Scalar dimension vs shape
    if out_contract.output_dimension == "scalar" and out_contract.shape_constraints == "(N,)":
        raise ValueError("Inconsistent capability contract: scalar output cannot have vector shape '(N,)'")

    # Rule 4: Fixed window constraint
    if caps.requires_fixed_window and (constraints.fixed_window is None or constraints.fixed_window <= 0):
        raise ValueError("Inconsistent capability contract: requires_fixed_window requires valid fixed_window > 0")

    return True
