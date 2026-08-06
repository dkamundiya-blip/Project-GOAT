"""
Project GOAT v1.0 — Test Suite for Dashboard Chart Integration (Step 1.6)
"""

import pytest
from goat.dashboard.api.router import DashboardAPIRouter, create_dashboard_router
from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.telemetry.collector import SystemTelemetryCollector
from goat.market_data.engine import LiveMarketDataIngestionEngine


def test_dashboard_router_market_data_chart_route_dispatch():
    """Verify DashboardAPIRouter dispatches market-data chart endpoints correctly."""
    repo = DashboardReadOnlyRepositoryAdapter()
    collector = SystemTelemetryCollector()
    market_engine = LiveMarketDataIngestionEngine(db_path=":memory:")

    router = create_dashboard_router(repo=repo, collector=collector, market_data_engine=market_engine)

    # Route /api/v1/market-data/status
    res = router.dispatch("/api/v1/market-data/status")
    assert res is not None
    assert res.status_code == 200

    # Route /api/v1/market-data/candles/latest/VOLATILITY_100
    res_candle = router.dispatch("/api/v1/market-data/candles/latest/VOLATILITY_100", timeframe="1M")
    assert res_candle is not None
    assert res_candle.status_code == 200
