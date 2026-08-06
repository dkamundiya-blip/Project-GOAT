"""
Project GOAT v0.8 — System Health Engine

Monitors health status across the 7 production subsystems and computes overall SystemHealth.
Assigns deterministic health levels: HEALTHY, WARNING, DEGRADED, CRITICAL, OFFLINE.
"""

from __future__ import annotations

from typing import Any

from goat.monitoring.core.canonical import compute_subsystem_health_id, compute_system_health_id
from goat.monitoring.core.enums import HealthLevel, SubsystemName
from goat.monitoring.core.models import SubsystemHealth, SystemHealth

ALL_SUBSYSTEMS = list(SubsystemName)


class SystemHealthEngine:
    """Engine aggregating individual subsystem health reports and evaluating overall SystemHealth."""

    def __init__(self):
        self._subsystem_health: dict[SubsystemName, SubsystemHealth] = {}

    def set_subsystem_health(
        self,
        subsystem_name: SubsystemName | str,
        health_level: HealthLevel | str,
        timestamp: str,
        details: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SubsystemHealth:
        """Set health level for a specific subsystem."""
        sub_enum = (
            SubsystemName(str(subsystem_name).upper())
            if not isinstance(subsystem_name, SubsystemName)
            else subsystem_name
        )
        level_enum = (
            HealthLevel(str(health_level).upper())
            if not isinstance(health_level, HealthLevel)
            else health_level
        )

        sbh_id, sbh_hash = compute_subsystem_health_id(
            subsystem_name=sub_enum.value,
            health_level=level_enum.value,
            timestamp=timestamp,
        )

        health_record = SubsystemHealth(
            subsystem_health_id=sbh_id,
            subsystem_name=sub_enum,
            health_level=level_enum,
            details=details,
            timestamp=timestamp,
            metadata=metadata or {},
            canonical_hash=sbh_hash,
        )

        self._subsystem_health[sub_enum] = health_record
        return health_record

    def get_subsystem_health(self, subsystem_name: SubsystemName | str) -> SubsystemHealth | None:
        sub_enum = (
            SubsystemName(str(subsystem_name).upper())
            if not isinstance(subsystem_name, SubsystemName)
            else subsystem_name
        )
        return self._subsystem_health.get(sub_enum)

    def evaluate_system_health(self, timestamp: str) -> SystemHealth:
        """Aggregate all subsystem health levels to evaluate overall system health."""
        sub_map: dict[str, HealthLevel] = {}

        # Default unconfigured subsystems to HEALTHY or OFFLINE
        for sub in ALL_SUBSYSTEMS:
            record = self._subsystem_health.get(sub)
            sub_map[sub.value] = record.health_level if record else HealthLevel.HEALTHY

        # Determine overall level based on priority
        levels = list(sub_map.values())
        if HealthLevel.CRITICAL in levels or HealthLevel.OFFLINE in levels:
            overall = HealthLevel.CRITICAL
        elif HealthLevel.DEGRADED in levels:
            overall = HealthLevel.DEGRADED
        elif HealthLevel.WARNING in levels:
            overall = HealthLevel.WARNING
        else:
            overall = HealthLevel.HEALTHY

        syh_id, syh_hash = compute_system_health_id(
            overall_health=overall.value,
            timestamp=timestamp,
        )

        return SystemHealth(
            health_id=syh_id,
            overall_health=overall,
            subsystem_health_map=sub_map,
            timestamp=timestamp,
            canonical_hash=syh_hash,
        )

    def get_all_subsystem_health(self) -> list[SubsystemHealth]:
        return list(self._subsystem_health.values())
