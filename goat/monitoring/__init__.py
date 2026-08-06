"""
Project GOAT v0.8 — Operational Monitoring & Reliability Engine Package

Export all public symbols via __all__. No implementation leakage.
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
from goat.monitoring.diagnostics.engine import DiagnosticsEngine
from goat.monitoring.engine import MonitoringEngine
from goat.monitoring.health.engine import SystemHealthEngine
from goat.monitoring.heartbeat.engine import HeartbeatEngine
from goat.monitoring.persistence.repository import (
    DiagnosticsRepository,
    HeartbeatRepository,
    MonitoringReportRepository,
    SQLiteMonitoringRepository,
    SystemHealthRepository,
    TelemetryRepository,
)
from goat.monitoring.reporting.reports import (
    BaseMonitoringReport,
    DiagnosticsReport,
    HeartbeatReport,
    MonitoringExecutiveReport,
    MonitoringReportEngine,
    ReliabilityReport,
    SystemHealthReport,
    TelemetryReport,
)
from goat.monitoring.telemetry.engine import TelemetryEngine
from goat.monitoring.watchdog.engine import WatchdogEngine

__all__ = [
    # Master Coordinator
    "MonitoringEngine",
    # Subsystem Engines
    "SystemHealthEngine",
    "WatchdogEngine",
    "HeartbeatEngine",
    "TelemetryEngine",
    "DiagnosticsEngine",
    "MonitoringReportEngine",
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
    # Persistence Repositories
    "SQLiteMonitoringRepository",
    "SystemHealthRepository",
    "HeartbeatRepository",
    "TelemetryRepository",
    "DiagnosticsRepository",
    "MonitoringReportRepository",
    # Reports
    "BaseMonitoringReport",
    "SystemHealthReport",
    "HeartbeatReport",
    "TelemetryReport",
    "DiagnosticsReport",
    "ReliabilityReport",
    "MonitoringExecutiveReport",
]
