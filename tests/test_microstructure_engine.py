"""
Project GOAT v0.9 — Dedicated Tests for Microstructure Research Engine Master Orchestrator
"""

import pytest

from goat.microstructure.core.enums import SyntheticIndexType
from goat.microstructure.engine import MicrostructureResearchEngine

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_research_engine_full_workflow(index_type: SyntheticIndexType) -> None:
    engine = MicrostructureResearchEngine(":memory:")

    prices = [100.0 + i * 0.05 for i in range(30)]
    spreads = [0.001 + (i % 2) * 0.0005 for i in range(30)]
    latencies = [40.0 + (i % 3) * 5.0 for i in range(30)]

    mkt_profile, obs_list = engine.profile_synthetic_index(
        symbol=index_type.value,
        index_type=index_type,
        prices=prices,
        spreads=spreads,
        latencies_ms=latencies,
        timestamp_str="2026-01-01T00:00:00Z",
    )

    assert mkt_profile.profile_id.startswith("MRP_")
    assert len(obs_list) > 0

    # Summary generation
    summary = engine.generate_research_summary("2026-01-01T00:00:00Z")
    assert summary.summary_id.startswith("MRS_")
    assert summary.total_observations >= len(obs_list)
    assert index_type.value in summary.symbols_profiled

    engine.close()


def test_research_engine_multi_symbol_summary() -> None:
    engine = MicrostructureResearchEngine(":memory:")
    symbols = ["VOLATILITY_10", "BOOM_1000", "CRASH_500", "JUMP_75", "STEP_INDEX"]

    for sym in symbols:
        idx_type = SyntheticIndexType(sym)
        engine.profile_synthetic_index(
            symbol=sym,
            index_type=idx_type,
            prices=[100.0, 102.0, 101.0, 105.0],
            timestamp_str="2026-01-01T00:00:00Z",
        )

    summary = engine.generate_research_summary("2026-01-01T00:00:00Z")
    assert len(summary.symbols_profiled) == 5
    assert summary.total_market_profiles == 5
    assert summary.total_volatility_profiles == 5
    assert summary.total_jump_profiles == 5

    engine.close()
