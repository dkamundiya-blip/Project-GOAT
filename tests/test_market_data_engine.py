"""
Project GOAT v1.0 — Test Suite for LiveMarketDataIngestionEngine
"""

import pytest
import asyncio
from goat.market_data.engine import LiveMarketDataIngestionEngine


@pytest.mark.asyncio
async def test_engine_lifecycle_and_tick_processing():
    """Verify master engine lifecycle, tick pipeline processing, and candle construction."""
    engine = LiveMarketDataIngestionEngine(db_path=":memory:")

    await engine.start()
    assert engine._is_running is True

    raw_payload = {
        "msg_type": "tick",
        "tick": {
            "symbol": "R_100",
            "quote": 1250.0,
            "pip_size": 2,
            "epoch": 1700000000,
            "bid": 1249.9,
            "ask": 1250.1,
        },
    }

    # Simulate raw tick arrival from WebSocket
    await engine._on_raw_tick_received(raw_payload)

    # Check buffer
    quote = engine.get_symbol_quote("VOLATILITY_100")
    assert quote.symbol == "VOLATILITY_100"
    assert quote.live_price == 1250.0
    assert quote.bid == 1249.9
    assert quote.ask == 1250.1

    # Check recent ticks
    ticks = engine.get_recent_ticks("VOLATILITY_100", limit=10)
    assert len(ticks) == 1
    assert ticks[0].price == 1250.0

    # Check latest forming candle
    candle = engine.get_latest_candle("VOLATILITY_100", timeframe="1M")
    assert candle is not None
    assert candle.open == 1250.0

    # Check telemetry
    telemetry = engine.get_telemetry_snapshot()
    assert telemetry.total_ticks_received == 1

    await engine.stop()
    assert engine._is_running is False
