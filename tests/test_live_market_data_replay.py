"""
Project GOAT v0.8 — Test Suite: Replay Engine & Snapshot Integrity (Exhaustive Matrix)
"""

import datetime
import pytest
from goat.marketdata.core.canonical import compute_tick_id
from goat.marketdata.core.enums import DerivSymbol
from goat.marketdata.core.models import MarketTick
from goat.marketdata.replay.engine import MarketReplayEngine
from goat.research.edge.canonical import compute_canonical_sha256

SYMBOLS = [s.value for s in DerivSymbol]
SEQUENCE_LENGTHS = [2, 5, 10, 20]


def make_tick(symbol: str, seq: int, ts: str) -> MarketTick:
    tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", 10.0, 10.2, ts, seq)
    checksum = compute_canonical_sha256(
        {
            "ask": 10.2,
            "bid": 10.0,
            "broker": "DERIV",
            "sequence_number": seq,
            "symbol": symbol,
            "timestamp": ts,
        }
    )
    return MarketTick(
        tick_id=tick_id,
        symbol=symbol,
        broker="DERIV",
        bid=10.0,
        ask=10.2,
        spread=0.2,
        timestamp=ts,
        sequence_number=seq,
        checksum=checksum,
        canonical_hash=canonical_hash,
    )


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("length", SEQUENCE_LENGTHS)
def test_replay_engine_successful_replay_matrix(symbol, length):
    engine = MarketReplayEngine()
    now = datetime.datetime.now(datetime.timezone.utc)
    ticks = [
        make_tick(symbol, i + 1, (now + datetime.timedelta(seconds=i)).isoformat())
        for i in range(length)
    ]

    res = engine.replay_tick_sequence(ticks)
    assert res.success is True
    assert res.snapshot.replay_id.startswith("RPS_")
    assert res.replayed_ticks_count == length


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
def test_replay_engine_out_of_order_failure_matrix(symbol):
    engine = MarketReplayEngine()
    now = datetime.datetime.now(datetime.timezone.utc)
    t1 = make_tick(symbol, 1, (now + datetime.timedelta(seconds=10)).isoformat())
    t2 = make_tick(symbol, 2, (now + datetime.timedelta(seconds=0)).isoformat())

    res = engine.replay_tick_sequence([t1, t2])
    assert res.success is False
    assert "REPLAY_CHRONOLOGY_VIOLATION" in res.integrity_error
