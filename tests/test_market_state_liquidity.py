"""
Project GOAT v0.8 — Test Suite: Liquidity Assessment Engine (Exhaustive Matrix)
"""

import pytest
from goat.marketdata.core.canonical import compute_tick_id
from goat.marketdata.core.enums import DerivSymbol
from goat.marketdata.core.models import MarketTick
from goat.marketstate.core.enums import ActivityState, LiquidityState, SpreadState
from goat.marketstate.liquidity.engine import LiquidityAssessmentEngine
from goat.research.edge.canonical import compute_canonical_sha256

SYMBOLS = [s.value for s in DerivSymbol]
SPREADS = [0.05, 0.2, 0.8, 3.0]
TICK_COUNTS = [2, 10, 30, 60]


def make_tick(symbol: str, seq: int, spread: float) -> MarketTick:
    bid = 100.0
    ask = 100.0 + spread
    ts = "2026-07-31T12:00:00Z"
    tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", bid, ask, ts, seq)
    checksum = compute_canonical_sha256({"ask": ask, "bid": bid, "broker": "DERIV", "sequence_number": seq, "symbol": symbol, "timestamp": ts})
    return MarketTick(
        tick_id=tick_id, symbol=symbol, broker="DERIV", bid=bid, ask=ask, spread=spread,
        timestamp=ts, sequence_number=seq, source_latency=1.0, checksum=checksum, metadata={}, canonical_hash=canonical_hash,
    )


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("spread", SPREADS)
@pytest.mark.parametrize("count", TICK_COUNTS)
def test_liquidity_engine_matrix(symbol, spread, count):
    engine = LiquidityAssessmentEngine()
    ticks = [make_tick(symbol, i + 1, spread) for i in range(count)]

    assessment = engine.evaluate_ticks(symbol, ticks)
    assert assessment.symbol == symbol
    assert assessment.assessment_id.startswith("LIQ_")
    assert isinstance(assessment.liquidity_state, LiquidityState)
    assert isinstance(assessment.spread_quality, SpreadState)
    assert isinstance(assessment.activity_state, ActivityState)
    assert assessment.liquidity_score >= 0.0
