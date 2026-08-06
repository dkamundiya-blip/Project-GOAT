"""
Project GOAT v0.9 — Immutable Pydantic V2 Domain Models for Microstructure Subsystem
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.microstructure.core.enums import (
    ExecutionQualityRating,
    JumpDirection,
    MicrostructureMetricType,
    ObservationCategory,
    SyntheticIndexType,
    VolatilityRegime,
)


class MicrostructureObservation(BaseModel):
    """Observable raw market microstructure metric measurement."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    observation_id: str = Field(..., description="Deterministic observation ID with prefix MSO_")
    metric_type: MicrostructureMetricType = Field(..., description="Type of measured metric")
    category: ObservationCategory = Field(..., description="Observation domain category")
    symbol: str = Field(..., description="Deriv symbol identifier")
    index_type: SyntheticIndexType = Field(..., description="Synthetic index category classification")
    timestamp: str = Field(..., description="ISO-8601 timestamp of measurement")
    value: float = Field(..., description="Numerical metric value")
    unit: str = Field(..., description="Unit of measure")
    window_seconds: int = Field(default=60, ge=1, description="Observation window size in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class VolatilityProfile(BaseModel):
    """Immutable Volatility Profile for a Synthetic Index."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str = Field(..., description="Deterministic profile ID with prefix VLP_")
    symbol: str = Field(..., description="Deriv symbol identifier")
    index_type: SyntheticIndexType = Field(..., description="Synthetic index classification")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    window_seconds: int = Field(default=300, ge=1, description="Window size in seconds")
    realized_volatility: float = Field(..., ge=0.0, description="Realized volatility measure")
    volatility_clustering_coeff: float = Field(..., description="Autocorrelation of absolute returns")
    volatility_persistence: float = Field(..., description="Decay / persistence rate of volatility")
    expansion_ratio: float = Field(..., ge=0.0, description="Peak rolling vol / mean vol ratio")
    contraction_ratio: float = Field(..., ge=0.0, description="Trough rolling vol / mean vol ratio")
    regime: VolatilityRegime = Field(..., description="Classified volatility regime")
    observation_ids: list[str] = Field(default_factory=list, description="IDs of component observations")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class JumpProfile(BaseModel):
    """Immutable Jump Profile for a Synthetic Index (Boom, Crash, Jump, Volatility, Step)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str = Field(..., description="Deterministic profile ID with prefix JMP_")
    symbol: str = Field(..., description="Deriv symbol identifier")
    index_type: SyntheticIndexType = Field(..., description="Synthetic index classification")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    window_seconds: int = Field(default=300, ge=1, description="Window size in seconds")
    jump_count: int = Field(..., ge=0, description="Total count of identified price jumps")
    jump_frequency: float = Field(..., ge=0.0, description="Jumps per unit time (jumps/min)")
    mean_jump_magnitude: float = Field(..., ge=0.0, description="Average magnitude of detected jumps")
    max_jump_magnitude: float = Field(..., ge=0.0, description="Maximum jump magnitude in window")
    mean_jump_spacing_sec: float = Field(..., ge=0.0, description="Average spacing between jumps in seconds")
    jump_persistence: float = Field(..., description="Jump magnitude decay / persistence factor")
    jump_clustering_index: float = Field(..., ge=0.0, description="Fano factor of jump arrival process")
    dominant_direction: JumpDirection = Field(..., description="Dominant price jump direction")
    observation_ids: list[str] = Field(default_factory=list, description="IDs of component observations")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class LiquidityProfile(BaseModel):
    """Immutable Liquidity Profile measuring quote continuity, spreads, and tick density."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str = Field(..., description="Deterministic profile ID with prefix LIQ_")
    symbol: str = Field(..., description="Deriv symbol identifier")
    index_type: SyntheticIndexType = Field(..., description="Synthetic index classification")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    window_seconds: int = Field(default=300, ge=1, description="Window size in seconds")
    average_spread: float = Field(..., ge=0.0, description="Average bid-ask spread")
    spread_stdev: float = Field(..., ge=0.0, description="Standard deviation of spread")
    spread_stability: float = Field(..., ge=0.0, description="Stability score of bid-ask spread")
    quote_continuity_score: float = Field(..., ge=0.0, le=1.0, description="Fraction of active quotes")
    ticks_per_second: float = Field(..., ge=0.0, description="Average tick arrival rate per second")
    tick_density: float = Field(..., ge=0.0, description="Total tick density per window")
    activity_score: float = Field(..., ge=0.0, description="Composite market activity score")
    observation_ids: list[str] = Field(default_factory=list, description="IDs of component observations")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class ExecutionProfile(BaseModel):
    """Immutable Execution Profile measuring latencies and fill metrics."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str = Field(..., description="Deterministic profile ID with prefix EXP_")
    symbol: str = Field(..., description="Deriv symbol identifier")
    index_type: SyntheticIndexType = Field(..., description="Synthetic index classification")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    window_seconds: int = Field(default=300, ge=1, description="Window size in seconds")
    sample_count: int = Field(..., ge=0, description="Number of measured execution interactions")
    mean_latency_ms: float = Field(..., ge=0.0, description="Mean latency in milliseconds")
    median_latency_ms: float = Field(..., ge=0.0, description="Median latency in milliseconds")
    p95_latency_ms: float = Field(..., ge=0.0, description="95th percentile latency in milliseconds")
    fill_time_ms: float = Field(..., ge=0.0, description="Mean fill confirmation time in milliseconds")
    consistency_score: float = Field(..., ge=0.0, le=1.0, description="Execution consistency score")
    rating: ExecutionQualityRating = Field(..., description="Overall execution quality rating")
    observation_ids: list[str] = Field(default_factory=list, description="IDs of component observations")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class MarketProfile(BaseModel):
    """Immutable Market Profile aggregating all microstructure profiles for an index."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str = Field(..., description="Deterministic profile ID with prefix MRP_")
    symbol: str = Field(..., description="Deriv symbol identifier")
    index_type: SyntheticIndexType = Field(..., description="Synthetic index classification")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    volatility_profile_id: str = Field(..., description="Referenced VolatilityProfile ID")
    jump_profile_id: str = Field(..., description="Referenced JumpProfile ID")
    liquidity_profile_id: str = Field(..., description="Referenced LiquidityProfile ID")
    execution_profile_id: str = Field(..., description="Referenced ExecutionProfile ID")
    observation_count: int = Field(..., ge=0, description="Total aggregated observations count")
    overall_health_score: float = Field(..., ge=0.0, le=100.0, description="Composite market health score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")


class ResearchSummary(BaseModel):
    """Immutable Research Summary archiving market microstructure research state."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(..., description="Deterministic summary ID with prefix MRS_")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    symbols_profiled: list[str] = Field(default_factory=list, description="List of profiled synthetic symbols")
    total_observations: int = Field(default=0, ge=0, description="Total stored observations count")
    total_volatility_profiles: int = Field(default=0, ge=0, description="Total stored volatility profiles")
    total_jump_profiles: int = Field(default=0, ge=0, description="Total stored jump profiles")
    total_liquidity_profiles: int = Field(default=0, ge=0, description="Total stored liquidity profiles")
    total_execution_profiles: int = Field(default=0, ge=0, description="Total stored execution profiles")
    total_market_profiles: int = Field(default=0, ge=0, description="Total stored market profiles")
    category_breakdown: dict[str, int] = Field(default_factory=dict, description="Counts by category")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary immutable metadata")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")
