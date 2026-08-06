"""
Project GOAT v0.8 — Step 7.7 Persistence Dedicated Unit Tests
"""

import tempfile
from pathlib import Path

import pytest

from goat.notifications.core.enums import NotificationChannelType, NotificationDeliveryStatus, NotificationType
from goat.notifications.engine import NotificationEngine
from goat.notifications.persistence.repository import SQLiteNotificationRepository


def test_sqlite_notifications_persistence_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_notifications.db"
        engine = NotificationEngine(db_path=db_path)

        rec1 = engine.register_recipient("Trader Bob", "TRADER", "tg_9999", [NotificationChannelType.TELEGRAM])
        ntf, delivs = engine.notify(NotificationType.SIGNAL_GENERATED, "GBPUSD Buy", "Buy 0.5 GBPUSD", "2026-08-01T00:00:00Z")

        engine.process_queue("2026-08-01T00:00:01Z")

        # Close engine to release connection lock on Windows
        engine.close()

        # Verify DB records directly
        repo = SQLiteNotificationRepository(db_path)
        db_n = repo.get_notification(ntf.notification_id)
        assert db_n is not None
        assert db_n.subject == "GBPUSD Buy"

        db_rec = repo.get_recipient(rec1.recipient_id)
        assert db_rec is not None
        assert db_rec.name == "Trader Bob"

        db_delivs = repo.get_deliveries(ntf.notification_id)
        assert len(db_delivs) == 1
        assert db_delivs[0].status == NotificationDeliveryStatus.DELIVERED

        db_audits = repo.get_audits(ntf.notification_id)
        assert len(db_audits) >= 2

        repo.close()
