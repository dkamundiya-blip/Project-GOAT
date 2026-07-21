"""
Project GOAT v0.2 — Unit Tests for Deriv Symbol Discovery
"""

from unittest.mock import AsyncMock

import pytest

from goat.data.collector.discovery import DerivSymbolDiscovery


@pytest.mark.asyncio
async def test_deriv_symbol_discovery_with_allowlist() -> None:
    """Test symbol discovery with allowlist filtering."""
    mock_collector = AsyncMock()
    mock_collector.request.return_value = {
        "active_symbols": [
            {
                "underlying_symbol": "R_10",
                "underlying_symbol_name": "Volatility 10 Index",
                "market": "synthetic_index",
                "submarket": "random_index",
                "is_trading_suspended": 0,
                "pip_size": 3,
            },
            {
                "underlying_symbol": "R_50",
                "underlying_symbol_name": "Volatility 50 Index",
                "market": "synthetic_index",
                "submarket": "random_index",
                "is_trading_suspended": 0,
                "pip_size": 4,
            },
            {
                "underlying_symbol": "R_75",
                "underlying_symbol_name": "Volatility 75 Index",
                "market": "synthetic_index",
                "submarket": "random_index",
                "is_trading_suspended": 0,
                "pip_size": 4,
            },
        ]
    }

    discovery = DerivSymbolDiscovery(mock_collector)
    discovered = await discovery.fetch_active_symbols(allowlist=["R_10", "R_75"])

    assert len(discovered) == 2
    symbols = [s.symbol for s in discovered]
    assert "R_10" in symbols
    assert "R_75" in symbols
    assert "R_50" not in symbols
