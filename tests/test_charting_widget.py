"""
Project GOAT v1.0 — Test Suite for Charting Widget Server-Side Contracts (Step 1.6)
"""

import pytest
from goat.market_data.candles.builder import LiveCandleBuilder
from goat.market_data.models.tick import LiveTick


def test_charting_widget_ohlc_integrity():
    """Verify OHLC bar integrity for rendering in TradingView canvas widget."""
    builder = LiveCandleBuilder()
    tick1 = LiveTick(
        tick_id="LTK_0123456789abcdef",
        symbol="VOLATILITY_100",
        price=100.0,
        bid=99.9,
        ask=100.1,
        spread=0.2,
        epoch_timestamp=1700000000,
        arrival_timestamp="2026-08-06T12:00:00Z",
        sequence_number=1,
        connection_id="CONN1",
        latency_ms=10.0,
        checksum="CHK1",
        metadata={},
        canonical_hash="HASH1",
    )
    tick2 = LiveTick(
        tick_id="LTK_fedcba9876543210",
        symbol="VOLATILITY_100",
        price=105.0,
        bid=104.9,
        ask=105.1,
        spread=0.2,
        epoch_timestamp=1700000010,
        arrival_timestamp="2026-08-06T12:00:10Z",
        sequence_number=2,
        connection_id="CONN1",
        latency_ms=10.0,
        checksum="CHK2",
        metadata={},
        canonical_hash="HASH2",
    )

    builder.process_tick(tick1)
    builder.process_tick(tick2)

    candle = builder.get_latest_candle("VOLATILITY_100", timeframe="1M")
    assert candle is not None
    assert candle.open == 100.0
    assert candle.high == 105.0
    assert candle.low == 100.0
    assert candle.close == 105.0
    assert candle.volume == 2
