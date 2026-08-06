"""
Project GOAT v0.9 — Dedicated Tests for Execution Profiling Engine
"""

import pytest

from goat.microstructure.core.enums import ExecutionQualityRating, SyntheticIndexType
from goat.microstructure.execution.engine import ExecutionProfilingEngine

INDICES = list(SyntheticIndexType)
MEAN_LATENCIES = [20.0, 80.0, 250.0, 600.0]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("lat", MEAN_LATENCIES)
def test_execution_engine_latencies(index_type: SyntheticIndexType, lat: float) -> None:
    engine = ExecutionProfilingEngine()
    latencies = [lat] * 50
    fill_times = [lat * 1.05 for _ in range(50)]

    profile, obs = engine.analyze_latencies(
        symbol=index_type.value,
        index_type=index_type,
        latencies_ms=latencies,
        fill_times_ms=fill_times,
        timestamp_str="2026-01-01T00:00:00Z",
        window_seconds=300,
    )

    assert profile.profile_id.startswith("EXP_")
    assert profile.mean_latency_ms == lat
    assert profile.p95_latency_ms >= profile.median_latency_ms
    assert isinstance(profile.rating, ExecutionQualityRating)
    assert len(obs) == 4

    if lat == 20.0:
        assert profile.rating == ExecutionQualityRating.EXCELLENT
    elif lat == 80.0:
        assert profile.rating == ExecutionQualityRating.NORMAL
    elif lat == 250.0:
        assert profile.rating == ExecutionQualityRating.DEGRADED
    elif lat == 600.0:
        assert profile.rating in (ExecutionQualityRating.DEGRADED, ExecutionQualityRating.POOR)


@pytest.mark.parametrize("index_type", INDICES[:5])
def test_execution_engine_fallback(index_type: SyntheticIndexType) -> None:
    engine = ExecutionProfilingEngine()
    profile, obs = engine.analyze_latencies(
        symbol=index_type.value,
        index_type=index_type,
        latencies_ms=[],
        timestamp_str="2026-01-01T00:00:00Z",
        window_seconds=300,
    )
    assert profile.sample_count == 0
    assert profile.mean_latency_ms == 0.0
    assert len(obs) == 1
