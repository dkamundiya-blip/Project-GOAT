"""
Project GOAT v1.0 — Test Suite for SymbolManager (Step 1.6)
"""

import pytest
from goat.market_data.models.symbol import SUPPORTED_SYMBOLS, get_symbol_config


def test_supported_symbols_catalogue_completeness():
    """Verify all 8 Deriv synthetic index instruments in supported registry."""
    assert len(SUPPORTED_SYMBOLS) == 8
    expected_ids = [
        "VOLATILITY_10",
        "VOLATILITY_25",
        "VOLATILITY_50",
        "VOLATILITY_75",
        "VOLATILITY_100",
        "BOOM_1000",
        "CRASH_1000",
        "STEP_INDEX",
    ]
    for sym_id in expected_ids:
        config = get_symbol_config(sym_id)
        assert config is not None
        assert config.symbol_id == sym_id
        assert config.pip_size >= 2
