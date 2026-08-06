"""
Project GOAT v0.9 — Dedicated Tests for Jump Profiling Engine
"""

import pytest

from goat.microstructure.core.enums import JumpDirection, SyntheticIndexType
from goat.microstructure.jumps.engine import JumpProfilingEngine

INDICES = list(SyntheticIndexType)
JUMP_COUNTS = [0, 1, 3, 5, 10]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("jump_count", JUMP_COUNTS)
def test_jump_engine_detection(index_type: SyntheticIndexType, jump_count: int) -> None:
    engine = JumpProfilingEngine()
    prices = [100.0]
    timestamps = [0.0]

    # Create baseline ticks with occasional sharp jumps
    for i in range(1, 100):
        timestamps.append(float(i))
        if i in [(k + 1) * 10 for k in range(jump_count)]:
            # Add large spike jump
            spike = 50.0 if "BOOM" in index_type.value else (-50.0 if "CRASH" in index_type.value else 50.0)
            prices.append(prices[-1] + spike)
        else:
            prices.append(prices[-1] + 0.01 * (1 if i % 2 == 0 else -1))

    profile, obs = engine.analyze_series(
        symbol=index_type.value,
        index_type=index_type,
        prices=prices,
        timestamps=timestamps,
        timestamp_str="2026-01-01T00:00:00Z",
        window_seconds=300,
        jump_threshold_std=2.5,
    )

    assert profile.profile_id.startswith("JMP_")
    assert profile.index_type == index_type
    assert len(obs) == 5

    if "BOOM" in index_type.value and jump_count > 0:
        assert profile.dominant_direction in (JumpDirection.UPWARD, JumpDirection.NEUTRAL)
    elif "CRASH" in index_type.value and jump_count > 0:
        assert profile.dominant_direction in (JumpDirection.DOWNWARD, JumpDirection.NEUTRAL)


@pytest.mark.parametrize("index_type", INDICES[:5])
def test_jump_engine_fallback(index_type: SyntheticIndexType) -> None:
    engine = JumpProfilingEngine()
    profile, obs = engine.analyze_series(
        symbol=index_type.value,
        index_type=index_type,
        prices=[100.0],
        timestamp_str="2026-01-01T00:00:00Z",
        window_seconds=300,
    )
    assert profile.jump_count == 0
    assert profile.mean_jump_magnitude == 0.0
    assert profile.dominant_direction == JumpDirection.NEUTRAL
    assert len(obs) == 1
