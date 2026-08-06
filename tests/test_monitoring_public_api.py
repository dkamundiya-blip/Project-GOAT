"""
Project GOAT v0.8 — Step 7.8 Public API Dedicated Unit Tests
"""

import pytest

import goat.monitoring as monitoring_pkg


def test_public_api_exports():
    expected_exports = [
        "MonitoringEngine",
        "SystemHealthEngine",
        "WatchdogEngine",
        "HeartbeatEngine",
        "TelemetryEngine",
        "DiagnosticsEngine",
        "MonitoringReportEngine",
        "HealthLevel",
        "AlertLevel",
        "SubsystemName",
        "DiagnosticCategory",
        "MonitoringAuditEventType",
        "compute_system_health_id",
        "compute_subsystem_health_id",
        "compute_heartbeat_id",
        "compute_alert_id",
        "compute_telemetry_id",
        "compute_reliability_id",
        "compute_watchdog_id",
        "compute_summary_id",
        "SystemHealth",
        "SubsystemHealth",
        "HeartbeatRecord",
        "HealthAlert",
        "TelemetrySnapshot",
        "ReliabilityAssessment",
        "WatchdogStatus",
        "MonitoringSummary",
        "SQLiteMonitoringRepository",
        "SystemHealthRepository",
        "HeartbeatRepository",
        "TelemetryRepository",
        "DiagnosticsRepository",
        "MonitoringReportRepository",
        "BaseMonitoringReport",
        "SystemHealthReport",
        "HeartbeatReport",
        "TelemetryReport",
        "DiagnosticsReport",
        "ReliabilityReport",
        "MonitoringExecutiveReport",
    ]

    for item in expected_exports:
        assert hasattr(monitoring_pkg, item)
    assert set(monitoring_pkg.__all__) == set(expected_exports)
