"""
Project GOAT v0.8 — Test Suite: Structure Assessment Engine (Exhaustive Matrix)
"""

import pytest
from goat.marketdata.core.canonical import compute_candle_id, compute_tick_id
from goat.marketdata.core.enums import DerivSymbol, MarketTimeframe
from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.marketstate.core.enums import StructureState, TrendState
from goat.marketstate.structure.engine import StructureAssessmentEngine
from goat.research.edge.canonical import compute_canonical_sha256

SYMBOLS = [s.value for s in DerivSymbol]
PRICE_STEPS = [0.1, 0.5, 1.0, 5.0]


def make_candle(symbol: str, open_p: float, high_p: float, low_p: float, close_p: float) -> MarketCandle:
    cid, chash = compute_candle_id(symbol, "1M", open_p, high_p, low_p, close_p, "2026-07-31T12:00:00Z", "2026-07-31T12:01:00Z")
    checksum = compute_canonical_sha256({"close": close_p, "high": high_p, "low": low_p, "open": open_p, "symbol": symbol, "timeframe": "1M"})
    return MarketCandle(
        candle_id=cid, symbol=symbol, timeframe=MarketTimeframe.M1, open=open_p, high=high_p, low=low_p, close=close_p,
        volume=10.0, open_timestamp="2026-07-31T12:00:00Z", close_timestamp="2026-07-31T12:01:00Z", completed=True,
        checksum=checksum, metadata={}, canonical_hash=chash,
    )


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


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("step", PRICE_STEPS)
def test_structure_uptrend_matrix(symbol, step):
    engine = StructureAssessmentEngine()
    candles = [
        make_candle(symbol, 100.0 + i * step, 102.0 + i * step, 99.0 + i * step, 101.0 + i * step)
        for i in range(5)
    ]
    assessment = engine.evaluate_candles(symbol, candles)
    assert assessment.symbol == symbol
    assert assessment.structure_state == StructureState.BULLISH
    assert assessment.trend_state in (TrendState.UPTREND, TrendState.STRONG_UPTREND)


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("step", PRICE_STEPS)
def test_structure_downtrend_matrix(symbol, step):
    engine = StructureAssessmentEngine()
    candles = [
        make_candle(symbol, 100.0 - i * step, 101.0 - i * step, 98.0 - i * step, 99.0 - i * step)
        for i in range(5)
    ]
    assessment = engine.evaluate_candles(symbol, candles)
    assert assessment.symbol == symbol
    assert assessment.structure_state == StructureState.BEARISH
    assert assessment.trend_state in (TrendState.DOWNTREND, TrendState.STRONG_DOWNTREND)


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_structure_ranging_matrix(symbol):
    engine = StructureAssessmentEngine()
    candles = [
        make_candle(symbol, 100.0, 102.0, 98.0, 100.0),
        make_candle(symbol, 100.0, 101.0, 99.0, 100.0),
        make_candle(symbol, 100.0, 102.0, 98.0, 100.0),
        make_candle(symbol, 100.0, 101.0, 99.0, 100.0),
    ]
    assessment = engine.evaluate_candles(symbol, candles)
    assert assessment.symbol == symbol
    assert assessment.structure_state in (StructureState.RANGING, StructureState.TRANSITIONAL)


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_structure_ticks_matrix(symbol):
    engine = StructureAssessmentEngine()
    ticks_up = [make_tick(symbol, i + 1, 100.0 + i) for i in range(10)]
    assessment_up = engine.evaluate_ticks(symbol, ticks_up)
    assert assessment_up.symbol == symbol
    assert assessment_up.structure_state == StructureState.BULLISH
