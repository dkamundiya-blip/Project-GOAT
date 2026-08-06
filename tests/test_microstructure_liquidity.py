"""
Project GOAT v0.9 — Dedicated Tests for Liquidity Profiling Engine
"""

import pytest

from goat.microstructure.core.enums import SyntheticIndexType
from goat.microstructure.liquidity.engine import LiquidityProfilingEngine

INDICES = list(SyntheticIndexType)
TICK_COUNTS = [10, 50, 100, 300]
BASE_SPREADS = [0.0001, 0.001, 0.01, 0.1]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("tick_count", TICK_COUNTS[:2])
@pytest.mark.parametrize("base_spread", BASE_SPREADS[:2])
def test_liquidity_engine_metrics(
    index_type: SyntheticIndexType, tick_count: int, base_spread: float
) -> None:
    engine = LiquidityProfilingEngine()
    spreads = [base_spread + (0.0001 * (i % 3)) for i in range(tick_count)]
    timestamps = [float(i) for i in range(tick_count)]

    profile, obs = engine.analyze_quotes(
        symbol=index_type.value,
        index_type=index_type,
        spreads=spreads,
        timestamps=timestamps,
        timestamp_str="2026-01-01T00:00:00Z",
        window_seconds=300,
    )

    assert profile.profile_id.startswith("LIQ_")
    assert profile.average_spread > 0.0
    assert profile.spread_stability > 0.0
    assert profile.quote_continuity_score >= 0.0
    assert len(obs) == 4


@pytest.mark.parametrize("index_type", INDICES[:5])
def test_liquidity_engine_fallback(index_type: SyntheticIndexType) -> None:
    engine = LiquidityProfilingEngine()
    profile, obs = engine.analyze_quotes(
        symbol=index_type.value,
        index_type=index_type,
        spreads=[],
        timestamp_str="2026-01-01T00:00:00Z",
        window_seconds=300,
    )
    assert profile.average_spread == 0.0
    assert profile.activity_score == 0.0
    assert len(obs) == 1
