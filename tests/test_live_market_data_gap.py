"""
Project GOAT v0.8 — Test Suite: Gap Detection Engine (Exhaustive Matrix)
"""

import datetime
import pytest
from goat.marketdata.core.canonical import compute_tick_id
from goat.marketdata.core.enums import DerivSymbol, GapReason
from goat.marketdata.core.models import MarketTick
from goat.marketdata.gap.engine import MarketGapDetectionEngine
from goat.research.edge.canonical import compute_canonical_sha256

SYMBOLS = [s.value for s in DerivSymbol]
SEQUENCE_JUMPS = [2, 3, 5, 10, 25, 50]


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
@pytest.mark.parametrize("jump", SEQUENCE_JUMPS)
def test_gap_detection_sequence_discontinuity_matrix(symbol, jump):
    engine = MarketGapDetectionEngine(max_allowed_time_gap_seconds=60.0)
    now = datetime.datetime.now(datetime.timezone.utc)
    ts1 = now.isoformat()
    ts2 = (now + datetime.timedelta(seconds=1)).isoformat()

    seq1 = 10
    seq2 = seq1 + jump

    t1 = make_tick(symbol, seq1, ts1)
    t2 = make_tick(symbol, seq2, ts2)

    g1 = engine.check_tick(t1)
    assert g1 is None

    g2 = engine.check_tick(t2)
    assert g2 is not None
    assert g2.gap_id.startswith("MGP_")
    assert g2.missing_packets == (jump - 1)
    assert g2.reason == GapReason.SEQUENCE_DISCONTINUITY


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("time_jump", [10, 20, 30, 60])
def test_gap_detection_timestamp_jump_matrix(symbol, time_jump):
    engine = MarketGapDetectionEngine(max_allowed_time_gap_seconds=5.0)
    now = datetime.datetime.now(datetime.timezone.utc)
    ts1 = now.isoformat()
    ts2 = (now + datetime.timedelta(seconds=time_jump)).isoformat()

    t1 = make_tick(symbol, 1, ts1)
    t2 = make_tick(symbol, 2, ts2)

    engine.check_tick(t1)
    g2 = engine.check_tick(t2)
    assert g2 is not None
    assert g2.reason == GapReason.TIMESTAMP_JUMP
