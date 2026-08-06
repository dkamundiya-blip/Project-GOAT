"""
Project GOAT v0.8 — Test Suite: Core Market Data Models & Deterministic IDs (Exhaustive)
"""

import pytest
from pydantic import ValidationError

from goat.marketdata.core.canonical import (
    compute_candle_id,
    compute_gap_id,
    compute_replay_id,
    compute_report_id,
    compute_stream_id,
    compute_tick_id,
)
from goat.marketdata.core.enums import (
    DerivSymbol,
    GapReason,
    MarketTimeframe,
    SafetyGateStatus,
    StreamConnectionStatus,
)
from goat.marketdata.core.models import (
    MarketCandle,
    MarketGap,
    MarketStreamState,
    MarketTick,
    ReplaySnapshot,
)

SYMBOLS = [s.value for s in DerivSymbol]
PRICE_LEVELS = [0.01, 0.5, 1.0, 100.0, 1234.56, 99999.99]
TIME_FRAMES = [t.value for t in MarketTimeframe]
GAP_REASONS = [g.value for g in GapReason]
STREAM_STATUSES = [s.value for s in StreamConnectionStatus]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("bid", [1.0, 100.0, 1234.56])
@pytest.mark.parametrize("spread", [0.01, 0.1, 1.0])
def test_market_tick_immutability_matrix(symbol, bid, spread):
    ask = bid + spread
    tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", bid, ask, "2026-07-31T12:00:00Z", 1)
    tick = MarketTick(
        tick_id=tick_id,
        symbol=symbol,
        broker="DERIV",
        bid=bid,
        ask=ask,
        spread=spread,
        timestamp="2026-07-31T12:00:00Z",
        sequence_number=1,
        source_latency=5.0,
        checksum="CHECKSUM123",
        metadata={"sym": symbol},
        canonical_hash=canonical_hash,
    )

    assert tick.tick_id.startswith("MTK_")
    assert tick.mid_price == round((bid + ask) / 2.0, 8)
    assert tick.spread == spread

    with pytest.raises(ValidationError):
        tick.bid = bid + 10.0


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("tf", TIME_FRAMES)
def test_market_candle_immutability_matrix(symbol, tf):
    candle_id, canonical_hash = compute_candle_id(
        symbol, tf, 100.0, 105.0, 99.0, 102.0, "2026-07-31T12:00:00Z", "2026-07-31T12:01:00Z"
    )
    candle = MarketCandle(
        candle_id=candle_id,
        symbol=symbol,
        timeframe=MarketTimeframe(tf),
        open=100.0,
        high=105.0,
        low=99.0,
        close=102.0,
        volume=50.0,
        open_timestamp="2026-07-31T12:00:00Z",
        close_timestamp="2026-07-31T12:01:00Z",
        completed=True,
        checksum="CHECKSUM123",
        metadata={},
        canonical_hash=canonical_hash,
    )

    assert candle.candle_id.startswith("MCD_")
    assert candle.is_bullish is True
    assert candle.range == 6.0

    with pytest.raises(ValidationError):
        candle.close = 90.0


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("status", STREAM_STATUSES)
def test_market_stream_state_matrix(symbol, status):
    stream_id, canonical_hash = compute_stream_id("DERIV", symbol, "2026-07-31T12:00:00Z")
    stream = MarketStreamState(
        stream_id=stream_id,
        broker="DERIV",
        symbol=symbol,
        connection_status=StreamConnectionStatus(status),
        heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=15.0,
        packets_received=100,
        packets_dropped=0,
        reconnect_count=0,
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert stream.stream_id.startswith("MSS_")
    assert stream.connection_status.value == status


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("reason", GAP_REASONS)
def test_market_gap_matrix(symbol, reason):
    gap_id, canonical_hash = compute_gap_id(symbol, "2026-07-31T12:00:00Z", "2026-07-31T12:00:10Z", reason)
    gap = MarketGap(
        gap_id=gap_id,
        symbol=symbol,
        start_timestamp="2026-07-31T12:00:00Z",
        end_timestamp="2026-07-31T12:00:10Z",
        missing_packets=5,
        reason=GapReason(reason),
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert gap.gap_id.startswith("MGP_")
    assert gap.reason.value == reason


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_replay_snapshot_matrix(symbol):
    replay_id, canonical_hash = compute_replay_id(symbol, "2026-07-31T12:00:00Z", f"REF_{symbol}")
    snap = ReplaySnapshot(
        replay_id=replay_id,
        symbol=symbol,
        replay_timestamp="2026-07-31T12:00:00Z",
        replay_checksum="HASH12345",
        snapshot_reference=f"REF_{symbol}",
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert snap.replay_id.startswith("RPS_")


@pytest.mark.parametrize("seq", [0, 1, 10, 100, 9999])
def test_deterministic_id_reproducibility(seq):
    id1, hash1 = compute_tick_id("R_100", "DERIV", 10.0, 10.2, "2026-07-31T12:00:00Z", seq)
    id2, hash2 = compute_tick_id("R_100", "DERIV", 10.0, 10.2, "2026-07-31T12:00:00Z", seq)
    assert id1 == id2
    assert hash1 == hash2
