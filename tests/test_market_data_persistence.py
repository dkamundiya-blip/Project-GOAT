"""
Project GOAT v1.0 — Test Suite for Market Data Persistence
"""

import sqlite3
import pytest
from goat.market_data.models import LiveTick, compute_live_tick_id
from goat.market_data.persistence import BufferedTickWriter, LiveTickBuffer, init_live_market_data_db


def test_live_tick_buffer():
    """Verify in-memory sliding window tick ring buffer."""
    buf = LiveTickBuffer(max_ticks_per_symbol=5)
    tick_id, canonical_hash = compute_live_tick_id(
        symbol="VOLATILITY_100",
        price=100.0,
        bid=99.9,
        ask=100.1,
        epoch_timestamp=1700000000,
        sequence_number=1,
    )

    tick = LiveTick(
        tick_id=tick_id,
        symbol="VOLATILITY_100",
        price=100.0,
        bid=99.9,
        ask=100.1,
        spread=0.2,
        epoch_timestamp=1700000000,
        arrival_timestamp="2026-08-06T12:00:00Z",
        sequence_number=1,
        connection_id="CONN_01",
        latency_ms=10.0,
        checksum="CHK",
        canonical_hash=canonical_hash,
    )

    buf.append_tick(tick)
    assert buf.total_ticks_received == 1

    latest = buf.get_latest_tick("VOLATILITY_100")
    assert latest is not None
    assert latest.tick_id == tick_id

    quote = buf.get_live_quote("VOLATILITY_100")
    assert quote.symbol == "VOLATILITY_100"
    assert quote.live_price == 100.0


def test_buffered_tick_writer_sqlite():
    """Verify BufferedTickWriter SQLite batch insertion and round-trip retrieval."""
    conn = init_live_market_data_db(":memory:")
    writer = BufferedTickWriter(db_conn=conn, batch_size=2)

    tick_id1, hash1 = compute_live_tick_id("VOLATILITY_25", 200.0, 199.9, 200.1, 1700000001, 1)
    t1 = LiveTick(
        tick_id=tick_id1,
        symbol="VOLATILITY_25",
        price=200.0,
        bid=199.9,
        ask=200.1,
        spread=0.2,
        epoch_timestamp=1700000001,
        arrival_timestamp="2026-08-06T12:00:01Z",
        sequence_number=1,
        connection_id="CONN_01",
        latency_ms=12.0,
        checksum="CHK1",
        canonical_hash=hash1,
    )

    tick_id2, hash2 = compute_live_tick_id("VOLATILITY_25", 200.5, 200.4, 200.6, 1700000002, 2)
    t2 = LiveTick(
        tick_id=tick_id2,
        symbol="VOLATILITY_25",
        price=200.5,
        bid=200.4,
        ask=200.6,
        spread=0.2,
        epoch_timestamp=1700000002,
        arrival_timestamp="2026-08-06T12:00:02Z",
        sequence_number=2,
        connection_id="CONN_01",
        latency_ms=11.5,
        checksum="CHK2",
        canonical_hash=hash2,
    )

    writer.write_tick_sync(t1)
    assert writer.get_buffer_size() == 1

    writer.write_tick_sync(t2)
    # Batch size reached -> flushed to SQLite DB
    assert writer.get_buffer_size() == 0
    assert writer.get_total_writes() == 2

    # Query back from DB
    retrieved = writer.get_ticks_from_db("VOLATILITY_25", limit=10)
    assert len(retrieved) == 2
    assert retrieved[0].tick_id == tick_id1
    assert retrieved[1].tick_id == tick_id2
    assert retrieved[0].price == 200.0
    assert retrieved[1].price == 200.5
