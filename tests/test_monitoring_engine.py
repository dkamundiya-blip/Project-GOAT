"""
Project GOAT v0.8 — Master MonitoringEngine Dedicated Unit Tests
"""

import pytest

from goat.monitoring.core.enums import AlertLevel, HealthLevel, SubsystemName
from goat.monitoring.engine import MonitoringEngine


def test_monitoring_engine_master_workflow():
    engine = MonitoringEngine()
    ts = "2026-08-01T00:00:00Z"

    # Record heartbeats
    for sub in list(SubsystemName):
        engine.record_heartbeat(sub, ts)
        engine.set_subsystem_health(sub, HealthLevel.HEALTHY, ts)

    # Evaluate system health
    sys_health = engine.evaluate_system_health(ts)
    assert sys_health.overall_health == HealthLevel.HEALTHY

    # Telemetry & Diagnostics
    snap = engine.record_telemetry(ts, cpu_usage=15.0, database_latency_ms=2.5)
    assert snap.snapshot_id.startswith("TEL_")

    # Summary
    summary = engine.get_summary(ts)
    assert summary.total_heartbeats == 7
    assert summary.active_subsystems == 7
