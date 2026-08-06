"""
Project GOAT v0.9 — Dedicated Tests for Microstructure Domain Models & Canonical Hashing
"""

import pytest
from pydantic import ValidationError

from goat.microstructure.core.canonical import (
    compute_canonical_sha256,
    compute_execution_profile_id,
    compute_jump_profile_id,
    compute_liquidity_profile_id,
    compute_market_profile_id,
    compute_observation_id,
    compute_research_summary_id,
    compute_volatility_profile_id,
    serialize_canonical_json,
)
from goat.microstructure.core.enums import (
    ExecutionQualityRating,
    JumpDirection,
    MicrostructureMetricType,
    ObservationCategory,
    SyntheticIndexType,
    VolatilityRegime,
)
from goat.microstructure.core.models import (
    ExecutionProfile,
    JumpProfile,
    LiquidityProfile,
    MarketProfile,
    MicrostructureObservation,
    ResearchSummary,
    VolatilityProfile,
)

INDICES = list(SyntheticIndexType)
WINDOWS = [15, 30, 60, 120, 300, 600, 900, 1800, 3600, 86400]
METRIC_TYPES = list(MicrostructureMetricType)
VALUES = [0.0, 0.001, 0.05, 1.25, 100.0]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("metric_type", METRIC_TYPES)
@pytest.mark.parametrize("window", WINDOWS[:5])
@pytest.mark.parametrize("val", VALUES)
def test_observation_model_matrix(
    index_type: SyntheticIndexType, metric_type: MicrostructureMetricType, window: int, val: float
) -> None:
    obs_id, h_digest = compute_observation_id("SYM", metric_type.value, "2026-01-01T00:00:00Z", val, window)
    obs = MicrostructureObservation(
        observation_id=obs_id,
        metric_type=metric_type,
        category=ObservationCategory.VOLATILITY,
        symbol="SYM",
        index_type=index_type,
        timestamp="2026-01-01T00:00:00Z",
        value=val,
        unit="unit",
        window_seconds=window,
        metadata={"idx": index_type.value},
        canonical_hash=h_digest,
    )
    assert obs.observation_id.startswith("MSO_")
    assert obs.canonical_hash == h_digest
    assert obs.index_type == index_type
    assert obs.window_seconds == window

    with pytest.raises(ValidationError):
        obs.value = val + 1.0  # type: ignore


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("regime", list(VolatilityRegime))
@pytest.mark.parametrize("window", WINDOWS[:4])
def test_volatility_profile_matrix(
    index_type: SyntheticIndexType, regime: VolatilityRegime, window: int
) -> None:
    p_id, h_digest = compute_volatility_profile_id("SYM", "2026-01-01T00:00:00Z", window, 0.02, ["MSO_1"])
    profile = VolatilityProfile(
        profile_id=p_id,
        symbol="SYM",
        index_type=index_type,
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=window,
        realized_volatility=0.02,
        volatility_clustering_coeff=0.4,
        volatility_persistence=0.8,
        expansion_ratio=1.2,
        contraction_ratio=0.8,
        regime=regime,
        observation_ids=["MSO_1"],
        metadata={"regime": regime.value},
        canonical_hash=h_digest,
    )
    assert profile.profile_id.startswith("VLP_")
    assert profile.canonical_hash == h_digest
    assert profile.regime == regime


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("direction", list(JumpDirection))
@pytest.mark.parametrize("window", WINDOWS[:4])
def test_jump_profile_matrix(
    index_type: SyntheticIndexType, direction: JumpDirection, window: int
) -> None:
    p_id, h_digest = compute_jump_profile_id("SYM", "2026-01-01T00:00:00Z", window, 5, 12.5, ["MSO_2"])
    profile = JumpProfile(
        profile_id=p_id,
        symbol="SYM",
        index_type=index_type,
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=window,
        jump_count=5,
        jump_frequency=1.0,
        mean_jump_magnitude=12.5,
        max_jump_magnitude=25.0,
        mean_jump_spacing_sec=60.0,
        jump_persistence=0.1,
        jump_clustering_index=1.2,
        dominant_direction=direction,
        observation_ids=["MSO_2"],
        metadata={},
        canonical_hash=h_digest,
    )
    assert profile.profile_id.startswith("JMP_")
    assert profile.canonical_hash == h_digest
    assert profile.dominant_direction == direction


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("window", WINDOWS[:5])
def test_liquidity_profile_matrix(index_type: SyntheticIndexType, window: int) -> None:
    p_id, h_digest = compute_liquidity_profile_id("SYM", "2026-01-01T00:00:00Z", window, 0.002, 60.0, ["MSO_3"])
    profile = LiquidityProfile(
        profile_id=p_id,
        symbol="SYM",
        index_type=index_type,
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=window,
        average_spread=0.002,
        spread_stdev=0.0001,
        spread_stability=0.99,
        quote_continuity_score=1.0,
        ticks_per_second=1.0,
        tick_density=60.0,
        activity_score=99.0,
        observation_ids=["MSO_3"],
        metadata={},
        canonical_hash=h_digest,
    )
    assert profile.profile_id.startswith("LIQ_")
    assert profile.canonical_hash == h_digest


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("rating", list(ExecutionQualityRating))
@pytest.mark.parametrize("window", WINDOWS[:4])
def test_execution_profile_matrix(
    index_type: SyntheticIndexType, rating: ExecutionQualityRating, window: int
) -> None:
    p_id, h_digest = compute_execution_profile_id("SYM", "2026-01-01T00:00:00Z", window, 45.0, 100, ["MSO_4"])
    profile = ExecutionProfile(
        profile_id=p_id,
        symbol="SYM",
        index_type=index_type,
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=window,
        sample_count=100,
        mean_latency_ms=45.0,
        median_latency_ms=40.0,
        p95_latency_ms=75.0,
        fill_time_ms=50.0,
        consistency_score=0.95,
        rating=rating,
        observation_ids=["MSO_4"],
        metadata={},
        canonical_hash=h_digest,
    )
    assert profile.profile_id.startswith("EXP_")
    assert profile.canonical_hash == h_digest
    assert profile.rating == rating


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("window", WINDOWS[:5])
def test_market_profile_matrix(index_type: SyntheticIndexType, window: int) -> None:
    p_id, h_digest = compute_market_profile_id(
        "SYM", "2026-01-01T00:00:00Z", "VLP_1", "JMP_1", "LIQ_1", "EXP_1"
    )
    profile = MarketProfile(
        profile_id=p_id,
        symbol="SYM",
        index_type=index_type,
        timestamp="2026-01-01T00:00:00Z",
        volatility_profile_id="VLP_1",
        jump_profile_id="JMP_1",
        liquidity_profile_id="LIQ_1",
        execution_profile_id="EXP_1",
        observation_count=20,
        overall_health_score=95.5,
        metadata={},
        canonical_hash=h_digest,
    )
    assert profile.profile_id.startswith("MRP_")
    assert profile.canonical_hash == h_digest


@pytest.mark.parametrize("obs_count", [0, 10, 100, 1000, 5000])
def test_research_summary_hashing(obs_count: int) -> None:
    s_id, h_digest = compute_research_summary_id("2026-01-01T00:00:00Z", obs_count, ["R_100", "BOOM_1000"])
    summary = ResearchSummary(
        summary_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        symbols_profiled=["R_100", "BOOM_1000"],
        total_observations=obs_count,
        total_volatility_profiles=1,
        total_jump_profiles=1,
        total_liquidity_profiles=1,
        total_execution_profiles=1,
        total_market_profiles=1,
        category_breakdown={"VOLATILITY": obs_count},
        metadata={},
        canonical_hash=h_digest,
    )
    assert summary.summary_id.startswith("MRS_")
    assert summary.canonical_hash == h_digest
