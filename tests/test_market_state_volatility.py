"""
Project GOAT v0.8 — Test Suite: Volatility Assessment Engine (Exhaustive Matrix)
"""

import pytest
from goat.marketdata.core.canonical import compute_candle_id, compute_tick_id
from goat.marketdata.core.enums import DerivSymbol, MarketTimeframe
from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.marketstate.core.enums import VolatilityState
from goat.marketstate.volatility.engine import VolatilityAssessmentEngine
from goat.research.edge.canonical import compute_canonical_sha256

SYMBOLS = [s.value for s in DerivSymbol]
PRICE_STEPS = [0.01, 0.05, 0.2, 1.0, 5.0, 10.0]


def make_tick(symbol: str, seq: int, mid: float) -> MarketTick:
    bid = mid - 0.1
    ask = mid + 0.1
    ts = "2026-07-31T12:00:00Z"
    tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", bid, ask, ts, seq)
    checksum = compute_canonical_sha256({"ask": ask, "bid": bid, "broker": "DERIV", "sequence_number": seq, "symbol": symbol, "timestamp": ts})
    return MarketTick(
        tick_id=tick_id, symbol=symbol, broker="DERIV", bid=bid, ask=ask, spread=0.2,
        timestamp=ts, sequence_number=seq, source_latency=1.0, checksum=checksum, metadata={}, canonical_hash=canonical_hash,
    )


def make_candle(symbol: str, open_p: float, high_p: float, low_p: float, close_p: float) -> MarketCandle:
    cid, chash = compute_candle_id(symbol, "1M", open_p, high_p, low_p, close_p, "2026-07-31T12:00:00Z", "2026-07-31T12:01:00Z")
    checksum = compute_canonical_sha256({"close": close_p, "high": high_p, "low": low_p, "open": open_p, "symbol": symbol, "timeframe": "1M"})
    return MarketCandle(
        candle_id=cid, symbol=symbol, timeframe=MarketTimeframe.M1, open=open_p, high=high_p, low=low_p, close=close_p,
        volume=10.0, open_timestamp="2026-07-31T12:00:00Z", close_timestamp="2026-07-31T12:01:00Z", completed=True,
        checksum=checksum, metadata={}, canonical_hash=chash,
    )


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("step", PRICE_STEPS)
def test_volatility_engine_ticks_matrix(symbol, step):
    engine = VolatilityAssessmentEngine()
    mids = [100.0 + (i * step if i % 2 == 0 else -i * step) for i in range(10)]
    ticks = [make_tick(symbol, i + 1, mids[i]) for i in range(len(mids))]

    assessment = engine.evaluate_ticks(symbol, ticks)
    assert assessment.symbol == symbol
    assert assessment.timeframe == "TICK"
    assert assessment.assessment_id.startswith("VOL_")
    assert isinstance(assessment.volatility_class, VolatilityState)


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("spread_pct", [0.001, 0.01, 0.05, 0.10])
def test_volatility_engine_candles_matrix(symbol, spread_pct):
    engine = VolatilityAssessmentEngine()
    base = 100.0
    candles = [
        make_candle(symbol, base, base * (1.0 + spread_pct), base * (1.0 - spread_pct), base)
        for _ in range(5)
    ]

    assessment = engine.evaluate_candles(symbol, candles)
    assert assessment.symbol == symbol
    assert assessment.timeframe == "1M"
    assert assessment.volatility_score >= 0.0
