"""
Project GOAT v0.8 — Step 7.8 Persistence Dedicated Unit Tests
"""

import tempfile
from pathlib import Path

import pytest

from goat.monitoring.core.enums import HealthLevel, SubsystemName
from goat.monitoring.engine import MonitoringEngine
from goat.monitoring.persistence.repository import SQLiteMonitoringRepository


def test_sqlite_monitoring_persistence_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_monitoring.db"
        engine = MonitoringEngine(db_path=db_path)
        ts = "2026-08-01T00:00:00Z"

        hb = engine.record_heartbeat(SubsystemName.LIVE_MARKET_DATA, ts)
        sh = engine.set_subsystem_health(SubsystemName.LIVE_MARKET_DATA, HealthLevel.HEALTHY, ts)
        sys_health = engine.evaluate_system_health(ts)

        engine.close()

        # Verify database contents directly
        repo = SQLiteMonitoringRepository(db_path)
        db_sys = repo.get_system_health(sys_health.health_id)
        assert db_sys is not None
        assert db_sys.overall_health == HealthLevel.HEALTHY

        db_hbs = repo.get_heartbeats(SubsystemName.LIVE_MARKET_DATA.value)
        assert len(db_hbs) == 1
        assert db_hbs[0].heartbeat_id == hb.heartbeat_id

        repo.close()
