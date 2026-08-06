"""
Project GOAT v0.8 — Master NotificationEngine Dedicated Unit Tests
"""

import pytest

from goat.notifications.core.enums import NotificationChannelType, NotificationDeliveryStatus, NotificationType
from goat.notifications.engine import NotificationEngine


def test_full_notification_workflow():
    engine = NotificationEngine()
    ts = "2026-08-01T00:00:00Z"

    # 1. Register Recipient
    rec = engine.register_recipient("Admin User", "ADMIN", "webhook_url_101", [NotificationChannelType.WEBHOOK, NotificationChannelType.DASHBOARD])
    assert rec.name == "Admin User"

    # 2. Publish Notification
    ntf, delivs = engine.notify(
        notification_type=NotificationType.RISK_ALERT,
        subject="Drawdown Alert",
        body="Max drawdown threshold exceeded 5%",
        timestamp=ts,
        metadata={"drawdown": 0.052},
    )
    assert ntf.notification_type == NotificationType.RISK_ALERT
    assert len(delivs) == 2

    # 3. Process Queue
    processed = engine.process_queue("2026-08-01T00:00:01Z")
    assert len(processed) == 2
    assert all(p.status == NotificationDeliveryStatus.DELIVERED for p in processed)

    # 4. Summary & Audit
    summary = engine.get_summary("2026-08-01T00:00:02Z")
    assert summary.total_notifications == 1
    assert summary.delivered_count == 2

    audits = engine.get_audit_log()
    assert len(audits) >= 3
