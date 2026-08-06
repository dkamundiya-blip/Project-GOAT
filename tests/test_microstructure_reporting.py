"""
Project GOAT v0.9 — Dedicated Tests for Microstructure Reporting Engine
"""

import json
import pytest

from goat.microstructure.core.enums import SyntheticIndexType
from goat.microstructure.execution.engine import ExecutionProfilingEngine
from goat.microstructure.jumps.engine import JumpProfilingEngine
from goat.microstructure.liquidity.engine import LiquidityProfilingEngine
from goat.microstructure.profiling.engine import MarketProfilingEngine
from goat.microstructure.reporting.reports import MicrostructureReportGenerator
from goat.microstructure.volatility.engine import VolatilityProfilingEngine

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_report_generation(index_type: SyntheticIndexType) -> None:
    reporter = MicrostructureReportGenerator()

    vol_p, _ = VolatilityProfilingEngine().analyze_series("SYM", index_type, [100.0, 101.0, 100.5])
    jmp_p, _ = JumpProfilingEngine().analyze_series("SYM", index_type, [100.0, 101.0, 100.5])
    liq_p, _ = LiquidityProfilingEngine().analyze_quotes("SYM", index_type, [0.001, 0.001])
    exc_p, _ = ExecutionProfilingEngine().analyze_latencies("SYM", index_type, [50.0, 60.0])
    mkt_p = MarketProfilingEngine().aggregate_market_profile("SYM", index_type, vol_p, jmp_p, liq_p, exc_p)

    vol_rep = reporter.generate_volatility_report(vol_p)
    jmp_rep = reporter.generate_jump_report(jmp_p)
    liq_rep = reporter.generate_liquidity_report(liq_p)
    exc_rep = reporter.generate_execution_report(exc_p)
    mkt_rep = reporter.generate_market_profile_report(mkt_p)

    assert "# DERIV VOLATILITY PROFILE REPORT" in vol_rep
    assert "# DERIV JUMP PROFILE REPORT" in jmp_rep
    assert "# DERIV LIQUIDITY PROFILE REPORT" in liq_rep
    assert "# DERIV EXECUTION PROFILE REPORT" in exc_rep
    assert "# DERIV MARKET PROFILE AGGREGATE REPORT" in mkt_rep

    json_str = reporter.export_canonical_json(mkt_p)
    data = json.loads(json_str)
    assert data["profile_id"] == mkt_p.profile_id
    assert data["canonical_hash"] == mkt_p.canonical_hash
