"""
Project GOAT v1.0 — Test Suite for TimeframeManager (Step 1.6)
"""

import pytest
from goat.market_data.candles.builder import floor_timestamp_to_interval


def test_timeframe_interval_flooring():
    """Verify timestamp interval flooring logic across timeframes."""
    ts = 1786019696  # 2026-08-06 epoch

    open_iso, close_iso = floor_timestamp_to_interval(ts, "1M")
    assert open_iso is not None
    assert close_iso is not None
    assert "T" in open_iso
    assert "T" in close_iso

    open_m5, close_m5 = floor_timestamp_to_interval(ts, "5M")
    assert open_m5 is not None
    assert close_m5 is not None
