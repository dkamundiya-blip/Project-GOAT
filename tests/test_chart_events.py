"""
Project GOAT v1.0 — Test Suite for Chart Event Bus Contracts (Step 1.6)
"""

import pytest
from goat.market_data.telemetry.metrics import IngestionMetricsCollector


def test_chart_event_telemetry_recording():
    """Verify operational telemetry recording for chart events."""
    collector = IngestionMetricsCollector()
    collector.record_packet_dropped()

    snap = collector.snapshot(
        total_ticks=100,
        ticks_per_sec=15.5,
        ws_connected_time=120.0,
        queue_size=0,
        buffer_size=10,
        db_writes_per_sec=5.0,
    )
    assert snap.total_ticks_received == 100
    assert snap.ticks_per_second == 15.5
    assert snap.dropped_packets == 1
