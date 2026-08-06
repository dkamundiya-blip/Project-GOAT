"""
Project GOAT v0.8 — Test Suite: MarketStateEngine Coordinator Integration (Exhaustive Matrix)
"""

import sqlite3
import pytest

from goat.marketdata.core.canonical import compute_candle_id, compute_tick_id
from goat.marketdata.core.enums import DerivSymbol, MarketTimeframe
from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.marketstate.engine import MarketStateEngine
from goat.marketstate.persistence.repository import init_marketstate_db
from goat.research.edge.canonical import compute_canonical_sha256

SYMBOLS = [s.value for s in DerivSymbol]


@pytest.fixture
def engine():
    conn = init_marketstate_db(":memory:")
    eng = MarketStateEngine(db_conn=conn)
    yield eng
    conn.close()


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
def test_market_state_engine_evaluation_matrix(engine, symbol):
    ticks = [make_tick(symbol, i + 1, 100.0 + i) for i in range(10)]
    candles = [make_candle(symbol, 100.0 + i, 102.0 + i, 99.0 + i, 101.0 + i) for i in range(5)]

    state = engine.evaluate_market_state(
        symbol=symbol,
        ticks=ticks,
        candles=candles,
    )

    assert state.symbol == symbol
    assert state.state_id.startswith("MST_")
    assert state.confidence > 0.0
    assert engine.get_latest_market_state(symbol) == state


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
def test_market_state_engine_executive_report_matrix(engine, symbol):
    ticks = [make_tick(symbol, 1, 100.0)]
    engine.evaluate_market_state(symbol=symbol, ticks=ticks)

    exec_rep = engine.generate_executive_report()
    assert exec_rep.active_symbols_count >= 1
    assert len(exec_rep.states) >= 1
