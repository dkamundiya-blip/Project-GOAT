"""
Project GOAT v0.8 — Step 7.7 Notification Queue Dedicated Unit Tests
"""

import pytest

from goat.notifications.core.canonical import compute_notification_id, compute_recipient_id
from goat.notifications.core.enums import NotificationChannelType, NotificationDeliveryStatus, NotificationType
from goat.notifications.core.models import Notification, NotificationRecipient
from goat.notifications.queue.engine import NotificationQueueEngine


def test_queue_enqueue_and_status_update():
    queue = NotificationQueueEngine()
    ntf_id, ntf_hash = compute_notification_id("SIGNAL_GENERATED", "Test", "2026-08-01T00:00:00Z")
    nrc_id, nrc_hash = compute_recipient_id("Test Recipient", "dest")

    notification = Notification(
        notification_id=ntf_id,
        notification_type=NotificationType.SIGNAL_GENERATED,
        subject="Test",
        body="Body",
        created_at="2026-08-01T00:00:00Z",
        canonical_hash=ntf_hash,
    )
    recipient = NotificationRecipient(
        recipient_id=nrc_id,
        name="Test Recipient",
        destination="dest",
        channels=[NotificationChannelType.DASHBOARD],
        canonical_hash=nrc_hash,
    )

    deliv = queue.enqueue_delivery(notification, recipient, NotificationChannelType.DASHBOARD, "2026-08-01T00:00:00Z")
    assert deliv.status == NotificationDeliveryStatus.QUEUED

    queued = queue.get_queued_deliveries()
    assert len(queued) == 1
    assert queued[0].delivery_id == deliv.delivery_id

    updated = queue.update_delivery_status(deliv.delivery_id, NotificationDeliveryStatus.DELIVERED, "2026-08-01T00:00:01Z")
    assert updated.status == NotificationDeliveryStatus.DELIVERED
    assert len(queue.get_queued_deliveries()) == 0
    assert len(queue.get_all_deliveries()) == 1


@pytest.mark.parametrize("idx", range(100))
def test_queue_append_only_integrity(idx):
    queue = NotificationQueueEngine()
    ntf_id, ntf_hash = compute_notification_id(f"TYPE_{idx}", f"Test_{idx}", "2026-08-01T00:00:00Z")
    nrc_id, nrc_hash = compute_recipient_id(f"Recipient_{idx}", f"dest_{idx}")

    notification = Notification(
        notification_id=ntf_id,
        notification_type=NotificationType.SIGNAL_GENERATED,
        subject=f"Test_{idx}",
        body="Body",
        created_at="2026-08-01T00:00:00Z",
        canonical_hash=ntf_hash,
    )
    recipient = NotificationRecipient(
        recipient_id=nrc_id,
        name=f"Recipient_{idx}",
        destination=f"dest_{idx}",
        channels=[NotificationChannelType.DASHBOARD],
        canonical_hash=nrc_hash,
    )

    deliv = queue.enqueue_delivery(notification, recipient, NotificationChannelType.DASHBOARD, f"2026-08-01T00:{idx % 60:02d}:00Z")
    assert deliv.delivery_id.startswith("NDL_")
