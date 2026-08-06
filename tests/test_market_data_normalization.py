"""
Project GOAT v1.0 — Test Suite for Market Data Normalization
"""

import datetime
from goat.market_data.normalization import (
    TickNormalizer,
    TickNormalizationResult,
    compute_latency_ms,
    epoch_to_iso,
    now_utc_iso,
)


def test_epoch_to_iso():
    """Verify Unix epoch to ISO 8601 UTC string conversion."""
    iso_str = epoch_to_iso(1700000000)
    assert "2023-11-14" in iso_str
    assert "+00:00" in iso_str or "Z" in iso_str


def test_compute_latency_ms():
    """Verify latency calculation between provider epoch and arrival time."""
    epoch = 1700000000
    arrival_dt = datetime.datetime.fromtimestamp(1700000001.250, tz=datetime.timezone.utc)
    lat = compute_latency_ms(epoch, arrival_dt)
    assert lat == 1250.0  # 1.25 seconds = 1250 ms


def test_tick_normalizer_valid_deriv_payload():
    """Verify normalizing standard Deriv WebSocket tick payload."""
    normalizer = TickNormalizer()
    raw = {
        "msg_type": "tick",
        "tick": {
            "symbol": "R_100",
            "quote": 1234.56,
            "pip_size": 2,
            "epoch": 1700000000,
            "bid": 1234.50,
            "ask": 1234.62,
        },
    }

    res: TickNormalizationResult = normalizer.normalize(raw, sequence_number=1)
    assert res.success is True
    assert res.tick is not None
    assert res.tick.symbol == "VOLATILITY_100"
    assert res.tick.price == 1234.56
    assert res.tick.bid == 1234.50
    assert res.tick.ask == 1234.62
    assert res.tick.spread == 0.12
    assert res.tick.tick_id.startswith("LTK_")


def test_tick_normalizer_quote_only_payload():
    """Verify normalizing payload when ask/bid are missing (infer from quote + pip_size)."""
    normalizer = TickNormalizer()
    raw = {
        "tick": {
            "symbol": "R_10",
            "quote": 500.0,
            "pip_size": 2,
            "epoch": 1700000000,
        }
    }
    res = normalizer.normalize(raw, sequence_number=2)
    assert res.success is True
    assert res.tick is not None
    assert res.tick.symbol == "VOLATILITY_10"
    assert res.tick.price == 500.0
    assert res.tick.bid > 0
    assert res.tick.ask > res.tick.bid


def test_tick_normalizer_malformed_payload():
    """Verify rejection of invalid/malformed payloads."""
    normalizer = TickNormalizer()

    # Empty payload
    res1 = normalizer.normalize({})
    assert res1.success is False
    assert "REJECTED" in res1.rejection_reason

    # Missing symbol
    res2 = normalizer.normalize({"quote": 100.0, "epoch": 1700000000})
    assert res2.success is False
    assert "REJECTED_MISSING_SYMBOL" in res2.rejection_reason

    # Negative price
    res3 = normalizer.normalize({"symbol": "R_100", "quote": -5.0, "epoch": 1700000000})
    assert res3.success is False
    assert "REJECTED_NON_POSITIVE_PRICE" in res3.rejection_reason
