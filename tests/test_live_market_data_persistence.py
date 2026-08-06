"""
Project GOAT v0.8 — Test Suite: SQLite Persistence & Round-Trip Repositories (Exhaustive Matrix)
"""

import sqlite3
import pytest

from goat.marketdata.core.canonical import (
    compute_candle_id,
    compute_gap_id,
    compute_replay_id,
    compute_stream_id,
    compute_tick_id,
)
from goat.marketdata.core.enums import DerivSymbol, GapReason, MarketTimeframe, StreamConnectionStatus
from goat.marketdata.core.models import (
    MarketCandle,
    MarketGap,
    MarketStreamState,
    MarketTick,
    ReplaySnapshot,
)
from goat.marketdata.persistence.repository import (
    MarketCandleRepository,
    MarketGapRepository,
    MarketStreamRepository,
    MarketTickRepository,
    ReplaySnapshotRepository,
    init_marketdata_db,
)

SYMBOLS = [s.value for s in DerivSymbol]


@pytest.fixture
def db_conn():
    conn = init_marketdata_db(":memory:")
    yield conn
    conn.close()


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_market_tick_persistence_roundtrip_matrix(db_conn, symbol):
    repo = MarketTickRepository(db_conn)
    tick_id, canonical_hash = compute_tick_id(symbol, "DERIV", 100.0, 100.2, "2026-07-31T12:00:00Z", 1)
    tick = MarketTick(
        tick_id=tick_id,
        symbol=symbol,
        broker="DERIV",
        bid=100.0,
        ask=100.2,
        spread=0.2,
        timestamp="2026-07-31T12:00:00Z",
        sequence_number=1,
        source_latency=5.0,
        checksum="CHECKSUM123",
        metadata={"test": symbol},
        canonical_hash=canonical_hash,
    )

    repo.save(tick)
    fetched = repo.get_by_id(tick_id)

    assert fetched is not None
    assert fetched.tick_id == tick.tick_id
    assert fetched.symbol == symbol
    assert fetched.bid == 100.0
    assert fetched.metadata == {"test": symbol}


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_market_candle_persistence_roundtrip_matrix(db_conn, symbol):
    repo = MarketCandleRepository(db_conn)
    candle_id, canonical_hash = compute_candle_id(
        symbol, "1M", 100.0, 105.0, 99.0, 102.0, "2026-07-31T12:00:00Z", "2026-07-31T12:01:00Z"
    )
    candle = MarketCandle(
        candle_id=candle_id,
        symbol=symbol,
        timeframe=MarketTimeframe.M1,
        open=100.0,
        high=105.0,
        low=99.0,
        close=102.0,
        volume=10.0,
        open_timestamp="2026-07-31T12:00:00Z",
        close_timestamp="2026-07-31T12:01:00Z",
        completed=True,
        checksum="CHECKSUM123",
        metadata={"sym": symbol},
        canonical_hash=canonical_hash,
    )

    repo.save(candle)
    fetched = repo.get_by_id(candle_id)

    assert fetched is not None
    assert fetched.candle_id == candle.candle_id
    assert fetched.high == 105.0


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_stream_state_persistence_roundtrip_matrix(db_conn, symbol):
    repo = MarketStreamRepository(db_conn)
    stream_id, canonical_hash = compute_stream_id("DERIV", symbol, "2026-07-31T12:00:00Z")
    stream = MarketStreamState(
        stream_id=stream_id,
        broker="DERIV",
        symbol=symbol,
        connection_status=StreamConnectionStatus.CONNECTED,
        heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=12.5,
        packets_received=50,
        packets_dropped=0,
        reconnect_count=1,
        canonical_hash=canonical_hash,
    )

    repo.save(stream)
    fetched = repo.get_by_id(stream_id)
    assert fetched is not None
    assert fetched.symbol == symbol
    assert fetched.packets_received == 50


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_gap_and_replay_persistence_matrix(db_conn, symbol):
    gap_repo = MarketGapRepository(db_conn)
    gap_id, g_hash = compute_gap_id(symbol, "2026-07-31T12:00:00Z", "2026-07-31T12:00:05Z", "SEQUENCE_DISCONTINUITY")
    gap = MarketGap(
        gap_id=gap_id,
        symbol=symbol,
        start_timestamp="2026-07-31T12:00:00Z",
        end_timestamp="2026-07-31T12:00:05Z",
        missing_packets=3,
        reason=GapReason.SEQUENCE_DISCONTINUITY,
        metadata={},
        canonical_hash=g_hash,
    )
    gap_repo.save(gap)
    assert gap_repo.get_by_id(gap_id) is not None

    replay_repo = ReplaySnapshotRepository(db_conn)
    r_id, r_hash = compute_replay_id(symbol, "2026-07-31T12:00:00Z", f"REF_{symbol}")
    snap = ReplaySnapshot(
        replay_id=r_id,
        symbol=symbol,
        replay_timestamp="2026-07-31T12:00:00Z",
        replay_checksum="HASH123",
        snapshot_reference=f"REF_{symbol}",
        metadata={},
        canonical_hash=r_hash,
    )
    replay_repo.save(snap)
    assert replay_repo.get_by_id(r_id) is not None
