"""
Project GOAT v1.0 — Test Suite for TradingView Datafeed Adapter (Step 1.6)
"""

import pytest
from goat.market_data.api.rest import MarketDataRESTHandler
from goat.market_data.engine import LiveMarketDataIngestionEngine


def test_tradingview_datafeed_backend_api_integration():
    """Verify backend endpoints powering TradingView JS Datafeed adapter."""
    engine = LiveMarketDataIngestionEngine(db_path=":memory:")
    handler = MarketDataRESTHandler(engine=engine)

    # Symbol list for Datafeed searchSymbols & resolveSymbol
    syms_resp = handler.get_symbols()
    assert syms_resp.status_code == 200
    assert len(syms_resp.data["symbols"]) == 8

    # History bars for Datafeed getBars
    hist_resp = handler.get_historical_candles("VOLATILITY_100", timeframe="1M", limit=50)
    assert hist_resp.status_code == 200
    assert "candles" in hist_resp.data

    # Latest bar for Datafeed subscribeBars streaming polling
    latest_resp = handler.get_latest_candle("VOLATILITY_100", timeframe="1M")
    assert latest_resp.status_code == 200
