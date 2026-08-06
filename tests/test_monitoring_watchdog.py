"""
Project GOAT v0.8 — Step 7.8 Watchdog Engine Dedicated Unit Tests
"""

import pytest

from goat.monitoring.core.canonical import compute_heartbeat_id
from goat.monitoring.core.enums import SubsystemName
from goat.monitoring.core.models import HeartbeatRecord
from goat.monitoring.watchdog.engine import WatchdogEngine


def test_watchdog_audit_unregistered_components():
    watchdog = WatchdogEngine()
    ts = "2026-08-01T00:00:00Z"

    # Register heartbeat for 1 component only
    hbt_id, hbt_hash = compute_heartbeat_id("LIVE_MARKET_DATA", 1, ts)
    hb = HeartbeatRecord(
        heartbeat_id=hbt_id,
        subsystem_name=SubsystemName.LIVE_MARKET_DATA,
        sequence=1,
        timestamp=ts,
        canonical_hash=hbt_hash,
    )
    watchdog.register_heartbeat(hb)

    status, alerts = watchdog.audit_components(ts)
    assert len(status.active_components) == 1
    assert len(status.dead_components) == 6
    assert len(alerts) == 6
