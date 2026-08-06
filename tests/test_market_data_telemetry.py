"""
Project GOAT v1.0 — Test Suite for Latency and Ingestion Telemetry
"""

from goat.market_data.telemetry import LatencyTracker, IngestionMetricsCollector


def test_latency_tracker_statistics():
    """Verify rolling latency tracker calculations."""
    tracker = LatencyTracker(window_size=100)

    tracker.record_latency("VOLATILITY_100", 10.0)
    tracker.record_latency("VOLATILITY_100", 20.0)
    tracker.record_latency("VOLATILITY_100", 30.0)

    snap = tracker.get_symbol_latency("VOLATILITY_100")
    assert snap.current_latency_ms == 30.0
    assert snap.average_latency_ms == 20.0
    assert snap.min_latency_ms == 10.0
    assert snap.max_latency_ms == 30.0
    assert snap.samples_count == 3

    glob_snap = tracker.get_global_latency()
    assert glob_snap.average_latency_ms == 20.0
    assert glob_snap.samples_count == 3


def test_ingestion_metrics_collector():
    """Verify IngestionMetricsCollector snapshot generation."""
    collector = IngestionMetricsCollector()

    collector.record_packet_dropped()
    collector.record_packet_dropped()
    collector.record_reconnect()

    assert collector.dropped_packets == 2
    assert collector.reconnect_count == 1

    snap = collector.snapshot(
        total_ticks=500,
        ticks_per_sec=10.5,
        ws_connected_time=120.0,
        queue_size=0,
        buffer_size=5,
        db_writes_per_sec=10.0,
    )

    assert snap.total_ticks_received == 500
    assert snap.ticks_per_second == 10.5
    assert snap.websocket_uptime_seconds == 120.0
    assert snap.dropped_packets == 2
    assert snap.reconnect_count == 1
