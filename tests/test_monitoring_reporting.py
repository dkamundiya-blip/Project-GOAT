"""
Project GOAT v0.8 — Step 7.8 Reporting Engine Dedicated Unit Tests
"""

import json

import pytest

from goat.monitoring.core.enums import HealthLevel, SubsystemName
from goat.monitoring.engine import MonitoringEngine


def test_monitoring_executive_report_generation():
    engine = MonitoringEngine()
    ts = "2026-08-01T00:00:00Z"

    engine.record_heartbeat(SubsystemName.LIVE_MARKET_DATA, ts)
    engine.set_subsystem_health(SubsystemName.LIVE_MARKET_DATA, HealthLevel.HEALTHY, ts)

    report = engine.generate_executive_report(ts)

    md = report.to_markdown()
    assert "# GOAT Operational Control Room Executive Report" in md

    js_str = report.to_json()
    parsed = json.loads(js_str)
    assert parsed["summary"]["total_heartbeats"] == 1
