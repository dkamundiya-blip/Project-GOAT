"""
Project GOAT v0.8 — Step 7.8 Telemetry Engine Dedicated Unit Tests
"""

import pytest

from goat.monitoring.telemetry.engine import TelemetryEngine


def test_telemetry_snapshot_recording():
    engine = TelemetryEngine()
    ts = "2026-08-01T00:00:00Z"

    snap = engine.record_snapshot(
        timestamp=ts,
        cpu_usage=25.5,
        memory_usage=60.0,
        disk_usage=40.0,
        database_latency_ms=4.2,
        execution_latency_ms=12.1,
    )

    assert snap.snapshot_id.startswith("TEL_")
    assert snap.cpu_usage == 25.5
    assert engine.get_latest_snapshot() == snap
