"""
Project GOAT v1.0 — Test Suite for Market Data Models
"""

import pytest
from pydantic import ValidationError

from goat.market_data.models import (
    SUPPORTED_SYMBOLS,
    DerivSymbolConfig,
    LiveQuote,
    LiveTick,
    SymbolType,
    compute_live_tick_id,
    get_symbol_config,
)


def test_supported_symbols_registry():
    """Verify all 8 mandatory symbols exist in registry."""
    mandatory = [
        "VOLATILITY_10",
        "VOLATILITY_25",
        "VOLATILITY_50",
        "VOLATILITY_75",
        "VOLATILITY_100",
        "BOOM_1000",
        "CRASH_1000",
        "STEP_INDEX",
    ]
    for sym in mandatory:
        assert sym in SUPPORTED_SYMBOLS
        cfg = get_symbol_config(sym)
        assert cfg is not None
        assert cfg.symbol_id == sym
        assert len(cfg.deriv_ws_symbol) > 0


def test_symbol_resolution_by_deriv_ws():
    """Verify resolving by Deriv WS API string."""
    cfg = get_symbol_config("R_100")
    assert cfg is not None
    assert cfg.symbol_id == "VOLATILITY_100"

    cfg_step = get_symbol_config("stpRNG")
    assert cfg_step is not None
    assert cfg_step.symbol_id == "STEP_INDEX"


def test_live_tick_deterministic_id_reproducibility():
    """Verify ID generation is deterministic and reproducible."""
    tick_id1, hash1 = compute_live_tick_id(
        symbol="VOLATILITY_100",
        price=1234.56,
        bid=1234.50,
        ask=1234.62,
        epoch_timestamp=1700000000,
        sequence_number=1,
    )
    tick_id2, hash2 = compute_live_tick_id(
        symbol="VOLATILITY_100",
        price=1234.56,
        bid=1234.50,
        ask=1234.62,
        epoch_timestamp=1700000000,
        sequence_number=1,
    )
    assert tick_id1 == tick_id2
    assert hash1 == hash2
    assert tick_id1.startswith("LTK_")
    assert len(tick_id1) == 20  # LTK_ + 16 hex chars


def test_live_tick_immutability():
    """Verify LiveTick is frozen and immutable."""
    tick_id, canonical_hash = compute_live_tick_id(
        symbol="VOLATILITY_100",
        price=100.0,
        bid=99.9,
        ask=100.1,
        epoch_timestamp=1700000000,
        sequence_number=1,
    )
    tick = LiveTick(
        tick_id=tick_id,
        symbol="VOLATILITY_100",
        price=100.0,
        bid=99.9,
        ask=100.1,
        spread=0.2,
        epoch_timestamp=1700000000,
        arrival_timestamp="2026-08-06T12:00:00Z",
        sequence_number=1,
        connection_id="CONN_01",
        latency_ms=10.5,
        checksum="CHECKSUM",
        canonical_hash=canonical_hash,
    )

    with pytest.raises(ValidationError):
        tick.price = 200.0  # Cannot modify frozen model


def test_live_quote_model():
    """Verify LiveQuote defaults and snapshot properties."""
    quote = LiveQuote(
        symbol="VOLATILITY_10",
        deriv_ws_symbol="R_10",
        live_price=500.0,
        bid=499.9,
        ask=500.1,
        spread=0.2,
        connection_status="CONNECTED",
    )
    assert quote.symbol == "VOLATILITY_10"
    assert quote.live_price == 500.0
    assert quote.spread == 0.2
