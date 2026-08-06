"""
Project GOAT v1.0 — Test Suite for Chart Performance & Batch Processing (Step 1.6)
"""

import pytest
import time
from goat.market_data.persistence.tick_writer import BufferedTickWriter
from goat.market_data.models.tick import LiveTick


def test_buffered_tick_writer_throughput_performance():
    """Verify high-throughput batch writes to maintain 60 FPS chart rendering capability."""
    writer = BufferedTickWriter(db_path=":memory:", batch_size=50)

    ticks = [
        LiveTick(
            tick_id=f"LTK_{i:016x}",
            symbol="VOLATILITY_100",
            price=1000.0 + i,
            bid=999.9 + i,
            ask=1000.1 + i,
            spread=0.2,
            epoch_timestamp=1700000000 + i,
            arrival_timestamp="2026-08-06T12:00:00Z",
            sequence_number=i + 1,
            connection_id="CONN_PERF",
            latency_ms=10.0,
            checksum="CHK_PERF",
            metadata={},
            canonical_hash=f"HASH_PERF_{i}",
        )
        for i in range(100)
    ]

    t0 = time.time()
    for t in ticks:
        writer.write_tick_sync(t)
    elapsed = time.time() - t0

    # 100 ticks buffered & written under 0.1s
    assert elapsed < 0.1
    assert writer.get_total_writes() == 100
