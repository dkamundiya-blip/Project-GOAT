"""
Project GOAT v0.9 — Dedicated Unit Tests for Scientific Observation Engine
"""

import pytest

from goat.evidence.core.enums import (
    EvidenceCategory,
    ObservationSource,
    ObservationStatus,
)
from goat.evidence.observation.engine import ScientificObservationEngine


@pytest.fixture
def obs_engine():
    return ScientificObservationEngine()


@pytest.mark.parametrize("idx", range(1, 20))
def test_create_observation_success(obs_engine: ScientificObservationEngine, idx: int):
    obs = obs_engine.create_observation(
        metric_name=f"tick_spread_{idx}",
        metric_value=0.1 * idx,
        unit_of_measure="pips",
        source=ObservationSource.LIVE_MARKET,
        category=EvidenceCategory.PRICE,
        instrument="Volatility 100 Index",
    )

    assert obs.observation_id.startswith("OBS_")
    assert obs.metric_name == f"tick_spread_{idx}"
    assert obs.metric_value == 0.1 * idx
    assert obs.status == ObservationStatus.CREATED
    assert obs_engine.get_observation(obs.observation_id) is not None


@pytest.mark.parametrize("invalid_metric", ["", " ", "a"])
def test_create_observation_invalid_metric_name(obs_engine: ScientificObservationEngine, invalid_metric: str):
    with pytest.raises(ValueError):
        obs_engine.create_observation(
            metric_name=invalid_metric,
            metric_value=100.0,
        )


@pytest.mark.parametrize("category", list(EvidenceCategory))
@pytest.mark.parametrize("source", list(ObservationSource))
def test_list_observations_filtering(
    obs_engine: ScientificObservationEngine,
    category: EvidenceCategory,
    source: ObservationSource,
):
    obs_engine.create_observation(
        metric_name="volatility_compression",
        metric_value=0.85,
        source=source,
        category=category,
        instrument="Crash 500 Index",
    )

    results = obs_engine.list_observations(category=category, source=source, instrument="Crash 500 Index")
    assert len(results) >= 1
    assert results[0].category == category
    assert results[0].source == source
    assert results[0].instrument == "CRASH 500 INDEX"


@pytest.mark.parametrize("count", range(1, 15))
def test_chronological_ordering(obs_engine: ScientificObservationEngine, count: int):
    for i in range(count):
        obs_engine.create_observation(
            metric_name=f"metric_{i}",
            metric_value=i,
            timestamp=f"2026-08-04T12:{i:02d}:00Z",
        )

    all_obs = obs_engine.list_observations()
    assert len(all_obs) == count
    timestamps = [o.timestamp for o in all_obs]
    assert timestamps == sorted(timestamps)
