"""
Project GOAT v0.8 — Step 7.8 System Health Engine Dedicated Unit Tests
"""

import pytest

from goat.monitoring.core.enums import HealthLevel, SubsystemName
from goat.monitoring.health.engine import SystemHealthEngine


def test_subsystem_health_setting_and_aggregation():
    engine = SystemHealthEngine()
    ts = "2026-08-01T00:00:00Z"

    engine.set_subsystem_health(SubsystemName.LIVE_MARKET_DATA, HealthLevel.HEALTHY, ts)
    engine.set_subsystem_health(SubsystemName.EXECUTION_ENGINE, HealthLevel.HEALTHY, ts)

    sys_health = engine.evaluate_system_health(ts)
    assert sys_health.overall_health == HealthLevel.HEALTHY

    engine.set_subsystem_health(SubsystemName.BROKER_ADAPTER, HealthLevel.CRITICAL, ts)
    sys_health_critical = engine.evaluate_system_health(ts)
    assert sys_health_critical.overall_health == HealthLevel.CRITICAL


@pytest.mark.parametrize("level", list(HealthLevel))
def test_all_health_levels(level):
    engine = SystemHealthEngine()
    rec = engine.set_subsystem_health(SubsystemName.PORTFOLIO_ENGINE, level, "2026-08-01T00:00:00Z")
    assert rec.health_level == level
