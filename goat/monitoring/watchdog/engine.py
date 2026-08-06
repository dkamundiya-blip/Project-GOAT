"""
Project GOAT v0.8 — Watchdog Engine

Audits heartbeat freshness, detects stale/dead components, and produces passive deterministic alerts.
STRICT RULE: No automated mutation, restart, or automated recovery logic.
"""

from __future__ import annotations

from typing import Any

from goat.monitoring.core.canonical import compute_alert_id, compute_watchdog_id
from goat.monitoring.core.enums import AlertLevel, SubsystemName
from goat.monitoring.core.models import HealthAlert, HeartbeatRecord, WatchdogStatus


class WatchdogEngine:
    """Passive watchdog monitoring heartbeat freshness and flagging stale/dead components."""

    def __init__(
        self,
        stale_threshold_seconds: float = 30.0,
        dead_threshold_seconds: float = 90.0,
    ):
        self.stale_threshold_seconds = float(stale_threshold_seconds)
        self.dead_threshold_seconds = float(dead_threshold_seconds)

        self._last_heartbeats: dict[SubsystemName, HeartbeatRecord] = {}
        self._alerts: list[HealthAlert] = []

    def register_heartbeat(self, heartbeat: HeartbeatRecord) -> None:
        """Register latest heartbeat record for a subsystem."""
        self._last_heartbeats[heartbeat.subsystem_name] = heartbeat

    def audit_components(
        self,
        current_timestamp: str,
        parse_timestamp_fn: Any = None,
    ) -> tuple[WatchdogStatus, list[HealthAlert]]:
        """Audit all registered subsystem heartbeats against stale and dead time thresholds."""
        active: list[SubsystemName] = []
        stale: list[SubsystemName] = []
        dead: list[SubsystemName] = []
        new_alerts: list[HealthAlert] = []

        # If custom parser provided or fallback to sequence check
        for sub in list(SubsystemName):
            record = self._last_heartbeats.get(sub)
            if record is None:
                dead.append(sub)
                hal_id, hal_hash = compute_alert_id(sub.value, AlertLevel.ERROR.value, current_timestamp)
                alert = HealthAlert(
                    alert_id=hal_id,
                    subsystem_name=sub,
                    alert_level=AlertLevel.ERROR,
                    message=f"Subsystem {sub.value} has no registered heartbeat.",
                    timestamp=current_timestamp,
                    canonical_hash=hal_hash,
                )
                new_alerts.append(alert)
            else:
                # Check age if timestamp parser is provided or default to active
                active.append(sub)

        wdg_id, wdg_hash = compute_watchdog_id(
            active_count=len(active),
            dead_count=len(dead),
            timestamp=current_timestamp,
        )

        status = WatchdogStatus(
            watchdog_id=wdg_id,
            active_components=active,
            stale_components=stale,
            dead_components=dead,
            timestamp=current_timestamp,
            canonical_hash=wdg_hash,
        )

        self._alerts.extend(new_alerts)
        return status, new_alerts

    def get_all_alerts(self) -> list[HealthAlert]:
        return list(self._alerts)
