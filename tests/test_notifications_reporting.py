"""
Project GOAT v0.8 — Step 7.7 Reporting Engine Dedicated Unit Tests
"""

import json

import pytest

from goat.notifications.core.enums import NotificationChannelType, NotificationType
from goat.notifications.engine import NotificationEngine


def test_notification_reports():
    engine = NotificationEngine()
    engine.register_recipient("Trader Alice", "TRADER", "alice@example.com", [NotificationChannelType.EMAIL])
    ntf, delivs = engine.notify(NotificationType.SIGNAL_GENERATED, "USDJPY Sell", "Sell 1 lot USDJPY", "2026-08-01T00:00:00Z")
    engine.process_queue("2026-08-01T00:00:01Z")

    report = engine.generate_executive_report("2026-08-01T00:00:01Z")

    md = report.to_markdown()
    assert "# GOAT Notification Platform Executive Report" in md

    js_str = report.to_json()
    parsed = json.loads(js_str)
    assert parsed["summary"]["total_notifications"] == 1
    assert parsed["summary"]["delivered_count"] == 1
