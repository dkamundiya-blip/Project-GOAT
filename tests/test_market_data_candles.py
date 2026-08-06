"""
Project GOAT v1.0 — Test Suite for Multi-Timeframe Live Candle Builder
"""

import pytest
import sqlite3
from goat.market_data.candles import LiveCandleBuilder, floor_timestamp_to_interval
from goat.market_data.models import LiveTick, compute_live_tick_id


def test_floor_timestamp_to_interval():
    """Verify floor_timestamp_to_interval boundary calculation."""
    # 1700000000 is Tue Nov 14 2023 22:13:20 UTC
    open_iso, close_iso = floor_timestamp_to_interval(1700000000, "1M")
    # 22:13:20 floored to 1M is 22:13:00 -> 22:14:00
    assert "22:13:00" in open_iso
    assert "22:14:00" in close_iso

    open_5m, close_5m = floor_timestamp_to_interval(1700000000, "5M")
    # 22:13:20 floored to 5M is 22:10:00 -> 22:15:00
    assert "22:10:00" in open_5m
    assert "22:15:00" in close_5m


def test_live_candle_builder_tick_aggregation():
    """Verify ticks forming candles and closing on interval boundary."""
    conn = sqlite3.connect(":memory:")
    builder = LiveCandleBuilder(db_conn=conn, timeframes=["1M"])

    # Tick 1 at 22:13:10 UTC (epoch 1700000000)
    t_id1, h1 = compute_live_tick_id("VOLATILITY_100", 100.0, 99.9, 100.1, 1700000000, 1)
    tick1 = LiveTick(
        tick_id=t_id1,
        symbol="VOLATILITY_100",
        price=100.0,
        bid=99.9,
        ask=100.1,
        spread=0.2,
        epoch_timestamp=1700000000,
        arrival_timestamp="2023-11-14T22:13:10Z",
        sequence_number=1,
        checksum="C1",
        canonical_hash=h1,
    )

    closed1 = builder.process_tick(tick1)
    assert len(closed1) == 0  # Still forming, not closed

    forming = builder.get_latest_candle("VOLATILITY_100", "1M")
    assert forming is not None
    assert forming.open == 100.0
    assert forming.high == 100.0
    assert forming.low == 100.0
    assert forming.close == 100.0
    assert forming.volume == 1.0

    # Tick 2 at 22:13:40 UTC (same 1M bar, high 105, low 98)
    t_id2, h2 = compute_live_tick_id("VOLATILITY_100", 105.0, 104.9, 105.1, 1700000030, 2)
    tick2 = LiveTick(
        tick_id=t_id2,
        symbol="VOLATILITY_100",
        price=105.0,
        bid=104.9,
        ask=105.1,
        spread=0.2,
        epoch_timestamp=1700000030,
        arrival_timestamp="2023-11-14T22:13:40Z",
        sequence_number=2,
        checksum="C2",
        canonical_hash=h2,
    )
    builder.process_tick(tick2)

    forming2 = builder.get_latest_candle("VOLATILITY_100", "1M")
    assert forming2.high == 105.0
    assert forming2.close == 105.0
    assert forming2.volume == 2.0

    # Tick 3 at 22:14:05 UTC (epoch 1700000055 -> NEXT 1M BAR)
    t_id3, h3 = compute_live_tick_id("VOLATILITY_100", 102.0, 101.9, 102.1, 1700000055, 3)
    tick3 = LiveTick(
        tick_id=t_id3,
        symbol="VOLATILITY_100",
        price=102.0,
        bid=101.9,
        ask=102.1,
        spread=0.2,
        epoch_timestamp=1700000055,
        arrival_timestamp="2023-11-14T22:14:05Z",
        sequence_number=3,
        checksum="C3",
        canonical_hash=h3,
    )
    closed_bars = builder.process_tick(tick3)
    assert len(closed_bars) == 1
    assert closed_bars[0].completed is True
    assert closed_bars[0].open == 100.0
    assert closed_bars[0].high == 105.0
    assert closed_bars[0].close == 105.0

    # Verify historical retrieval from SQLite DB
    history = builder.get_historical_candles("VOLATILITY_100", "1M", limit=10)
    assert len(history) == 1
    assert history[0].candle_id == closed_bars[0].candle_id
