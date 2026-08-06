"""
Project GOAT v0.8 — Diagnostics Engine

Detects operational anomalies (stale feeds, DB degradation, queue congestion, latency spikes, heartbeat failures)
and produces deterministic diagnostic findings.
"""

from __future__ import annotations

from typing import Any

from goat.monitoring.core.canonical import compute_alert_id
from goat.monitoring.core.enums import AlertLevel, DiagnosticCategory, SubsystemName
from goat.monitoring.core.models import HealthAlert, TelemetrySnapshot, WatchdogStatus


class DiagnosticsEngine:
    """Engine analyzing operational telemetry and watchdog state to produce diagnostic findings."""

    def __init__(
        self,
        max_latency_threshold_ms: float = 1000.0,
        max_queue_depth_threshold: int = 50,
    ):
        self.max_latency_threshold_ms = float(max_latency_threshold_ms)
        self.max_queue_depth_threshold = int(max_queue_depth_threshold)

    def analyze_telemetry(
        self,
        snapshot: TelemetrySnapshot,
    ) -> list[HealthAlert]:
        """Analyze a TelemetrySnapshot and generate alerts for detected anomalies."""
        alerts: list[HealthAlert] = []
        ts = snapshot.timestamp

        if snapshot.database_latency_ms > self.max_latency_threshold_ms:
            hal_id, hal_hash = compute_alert_id(SubsystemName.LIVE_MARKET_DATA.value, AlertLevel.WARNING.value, ts)
            alerts.append(
                HealthAlert(
                    alert_id=hal_id,
                    subsystem_name=SubsystemName.LIVE_MARKET_DATA,
                    alert_level=AlertLevel.WARNING,
                    message=f"High DB latency detected: {snapshot.database_latency_ms} ms",
                    timestamp=ts,
                    canonical_hash=hal_hash,
                )
            )

        if snapshot.queue_depth > self.max_queue_depth_threshold:
            hal_id, hal_hash = compute_alert_id(SubsystemName.NOTIFICATION_PLATFORM.value, AlertLevel.ERROR.value, ts)
            alerts.append(
                HealthAlert(
                    alert_id=hal_id,
                    subsystem_name=SubsystemName.NOTIFICATION_PLATFORM,
                    alert_level=AlertLevel.ERROR,
                    message=f"Queue congestion detected: depth {snapshot.queue_depth}",
                    timestamp=ts,
                    canonical_hash=hal_hash,
                )
            )

        return alerts
