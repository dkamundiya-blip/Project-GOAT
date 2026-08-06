"""
Project GOAT v1.0 — Public API Import & Contract Test Suite (Step 1.6)
"""

import pytest


def test_market_data_public_api_exports():
    """Verify all public exports of goat.market_data are importable and valid."""
    from goat.market_data import LiveMarketDataIngestionEngine
    from goat.market_data.api import MarketDataAPIRouter, MarketDataRESTHandler
    from goat.market_data.candles import LiveCandleBuilder
    from goat.market_data.models import LiveQuote, LiveTick, DerivSymbolConfig, SUPPORTED_SYMBOLS
    from goat.market_data.normalization import TickNormalizer
    from goat.market_data.persistence import BufferedTickWriter, LiveTickBuffer
    from goat.market_data.telemetry import IngestionMetricsCollector, LatencyTracker
    from goat.market_data.websocket import DerivWebSocketClient, WebSocketManager

    assert LiveMarketDataIngestionEngine is not None
    assert MarketDataAPIRouter is not None
    assert MarketDataRESTHandler is not None
    assert LiveCandleBuilder is not None
    assert LiveQuote is not None
    assert LiveTick is not None
    assert DerivSymbolConfig is not None
    assert len(SUPPORTED_SYMBOLS) == 8
    assert TickNormalizer is not None
    assert BufferedTickWriter is not None
    assert LiveTickBuffer is not None
    assert IngestionMetricsCollector is not None
    assert LatencyTracker is not None
    assert DerivWebSocketClient is not None
    assert WebSocketManager is not None
