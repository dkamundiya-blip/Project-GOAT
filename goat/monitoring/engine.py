"""
Project GOAT v0.8 — Monitoring Engine Master Coordinator

Master coordinator implementing canonical Operational Monitoring & Reliability Engine.
Integrates SystemHealthEngine, WatchdogEngine, HeartbeatEngine, TelemetryEngine,
DiagnosticsEngine, SQLiteMonitoringRepository, and MonitoringReportEngine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from goat.monitoring.core.canonical import compute_alert_id, compute_summary_id
from goat.monitoring.core.enums import AlertLevel, HealthLevel, SubsystemName
from goat.monitoring.core.models import (
    HealthAlert,
    HeartbeatRecord,
    MonitoringSummary,
    SubsystemHealth,
    SystemHealth,
    TelemetrySnapshot,
    WatchdogStatus,
)
from goat.monitoring.diagnostics.engine import DiagnosticsEngine
from goat.monitoring.health.engine import SystemHealthEngine
from goat.monitoring.heartbeat.engine import HeartbeatEngine
from goat.monitoring.persistence.repository import SQLiteMonitoringRepository
from goat.monitoring.reporting.reports import MonitoringExecutiveReport, MonitoringReportEngine
from goat.monitoring.telemetry.engine import TelemetryEngine
from goat.monitoring.watchdog.engine import WatchdogEngine


class MonitoringEngine:
    """Master Control Room coordinator for operational monitoring and reliability tracking."""

    def __init__(self, db_path: str | Path | None = None):
        self.health_engine = SystemHealthEngine()
        self.watchdog_engine = WatchdogEngine()
        self.heartbeat_engine = HeartbeatEngine()
        self.telemetry_engine = TelemetryEngine()
        self.diagnostics_engine = DiagnosticsEngine()
        self.report_engine = MonitoringReportEngine()

        self.repository = SQLiteMonitoringRepository(db_path) if db_path else None
        self._alerts: list[HealthAlert] = []

    def close(self) -> None:
        """Close database connection if active."""
        if self.repository:
            self.repository.close()

    def record_heartbeat(
        self,
        subsystem_name: SubsystemName | str,
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> HeartbeatRecord:
        """Record sequential heartbeat pulse and register with watchdog."""
        record = self.heartbeat_engine.generate_heartbeat(subsystem_name, timestamp, metadata)
        self.watchdog_engine.register_heartbeat(record)

        if self.repository:
            self.repository.save_heartbeat(record)

        return record

    def set_subsystem_health(
        self,
        subsystem_name: SubsystemName | str,
        health_level: HealthLevel | str,
        timestamp: str,
        details: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SubsystemHealth:
        """Update health level for a target subsystem."""
        record = self.health_engine.set_subsystem_health(subsystem_name, health_level, timestamp, details, metadata)
        if self.repository:
            self.repository.save_subsystem_health(record)
        return record

    def evaluate_system_health(self, timestamp: str) -> SystemHealth:
        """Evaluate overall aggregated system health."""
        sys_health = self.health_engine.evaluate_system_health(timestamp)
        if self.repository:
            self.repository.save_system_health(sys_health)
        return sys_health

    def audit_watchdog(self, timestamp: str) -> tuple[WatchdogStatus, list[HealthAlert]]:
        """Audit component heartbeat freshness and produce watchdog alerts."""
        status, alerts = self.watchdog_engine.audit_components(timestamp)
        for alert in alerts:
            self._alerts.append(alert)
            if self.repository:
                self.repository.save_alert(alert)
        return status, alerts

    def record_telemetry(
        self,
        timestamp: str,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        disk_usage: float = 0.0,
        database_latency_ms: float = 0.0,
        tick_latency_ms: float = 0.0,
        notification_latency_ms: float = 0.0,
        execution_latency_ms: float = 0.0,
        queue_depth: int = 0,
        processing_time_ms: float = 0.0,
        repository_size_bytes: int = 0,
        replay_throughput_eps: float = 0.0,
        event_throughput_eps: float = 0.0,
    ) -> TelemetrySnapshot:
        """Record abstract operational telemetry metrics."""
        snapshot = self.telemetry_engine.record_snapshot(
            timestamp=timestamp,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            database_latency_ms=database_latency_ms,
            tick_latency_ms=tick_latency_ms,
            notification_latency_ms=notification_latency_ms,
            execution_latency_ms=execution_latency_ms,
            queue_depth=queue_depth,
            processing_time_ms=processing_time_ms,
            repository_size_bytes=repository_size_bytes,
            replay_throughput_eps=replay_throughput_eps,
            event_throughput_eps=event_throughput_eps,
        )

        if self.repository:
            self.repository.save_telemetry(snapshot)

        return snapshot

    def run_diagnostics(self, timestamp: str) -> list[HealthAlert]:
        """Run operational anomaly diagnostics on latest telemetry."""
        latest = self.telemetry_engine.get_latest_snapshot()
        if not latest:
            return []

        alerts = self.diagnostics_engine.analyze_telemetry(latest)
        for alert in alerts:
            self._alerts.append(alert)
            if self.repository:
                self.repository.save_alert(alert)

        return alerts

    def create_alert(
        self,
        subsystem_name: SubsystemName | str,
        alert_level: AlertLevel | str,
        message: str,
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> HealthAlert:
        """Create and log an operational health alert."""
        sub_enum = (
            SubsystemName(str(subsystem_name).upper())
            if not isinstance(subsystem_name, SubsystemName)
            else subsystem_name
        )
        lvl_enum = (
            AlertLevel(str(alert_level).upper())
            if not isinstance(alert_level, AlertLevel)
            else alert_level
        )

        hal_id, hal_hash = compute_alert_id(sub_enum.value, lvl_enum.value, timestamp)
        alert = HealthAlert(
            alert_id=hal_id,
            subsystem_name=sub_enum,
            alert_level=lvl_enum,
            message=message,
            timestamp=timestamp,
            metadata=metadata or {},
            canonical_hash=hal_hash,
        )

        self._alerts.append(alert)
        if self.repository:
            self.repository.save_alert(alert)

        return alert

    def get_summary(self, timestamp: str) -> MonitoringSummary:
        """Compute aggregated MonitoringSummary metrics."""
        total_hb = len(self.heartbeat_engine.get_history())
        total_al = len(self._alerts)

        sys_health = self.health_engine.evaluate_system_health(timestamp)
        active_cnt = sum(1 for v in sys_health.subsystem_health_map.values() if v == HealthLevel.HEALTHY)

        msm_id, msm_hash = compute_summary_id(total_hb, timestamp)

        return MonitoringSummary(
            summary_id=msm_id,
            total_heartbeats=total_hb,
            total_alerts=total_al,
            active_subsystems=active_cnt,
            overall_status=sys_health.overall_health,
            timestamp=timestamp,
            canonical_hash=msm_hash,
        )

    def generate_executive_report(self, timestamp: str) -> MonitoringExecutiveReport:
        """Generate Control Room Executive Report in Markdown and JSON formats."""
        summary = self.get_summary(timestamp)
        sys_health = self.health_engine.evaluate_system_health(timestamp)
        watchdog, _ = self.watchdog_engine.audit_components(timestamp)
        recent_alerts = self._alerts[-20:]

        report = self.report_engine.build_executive_report(summary, sys_health, watchdog, recent_alerts)

        if self.repository:
            self.repository.save_report(f"REP_{summary.summary_id[4:]}", "EXECUTIVE", timestamp, report.to_markdown(), report.get_dict())

        return report

    def get_all_alerts(self) -> list[HealthAlert]:
        return list(self._alerts)
