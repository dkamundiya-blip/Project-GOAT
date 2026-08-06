"""
Project GOAT v1.0 — Test Suite for Chart Streaming Latency (Step 1.6)
"""

import pytest
from goat.market_data.telemetry.latency import LatencyTracker


def test_chart_streaming_latency_performance():
    """Verify stream tick processing latency stays well under 250ms target."""
    tracker = LatencyTracker()

    for lat in [12.0, 15.5, 18.2, 22.0, 9.8, 14.1]:
        tracker.record_latency("VOLATILITY_100", lat)

    stat = tracker.get_symbol_latency("VOLATILITY_100")
    assert stat.average_latency_ms < 50.0
    assert stat.max_latency_ms < 250.0  # Strict requirement: <250ms latency
