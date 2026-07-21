"""
Project GOAT v0.2 — Unit Tests for Deriv Schemas & Adapter
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from goat.data.collector.deriv_schemas import DerivSymbolMetadata, DerivTickPayload
from goat.data.schemas import DataSource


def test_active_symbols_current_format() -> None:
    """Test parsing current Deriv active_symbols API response format."""
    current_data = {
        "underlying_symbol": "R_75",
        "underlying_symbol_name": "Volatility 75 Index",
        "market": "synthetic_index",
        "submarket": "random_index",
        "is_trading_suspended": 0,
        "pip_size": 4,
    }
    meta = DerivSymbolMetadata.from_active_symbol_dict(current_data)
    assert meta.symbol == "R_75"
    assert meta.display_name == "Volatility 75 Index"
    assert meta.market == "synthetic_index"
    assert meta.submarket == "random_index"
    assert meta.is_trading_suspended is False
    assert meta.pip_size == 4


def test_active_symbols_legacy_format() -> None:
    """Test parsing legacy Deriv active_symbols API response format."""
    legacy_data = {
        "symbol": "R_10",
        "display_name": "Volatility 10 Index",
        "market_name": "synthetic_index",
        "submarket_name": "random_index",
        "is_trading_suspended": 1,
        "pip": 0.001,
    }
    meta = DerivSymbolMetadata.from_active_symbol_dict(legacy_data)
    assert meta.symbol == "R_10"
    assert meta.display_name == "Volatility 10 Index"
    assert meta.is_trading_suspended is True
    assert meta.pip_size == 3


def test_active_symbols_missing_symbol_raises() -> None:
    """Test that active_symbols dict without symbol raises ValueError."""
    with pytest.raises(ValueError, match="missing symbol"):
        DerivSymbolMetadata.from_active_symbol_dict({"display_name": "No Symbol"})


def test_deriv_tick_payload_conversion() -> None:
    """Test Deriv tick payload parsing and conversion to canonical GOAT Tick."""
    raw_tick = {
        "symbol": "R_75",
        "quote": 751.2345,
        "epoch": 1721623200,
        "id": "tick_12345",
        "pip_size": 4,
        "ask": 751.24,
        "bid": 751.22,
    }
    payload = DerivTickPayload.from_tick_dict(raw_tick)
    assert payload.symbol == "R_75"
    assert payload.quote == Decimal("751.2345")
    assert payload.epoch == 1721623200

    tick = payload.to_goat_tick(source=DataSource.LIVE)
    assert tick.symbol == "R_75"
    assert tick.price == Decimal("751.2345")
    assert tick.timestamp == datetime(2024, 7, 22, 4, 40, 0, tzinfo=timezone.utc)
    assert tick.tick_id == "tick_12345"
    assert tick.source == DataSource.LIVE
    assert tick.metadata["provider"] == "deriv"
    assert tick.metadata["ask"] == 751.24


def test_deriv_tick_payload_missing_quote_raises() -> None:
    """Test that tick dict without quote raises ValueError."""
    with pytest.raises(ValueError, match="missing quote"):
        DerivTickPayload.from_tick_dict({"symbol": "R_75", "epoch": 1721623200})
