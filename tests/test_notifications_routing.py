"""
Project GOAT v0.8 — Step 7.7 Notification Routing Engine Dedicated Unit Tests
"""

import pytest

from goat.notifications.core.canonical import compute_notification_id, compute_recipient_id
from goat.notifications.core.enums import NotificationChannelType, NotificationPriority, NotificationType
from goat.notifications.core.models import Notification, NotificationRecipient
from goat.notifications.routing.engine import NotificationRoutingEngine


def test_routing_engine_recipient_registration():
    routing = NotificationRoutingEngine()
    nrc_id, nrc_hash = compute_recipient_id("Trader Joe", "tg_12345")
    r1 = NotificationRecipient(
        recipient_id=nrc_id,
        name="Trader Joe",
        role="TRADER",
        destination="tg_12345",
        channels=[NotificationChannelType.TELEGRAM, NotificationChannelType.DASHBOARD],
        canonical_hash=nrc_hash,
    )
    routing.register_recipient(r1)
    recipients = routing.get_all_recipients()
    assert len(recipients) == 1
    assert recipients[0].name == "Trader Joe"


def test_routing_engine_priority_resolution():
    routing = NotificationRoutingEngine()
    assert routing.resolve_priority(NotificationType.RISK_ALERT) == NotificationPriority.URGENT
    assert routing.resolve_priority(NotificationType.EXECUTION_FAILED) == NotificationPriority.CRITICAL
    assert routing.resolve_priority(NotificationType.TRADE_OPENED) == NotificationPriority.HIGH
    assert routing.resolve_priority(NotificationType.HEALTH_NOTIFICATION) == NotificationPriority.LOW


def test_routing_engine_duplicate_suppression():
    routing = NotificationRoutingEngine()
    ntype = NotificationType.SIGNAL_GENERATED
    subject = "EURUSD Buy Signal"
    body = "Buy 1.0 lot EURUSD @ 1.0850"
    ts = "2026-08-01T00:00:00Z"

    assert not routing.is_duplicate(ntype, subject, body)
    routing.record_fingerprint(ntype, subject, body, ts)
    assert routing.is_duplicate(ntype, subject, body)


@pytest.mark.parametrize("ntype", list(NotificationType))
def test_routing_priority_matrix(ntype):
    routing = NotificationRoutingEngine()
    prio = routing.resolve_priority(ntype)
    assert isinstance(prio, NotificationPriority)
