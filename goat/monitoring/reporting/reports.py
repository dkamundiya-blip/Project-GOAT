"""
Project GOAT v0.8 — Operational Monitoring Reporting Engine

Generates canonical Markdown and JSON reports for:
- SystemHealthReport
- HeartbeatReport
- TelemetryReport
- DiagnosticsReport
- ReliabilityReport
- MonitoringExecutiveReport

Supports to_markdown() and to_json() formatting.
"""

from __future__ import annotations

import json
from typing import Any

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


class BaseMonitoringReport:
    """Base report class providing to_markdown() and to_json() contract interface."""

    def __init__(self, title: str, markdown_content: str, json_payload: dict[str, Any]):
        self.title = title
        self._markdown = markdown_content
        self._json_payload = json_payload

    def to_markdown(self) -> str:
        return self._markdown

    def to_json(self) -> str:
        return json.dumps(self._json_payload, indent=2, sort_keys=True)

    def get_dict(self) -> dict[str, Any]:
        return dict(self._json_payload)


class SystemHealthReport(BaseMonitoringReport):
    """Report detailing overall system and subsystem health status."""
    pass


class HeartbeatReport(BaseMonitoringReport):
    """Report detailing subsystem heartbeat freshness and sequence logs."""
    pass


class TelemetryReport(BaseMonitoringReport):
    """Report detailing abstract performance latency and throughput metrics."""
    pass


class DiagnosticsReport(BaseMonitoringReport):
    """Report detailing operational anomaly diagnostics and alerts."""
    pass


class ReliabilityReport(BaseMonitoringReport):
    """Report detailing aggregated uptime percentages and reliability scores."""
    pass


class MonitoringExecutiveReport(BaseMonitoringReport):
    """Executive Control Room report combining system health, watchdog state, telemetry, and alerts."""
    pass


class MonitoringReportEngine:
    """Reporting engine generating structured Markdown and JSON monitoring reports."""

    def build_system_health_report(self, system_health: SystemHealth) -> SystemHealthReport:
        json_data = system_health.model_dump()
        sub_rows = []
        for sub, level in sorted(system_health.subsystem_health_map.items()):
            sub_rows.append(f"| `{sub}` | `{level.value if hasattr(level, 'value') else level}` |")
        sub_table = "\n".join(sub_rows) if sub_rows else "| None | - |"

        markdown = f"""# GOAT System Health Report

- **System Health ID**: `{system_health.health_id}`
- **Overall Health**: `{system_health.overall_health.value}`
- **Timestamp**: {system_health.timestamp}

| Subsystem Name | Health Level |
|---|---|
{sub_table}

---
*Canonical Hash*: `{system_health.canonical_hash}`
"""
        return SystemHealthReport("System Health Report", markdown, json_data)

    def build_heartbeat_report(self, heartbeats: list[HeartbeatRecord]) -> HeartbeatReport:
        json_data = {
            "heartbeats_count": len(heartbeats),
            "heartbeats": [h.model_dump() for h in heartbeats],
        }

        rows = []
        for h in heartbeats:
            rows.append(
                f"| `{h.heartbeat_id[:12]}` | `{h.subsystem_name.value}` | {h.sequence} | {h.timestamp} |"
            )
        table = "\n".join(rows) if rows else "| None | - | - | - |"

        markdown = f"""# GOAT Subsystem Heartbeat Report

- **Total Heartbeats Recorded**: {len(heartbeats)}

| Heartbeat ID | Subsystem Name | Sequence | Timestamp |
|---|---|---|---|
{table}
"""
        return HeartbeatReport("Subsystem Heartbeat Report", markdown, json_data)

    def build_telemetry_report(self, snapshot: TelemetrySnapshot) -> TelemetryReport:
        json_data = snapshot.model_dump()
        markdown = f"""# GOAT Telemetry Snapshot Report

- **Snapshot ID**: `{snapshot.snapshot_id}`
- **Timestamp**: {snapshot.timestamp}

## Resource Usage
- **CPU Usage**: {snapshot.cpu_usage:.2f}%
- **Memory Usage**: {snapshot.memory_usage:.2f}%
- **Disk Usage**: {snapshot.disk_usage:.2f}%

## Subsystem Latencies
- **Database Latency**: {snapshot.database_latency_ms:.2f} ms
- **Tick Latency**: {snapshot.tick_latency_ms:.2f} ms
- **Notification Latency**: {snapshot.notification_latency_ms:.2f} ms
- **Execution Latency**: {snapshot.execution_latency_ms:.2f} ms

## Throughput & Queues
- **Queue Depth**: {snapshot.queue_depth}
- **Processing Time**: {snapshot.processing_time_ms:.2f} ms
- **Replay Throughput**: {snapshot.replay_throughput_eps:.2f} eps
- **Event Throughput**: {snapshot.event_throughput_eps:.2f} eps
"""
        return TelemetryReport("Telemetry Snapshot Report", markdown, json_data)

    def build_diagnostics_report(self, alerts: list[HealthAlert]) -> DiagnosticsReport:
        json_data = {
            "alerts_count": len(alerts),
            "alerts": [a.model_dump() for a in alerts],
        }

        rows = []
        for a in alerts:
            rows.append(
                f"| `{a.alert_id[:12]}` | `{a.subsystem_name.value}` | `{a.alert_level.value}` | {a.message} | {a.timestamp} |"
            )
        table = "\n".join(rows) if rows else "| None | - | - | - | - |"

        markdown = f"""# GOAT Operational Diagnostics Report

- **Total Health Alerts**: {len(alerts)}

| Alert ID | Subsystem Name | Alert Level | Message | Timestamp |
|---|---|---|---|---|
{table}
"""
        return DiagnosticsReport("Operational Diagnostics Report", markdown, json_data)

    def build_executive_report(
        self,
        summary: MonitoringSummary,
        system_health: SystemHealth,
        watchdog: WatchdogStatus,
        recent_alerts: list[HealthAlert],
    ) -> MonitoringExecutiveReport:
        json_data = {
            "summary": summary.model_dump(),
            "system_health": system_health.model_dump(),
            "watchdog": watchdog.model_dump(),
            "recent_alerts_count": len(recent_alerts),
            "recent_alerts": [a.model_dump() for a in recent_alerts],
        }

        markdown = f"""# GOAT Operational Control Room Executive Report

- **Timestamp**: {summary.timestamp}
- **Summary ID**: `{summary.summary_id}`

## Overall System Status
- **System Health**: `{system_health.overall_health.value}`
- **Active Subsystems**: {summary.active_subsystems} / 7
- **Total Heartbeats**: {summary.total_heartbeats}
- **Total Alerts Generated**: {summary.total_alerts}

## Watchdog Component Status
- **Active**: {len(watchdog.active_components)}
- **Stale**: {len(watchdog.stale_components)}
- **Dead**: {len(watchdog.dead_components)}
"""
        return MonitoringExecutiveReport("Operational Control Room Executive Report", markdown, json_data)
