"""
Project GOAT v1.0 — Test Suite for TradingView Adapter (Step 1.6)
"""

import pytest
from goat.market_data.normalization.tick_normalizer import TickNormalizer


def test_tradingview_adapter_tick_to_bar_transformation():
    """Verify raw WebSocket tick data normalization for TradingView adapter consumption."""
    normalizer = TickNormalizer()
    payload = {
        "msg_type": "tick",
        "tick": {
            "symbol": "R_100",
            "quote": 1254.50,
            "pip_size": 2,
            "epoch": 1700000000,
            "bid": 1254.40,
            "ask": 1254.60,
        },
    }

    res = normalizer.normalize(raw_payload=payload, sequence_number=1)
    assert res.success is True
    assert res.tick is not None
    assert res.tick.price == 1254.50
    assert res.tick.symbol == "VOLATILITY_100"
