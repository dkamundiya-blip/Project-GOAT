"""
Project GOAT v1.0 — Test Suite for Chart State Contracts (Step 1.6)
"""

import pytest
from goat.market_data.persistence.buffer import LiveTickBuffer
from goat.market_data.models.tick import LiveTick


def test_chart_state_snapshot_reproducibility():
    """Verify live quote state snapshots for active chart instruments."""
    buffer = LiveTickBuffer()
    tick = LiveTick(
        tick_id="LTK_0123456789abcdef",
        symbol="VOLATILITY_75",
        price=350.25,
        bid=350.20,
        ask=350.30,
        spread=0.10,
        epoch_timestamp=1700000000,
        arrival_timestamp="2026-08-06T12:00:00Z",
        sequence_number=1,
        connection_id="CONN_WS",
        latency_ms=12.5,
        checksum="CHK_SNAP",
        metadata={},
        canonical_hash="HASH_SNAP",
    )
    buffer.append_tick(tick)

    quote = buffer.get_live_quote("VOLATILITY_75", connection_status="CONNECTED")
    assert quote.symbol == "VOLATILITY_75"
    assert quote.live_price == 350.25
    assert quote.connection_status == "CONNECTED"
