"""
Project GOAT v1.0 — Test Suite for TradingView Provider Interface (Step 1.6)
"""

import pytest
from goat.market_data.api.router import MarketDataAPIRouter
from goat.market_data.engine import LiveMarketDataIngestionEngine


def test_tradingview_provider_router_dispatch():
    """Verify APIRouter correctly dispatches datafeed requests."""
    engine = LiveMarketDataIngestionEngine(db_path=":memory:")
    router = MarketDataAPIRouter(engine=engine)

    res = router.dispatch("/api/v1/market-data/status")
    assert res is not None
    assert res.status_code == 200

    res_candles = router.dispatch("/api/v1/market-data/candles/history/VOLATILITY_100", timeframe="1M", limit=10)
    assert res_candles is not None
    assert res_candles.status_code == 200
