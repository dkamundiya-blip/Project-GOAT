"""
Project GOAT v0.9 — Dedicated Tests for Volatility Profiling Engine
"""

import math
import pytest

from goat.microstructure.core.enums import SyntheticIndexType, VolatilityRegime
from goat.microstructure.volatility.engine import VolatilityProfilingEngine

INDICES = list(SyntheticIndexType)
SCALES = [0.001, 0.005, 0.01, 0.02, 0.05]
WINDOWS = [15, 30, 60, 120, 300, 600, 900, 1800, 3600, 86400]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("scale", SCALES)
@pytest.mark.parametrize("window", WINDOWS[:4])
def test_volatility_engine_calculation(
    index_type: SyntheticIndexType, scale: float, window: int
) -> None:
    engine = VolatilityProfilingEngine()
    prices = [1000.0]
    for i in range(1, 60):
        ret = scale * math.sin(i / 5.0)
        prices.append(prices[-1] * (1.0 + ret))

    profile, obs = engine.analyze_series(
        symbol=index_type.value,
        index_type=index_type,
        prices=prices,
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=window,
    )

    assert profile.profile_id.startswith("VLP_")
    assert profile.index_type == index_type
    assert profile.realized_volatility >= 0.0
    assert len(obs) == 5
    assert len(profile.observation_ids) == 5

    # Verify deterministic reproducibility
    profile2, obs2 = engine.analyze_series(
        symbol=index_type.value,
        index_type=index_type,
        prices=prices,
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=window,
    )
    assert profile.profile_id == profile2.profile_id
    assert profile.canonical_hash == profile2.canonical_hash


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("window", WINDOWS[:5])
def test_volatility_engine_empty_or_single(index_type: SyntheticIndexType, window: int) -> None:
    engine = VolatilityProfilingEngine()
    profile, obs = engine.analyze_series(
        symbol=index_type.value,
        index_type=index_type,
        prices=[100.0],
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=window,
    )
    assert profile.realized_volatility == 0.0
    assert profile.regime == VolatilityRegime.NORMAL_VOLATILITY
    assert len(obs) == 1


@pytest.mark.parametrize("index_type", INDICES[:5])
@pytest.mark.parametrize("expansion_mult", [1.0, 2.0, 3.0])
def test_volatility_expansion_regime(
    index_type: SyntheticIndexType, expansion_mult: float
) -> None:
    engine = VolatilityProfilingEngine()
    prices = [100.0]
    for i in range(60):
        mult = 0.001 if i < 30 else (0.001 * expansion_mult * 5.0)
        ret = mult * (1 if i % 2 == 0 else -1)
        prices.append(prices[-1] * (1.0 + ret))

    profile, obs = engine.analyze_series(
        symbol=index_type.value,
        index_type=index_type,
        prices=prices,
        timestamp="2026-01-01T00:00:00Z",
        window_seconds=300,
    )

    if expansion_mult > 1.5:
        assert profile.expansion_ratio > 1.2
