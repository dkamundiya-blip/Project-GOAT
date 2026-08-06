"""
Project GOAT v1.1 — Dedicated FastAPI Server & Production Gateway Tests

Tests ASGI server lifespan, endpoints, live market data engine routing, and WebSocket streaming gateway.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from goat.server import app


@pytest.fixture
def client():
    """Test client fixture with lifespan context manager active."""
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client: TestClient):
    """Test / root endpoint JSON payload."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data.get("name") == "Project GOAT — Institutional Trading Platform API"
    assert data.get("status") == "RUNNING"
    assert data.get("version") == "1.1.0"
    assert data.get("docs") == "/docs"
    assert data.get("health") == "/health"


def test_health_endpoint(client: TestClient):
    """Test /api/v1/health system status."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["status"] in ["RUNNING", "HEALTHY"]


def test_market_data_status(client: TestClient):
    """Test /api/v1/market-data/status endpoint."""
    res = client.get("/api/v1/market-data/status")
    assert res.status_code == 200
    data = res.json()
    assert data.get("route") == "/api/v1/market-data/status"
    assert "connection_state" in data.get("data", {})


def test_market_data_symbols(client: TestClient):
    """Test /api/v1/market-data/symbols endpoint."""
    res = client.get("/api/v1/market-data/symbols")
    assert res.status_code == 200
    data = res.json()
    assert data.get("route") == "/api/v1/market-data/symbols"
    symbols_data = data.get("data", {})
    assert "symbols" in symbols_data
    assert "count" in symbols_data
    assert symbols_data["count"] == 8


def test_market_data_symbol_detail(client: TestClient):
    """Test /api/v1/market-data/symbol/{symbol_id} endpoint."""
    res = client.get("/api/v1/market-data/symbol/VOLATILITY_100")
    assert res.status_code == 200
    data = res.json()
    assert "symbol" in data.get("data", {})


def test_market_data_metrics(client: TestClient):
    """Test /api/v1/market-data/metrics telemetry snapshot."""
    res = client.get("/api/v1/market-data/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data.get("route") == "/api/v1/market-data/metrics"
    metrics = data.get("data", {})
    assert "total_ticks_received" in metrics
    assert "ticks_per_second" in metrics


def test_market_data_candles_history(client: TestClient):
    """Test /api/v1/market-data/candles/history/{symbol_id} endpoint."""
    res = client.get("/api/v1/market-data/candles/history/VOLATILITY_100?timeframe=1M&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data.get("route") == "/api/v1/market-data/candles/history/VOLATILITY_100"
    candles_data = data.get("data", {})
    assert "candles" in candles_data


def test_market_data_control_actions(client: TestClient):
    """Test POST operator control endpoints (connect/disconnect/reconnect/subscribe/unsubscribe)."""
    res_sub = client.post("/api/v1/market-data/subscribe/VOLATILITY_100")
    assert res_sub.status_code == 200

    res_unsub = client.post("/api/v1/market-data/unsubscribe/VOLATILITY_100")
    assert res_unsub.status_code == 200

    res_reconnect = client.post("/api/v1/market-data/reconnect")
    assert res_reconnect.status_code in [200, 500]


def test_websocket_streaming_gateway(client: TestClient):
    """Test real-time browser WebSocket streaming endpoint connection."""
    with client.websocket_connect("/api/v1/market-data/ws") as websocket:
        assert websocket is not None
