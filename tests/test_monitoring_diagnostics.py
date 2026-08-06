"""
Project GOAT v0.8 — Step 7.8 Diagnostics Engine Dedicated Unit Tests
"""

import pytest

from goat.monitoring.core.enums import AlertLevel
from goat.monitoring.diagnostics.engine import DiagnosticsEngine
from goat.monitoring.telemetry.engine import TelemetryEngine


def test_diagnostics_anomaly_detection():
    telemetry_eng = TelemetryEngine()
    diag_eng = DiagnosticsEngine(max_latency_threshold_ms=10.0, max_queue_depth_threshold=5)
    ts = "2026-08-01T00:00:00Z"

    snapshot = telemetry_eng.record_snapshot(
        timestamp=ts,
        database_latency_ms=25.0,  # exceeds 10.0 threshold
        queue_depth=10,  # exceeds 5 threshold
    )

    alerts = diag_eng.analyze_telemetry(snapshot)
    assert len(alerts) == 2
    assert any(a.alert_level == AlertLevel.WARNING for a in alerts)
    assert any(a.alert_level == AlertLevel.ERROR for a in alerts)
