"""
Project GOAT v0.9 — Dedicated Tests for Pattern Mining Engine
"""

import pytest

from goat.edge_discovery.core.enums import PatternType
from goat.edge_discovery.mining.engine import PatternMiningEngine
from goat.microstructure.core.enums import MicrostructureMetricType, SyntheticIndexType
from goat.microstructure.core.models import MicrostructureObservation

INDICES = list(SyntheticIndexType)
METRICS = list(MicrostructureMetricType)
SAMPLE_SIZES = [15, 25, 50, 100]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("metric", METRICS[:4])
@pytest.mark.parametrize("n_obs", SAMPLE_SIZES[:2])
def test_pattern_mining_from_observations_matrix(
    index_type: SyntheticIndexType, metric: MicrostructureMetricType, n_obs: int
) -> None:
    engine = PatternMiningEngine()
    obs_list = []
    for i in range(n_obs):
        obs_list.append(
            MicrostructureObservation(
                observation_id=f"MSO_{index_type.value}_{metric.value}_{i}",
                metric_type=metric,
                category="VOLATILITY",
                symbol=index_type.value,
                index_type=index_type,
                timestamp="2026-01-01T00:00:00Z",
                value=0.05 + (i * 0.001),
                unit="unit",
                window_seconds=300,
                metadata={},
                canonical_hash=f"HASH_{i}",
            )
        )

    patterns, candidates = engine.mine_microstructure_patterns(
        symbol=index_type.value,
        observations=obs_list,
        timestamp_str="2026-01-01T00:00:00Z",
        min_sample_size=10,
    )

    assert len(patterns) == 1
    assert len(candidates) == 1

    pattern = patterns[0]
    candidate = candidates[0]

    assert pattern.pattern_id.startswith("EPT_")
    assert pattern.symbol == index_type.value
    assert pattern.sample_size == n_obs
    assert candidate.candidate_id.startswith("EDC_")
    assert candidate.symbol == index_type.value
    assert len(candidate.pattern_ids) == 1


@pytest.mark.parametrize("index_type", INDICES[:5])
def test_pattern_mining_insufficient_samples(index_type: SyntheticIndexType) -> None:
    engine = PatternMiningEngine()
    obs_list = [
        MicrostructureObservation(
            observation_id="MSO_1",
            metric_type=MicrostructureMetricType.REALIZED_VOLATILITY,
            category="VOLATILITY",
            symbol=index_type.value,
            index_type=index_type,
            timestamp="2026-01-01T00:00:00Z",
            value=0.05,
            unit="unit",
            window_seconds=300,
            metadata={},
            canonical_hash="HASH",
        )
    ]

    patterns, candidates = engine.mine_microstructure_patterns(
        symbol=index_type.value,
        observations=obs_list,
        timestamp_str="2026-01-01T00:00:00Z",
        min_sample_size=10,
    )

    assert len(patterns) == 0
    assert len(candidates) == 0
