"""
Project GOAT v1.0 — Test Suite for Market Data REST API & Router
"""

import pytest
from goat.market_data.api import MarketDataAPIRouter, MarketDataRESTHandler
from goat.market_data.engine import LiveMarketDataIngestionEngine


@pytest.fixture
def engine():
    return LiveMarketDataIngestionEngine()


@pytest.fixture
def router(engine):
    return MarketDataAPIRouter(engine)


def test_api_status_endpoint(router):
    """Verify GET /api/v1/market-data/status response format."""
    res = router.dispatch("/api/v1/market-data/status")
    assert res is not None
    assert res.status_code == 200
    assert "connection_state" in res.data
    assert "total_ticks_received" in res.data


def test_api_symbols_endpoint(router):
    """Verify GET /api/v1/market-data/symbols response format."""
    res = router.dispatch("/api/v1/market-data/symbols")
    assert res is not None
    assert res.status_code == 200
    assert "symbols" in res.data
    assert res.data["count"] == 8


def test_api_symbol_detail_endpoint(router):
    """Verify GET /api/v1/market-data/symbol/{symbol_id} response format."""
    res = router.dispatch("/api/v1/market-data/symbol/VOLATILITY_100")
    assert res is not None
    assert res.status_code == 200
    assert res.data["symbol"] == "VOLATILITY_100"


def test_api_ticks_endpoint(router):
    """Verify GET /api/v1/market-data/ticks/{symbol_id} response format."""
    res = router.dispatch("/api/v1/market-data/ticks/VOLATILITY_10", limit=10)
    assert res is not None
    assert res.status_code == 200
    assert res.data["symbol"] == "VOLATILITY_10"
    assert "ticks" in res.data


def test_api_candles_latest_endpoint(router):
    """Verify GET /api/v1/market-data/candles/latest/{symbol_id} response format."""
    res = router.dispatch("/api/v1/market-data/candles/latest/VOLATILITY_100", timeframe="1M")
    assert res is not None
    assert res.status_code == 200
    assert res.data["symbol"] == "VOLATILITY_100"
    assert res.data["timeframe"] == "1M"


def test_api_candles_history_endpoint(router):
    """Verify GET /api/v1/market-data/candles/history/{symbol_id} response format."""
    res = router.dispatch("/api/v1/market-data/candles/history/VOLATILITY_100", timeframe="1M", limit=50)
    assert res is not None
    assert res.status_code == 200
    assert res.data["symbol"] == "VOLATILITY_100"
    assert "candles" in res.data


def test_api_metrics_endpoint(router):
    """Verify GET /api/v1/market-data/metrics response format."""
    res = router.dispatch("/api/v1/market-data/metrics")
    assert res is not None
    assert res.status_code == 200
    assert "cpu_usage_percent" in res.data
    assert "memory_usage_mb" in res.data


@pytest.mark.asyncio
async def test_api_async_control_endpoints(router):
    """Verify POST control endpoints for connect/disconnect/subscribe/unsubscribe."""
    res1 = await router.dispatch_async("/api/v1/market-data/subscribe/VOLATILITY_50")
    assert res1 is not None
    assert res1.status_code == 200
    assert res1.data["success"] is True

    res2 = await router.dispatch_async("/api/v1/market-data/unsubscribe/VOLATILITY_50")
    assert res2 is not None
    assert res2.status_code == 200
    assert res2.data["success"] is True
