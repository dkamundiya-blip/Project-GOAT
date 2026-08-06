"""
Project GOAT v0.9 — Dedicated Tests for Market Profile Aggregation Engine
"""

import pytest

from goat.microstructure.core.enums import SyntheticIndexType
from goat.microstructure.execution.engine import ExecutionProfilingEngine
from goat.microstructure.jumps.engine import JumpProfilingEngine
from goat.microstructure.liquidity.engine import LiquidityProfilingEngine
from goat.microstructure.profiling.engine import MarketProfilingEngine
from goat.microstructure.volatility.engine import VolatilityProfilingEngine

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_market_profile_aggregation(index_type: SyntheticIndexType) -> None:
    vol_eng = VolatilityProfilingEngine()
    jmp_eng = JumpProfilingEngine()
    liq_eng = LiquidityProfilingEngine()
    exc_eng = ExecutionProfilingEngine()
    mkt_eng = MarketProfilingEngine()

    prices = [100.0 + i * 0.1 for i in range(50)]
    vol_p, _ = vol_eng.analyze_series("SYM", index_type, prices)
    jmp_p, _ = jmp_eng.analyze_series("SYM", index_type, prices)
    liq_p, _ = liq_eng.analyze_quotes("SYM", index_type, [0.001] * 50)
    exc_p, _ = exc_eng.analyze_latencies("SYM", index_type, [30.0] * 50)

    mkt_p = mkt_eng.aggregate_market_profile(
        symbol="SYM",
        index_type=index_type,
        volatility_profile=vol_p,
        jump_profile=jmp_p,
        liquidity_profile=liq_p,
        execution_profile=exc_p,
        timestamp_str="2026-01-01T00:00:00Z",
    )

    assert mkt_p.profile_id.startswith("MRP_")
    assert mkt_p.symbol == "SYM"
    assert mkt_p.index_type == index_type
    assert mkt_p.volatility_profile_id == vol_p.profile_id
    assert mkt_p.jump_profile_id == jmp_p.profile_id
    assert mkt_p.liquidity_profile_id == liq_p.profile_id
    assert mkt_p.execution_profile_id == exc_p.profile_id
    assert mkt_p.observation_count > 0
    assert 0.0 <= mkt_p.overall_health_score <= 100.0
