"""
Project GOAT v0.8 — Operational Monitoring Core Package
"""

from goat.monitoring.core.canonical import (
    compute_alert_id,
    compute_heartbeat_id,
    compute_reliability_id,
    compute_subsystem_health_id,
    compute_summary_id,
    compute_system_health_id,
    compute_telemetry_id,
    compute_watchdog_id,
)
from goat.monitoring.core.enums import (
    AlertLevel,
    DiagnosticCategory,
    HealthLevel,
    MonitoringAuditEventType,
    SubsystemName,
)
from goat.monitoring.core.models import (
    HealthAlert,
    HeartbeatRecord,
    MonitoringSummary,
    ReliabilityAssessment,
    SubsystemHealth,
    SystemHealth,
    TelemetrySnapshot,
    WatchdogStatus,
)

__all__ = [
    # Enums
    "HealthLevel",
    "AlertLevel",
    "SubsystemName",
    "DiagnosticCategory",
    "MonitoringAuditEventType",
    # Canonical SHA-256 Generators
    "compute_system_health_id",
    "compute_subsystem_health_id",
    "compute_heartbeat_id",
    "compute_alert_id",
    "compute_telemetry_id",
    "compute_reliability_id",
    "compute_watchdog_id",
    "compute_summary_id",
    # Domain Models
    "SystemHealth",
    "SubsystemHealth",
    "HeartbeatRecord",
    "HealthAlert",
    "TelemetrySnapshot",
    "ReliabilityAssessment",
    "WatchdogStatus",
    "MonitoringSummary",
]
