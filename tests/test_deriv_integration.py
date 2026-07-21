"""
Project GOAT v0.2 — Optional Live External Connectivity Smoke Test

This test connects to Deriv's public WebSocket market data endpoint.
It is SKIPPED by default during automated deterministic unit testing.

To execute manually:
    $env:RUN_INTEGRATION_TESTS="1"; pytest tests/test_deriv_integration.py
"""

import os
from datetime import datetime, timedelta, timezone

import pytest

from goat.data.collector.deriv import DerivMarketDataCollector
from goat.data.collector.discovery import DerivSymbolDiscovery
from goat.data.schemas import DataSource

RUN_INTEGRATION = os.getenv("RUN_INTEGRATION_TESTS") == "1"


@pytest.mark.skipif(not RUN_INTEGRATION, reason="Requires RUN_INTEGRATION_TESTS=1 environment variable")
@pytest.mark.asyncio
async def test_live_deriv_public_market_data_connectivity() -> None:
    """Manually invoked integration test for live public market data acquisition."""
    collector = DerivMarketDataCollector()

    async with collector:
        # 1. Symbol discovery
        discovery = DerivSymbolDiscovery(collector)
        symbols = await discovery.fetch_active_symbols(allowlist=["R_10"])
        assert len(symbols) > 0
        assert symbols[0].symbol == "R_10"

        # 2. Collect 2 live ticks
        collected_ticks = []
        start = datetime.now(timezone.utc)
        end = start + timedelta(seconds=15)

        async for tick in collector.collect_ticks("R_10", start, end):
            collected_ticks.append(tick)
            if len(collected_ticks) >= 2:
                break

        assert len(collected_ticks) >= 2
        assert collected_ticks[0].symbol == "R_10"
        assert collected_ticks[0].source == DataSource.LIVE
        assert collected_ticks[0].price > 0
