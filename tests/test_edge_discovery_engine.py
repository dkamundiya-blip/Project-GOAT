"""
Project GOAT v0.9 — Dedicated Tests for Master Quantitative Edge Discovery Engine
"""

import pytest

from goat.edge_discovery.engine import MasterEdgeDiscoveryEngine
from goat.microstructure.core.enums import MicrostructureMetricType, SyntheticIndexType
from goat.microstructure.core.models import MicrostructureObservation

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_master_edge_discovery_engine_workflow(index_type: SyntheticIndexType) -> None:
    engine = MasterEdgeDiscoveryEngine(":memory:")

    obs_list = []
    for i in range(30):
        obs_list.append(
            MicrostructureObservation(
                observation_id=f"MSO_{index_type.value}_{i}",
                metric_type=MicrostructureMetricType.REALIZED_VOLATILITY,
                category="VOLATILITY",
                symbol=index_type.value,
                index_type=index_type,
                timestamp="2026-01-01T00:00:00Z",
                value=0.02 + (i * 0.001),
                unit="unit",
                window_seconds=300,
                metadata={},
                canonical_hash=f"HASH_{i}",
            )
        )

    candidates, decisions = engine.discover_edges(
        symbol=index_type.value,
        observations=obs_list,
        timestamp_str="2026-01-01T00:00:00Z",
    )

    assert len(candidates) == 1
    assert len(decisions) == 1

    candidate = candidates[0]
    decision = decisions[0]

    assert candidate.candidate_id.startswith("EDC_")
    assert decision.decision_id.startswith("DSC_")
    assert decision.candidate_id == candidate.candidate_id

    summary = engine.generate_discovery_summary("2026-01-01T00:00:00Z")
    assert summary.summary_id.startswith("DSM_")
    assert summary.total_candidates >= 1

    engine.close()


def test_master_edge_discovery_multi_symbol() -> None:
    engine = MasterEdgeDiscoveryEngine(":memory:")
    symbols = ["VOLATILITY_10", "BOOM_1000", "CRASH_500", "JUMP_75", "STEP_INDEX"]

    for sym in symbols:
        idx_type = SyntheticIndexType(sym)
        obs_list = [
            MicrostructureObservation(
                observation_id=f"MSO_{sym}_{i}",
                metric_type=MicrostructureMetricType.REALIZED_VOLATILITY,
                category="VOLATILITY",
                symbol=sym,
                index_type=idx_type,
                timestamp="2026-01-01T00:00:00Z",
                value=0.05 + (i * 0.002),
                unit="unit",
                window_seconds=300,
                metadata={},
                canonical_hash=f"HASH_{i}",
            )
            for i in range(20)
        ]
        engine.discover_edges(symbol=sym, observations=obs_list, timestamp_str="2026-01-01T00:00:00Z")

    summary = engine.generate_discovery_summary("2026-01-01T00:00:00Z")
    assert summary.total_candidates == 5
    assert summary.total_validated == 5
    assert summary.total_patterns == 5

    engine.close()
