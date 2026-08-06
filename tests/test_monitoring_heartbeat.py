"""
Project GOAT v0.8 — Step 7.8 Heartbeat Engine Dedicated Unit Tests
"""

import pytest

from goat.monitoring.core.enums import SubsystemName
from goat.monitoring.heartbeat.engine import HeartbeatEngine


def test_heartbeat_sequence_tracking_and_verification():
    engine = HeartbeatEngine()
    ts = "2026-08-01T00:00:00Z"

    hb1 = engine.generate_heartbeat(SubsystemName.EXECUTION_ENGINE, ts)
    assert hb1.sequence == 1
    assert engine.verify_heartbeat(hb1)

    hb2 = engine.generate_heartbeat(SubsystemName.EXECUTION_ENGINE, ts)
    assert hb2.sequence == 2
    assert engine.verify_heartbeat(hb2)

    latest = engine.get_latest_heartbeat(SubsystemName.EXECUTION_ENGINE)
    assert latest == hb2
    assert len(engine.get_history()) == 2
