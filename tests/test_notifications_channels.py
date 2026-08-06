"""
Project GOAT v0.8 — Step 7.7 Notification Channels Dedicated Unit Tests
"""

import pytest

from goat.notifications.channels.engine import NotificationChannelEngine
from goat.notifications.core.canonical import compute_notification_id, compute_recipient_id
from goat.notifications.core.enums import NotificationChannelType, NotificationType
from goat.notifications.core.models import Notification, NotificationRecipient


def test_all_9_channels_dispatch_planning():
    engine = NotificationChannelEngine()
    ntf_id, ntf_hash = compute_notification_id("SIGNAL_GENERATED", "Test Signal", "2026-08-01T00:00:00Z")
    nrc_id, nrc_hash = compute_recipient_id("Subscriber", "endpoint_ref")

    notification = Notification(
        notification_id=ntf_id,
        notification_type=NotificationType.SIGNAL_GENERATED,
        subject="Test Signal",
        body="Buy 1 lot EURUSD",
        created_at="2026-08-01T00:00:00Z",
        canonical_hash=ntf_hash,
    )

    recipient = NotificationRecipient(
        recipient_id=nrc_id,
        name="Subscriber",
        destination="endpoint_ref",
        channels=list(NotificationChannelType),
        canonical_hash=nrc_hash,
    )

    all_channels = list(NotificationChannelType)
    assert len(all_channels) == 9

    for channel in all_channels:
        payload = engine.plan_dispatch(notification, recipient, channel)
        assert payload["channel_type"] == channel.value
        assert payload["subject"] == "Test Signal"
        assert payload["body"] == "Buy 1 lot EURUSD"


@pytest.mark.parametrize("channel", list(NotificationChannelType))
def test_channel_handler_lookup(channel):
    engine = NotificationChannelEngine()
    handler = engine.get_handler(channel)
    assert handler.channel_type == channel
