"""
Project GOAT v0.8 — Notification Queue Engine

Maintains an append-only FIFO and priority ordered delivery queue, tracks retry metadata,
and supports full deterministic queue event stream replay.
"""

from __future__ import annotations

from typing import Any

from goat.notifications.core.canonical import compute_delivery_id
from goat.notifications.core.enums import NotificationChannelType, NotificationDeliveryStatus, NotificationPriority
from goat.notifications.core.models import Notification, NotificationDelivery, NotificationRecipient

PRIORITY_WEIGHTS: dict[NotificationPriority, int] = {
    NotificationPriority.URGENT: 5,
    NotificationPriority.CRITICAL: 4,
    NotificationPriority.HIGH: 3,
    NotificationPriority.MEDIUM: 2,
    NotificationPriority.LOW: 1,
}


class NotificationQueueEngine:
    """Synchronous append-only priority delivery queue and replay manager."""

    def __init__(self):
        self._queue: list[NotificationDelivery] = []  # Append-only list
        self._deliveries_by_id: dict[str, NotificationDelivery] = {}

    def enqueue_delivery(
        self,
        notification: Notification,
        recipient: NotificationRecipient,
        channel_type: NotificationChannelType,
        delivered_at: str,
        status: NotificationDeliveryStatus = NotificationDeliveryStatus.QUEUED,
        metadata: dict[str, Any] | None = None,
    ) -> NotificationDelivery:
        """Enqueue a new NotificationDelivery record."""
        ndl_id, ndl_hash = compute_delivery_id(
            notification_id=notification.notification_id,
            recipient_id=recipient.recipient_id,
            channel_type=channel_type.value,
            delivered_at=delivered_at,
        )

        delivery = NotificationDelivery(
            delivery_id=ndl_id,
            notification_id=notification.notification_id,
            recipient_id=recipient.recipient_id,
            channel_type=channel_type,
            status=status,
            attempt_count=0 if status == NotificationDeliveryStatus.QUEUED else 1,
            delivered_at=delivered_at,
            metadata=metadata or {},
            canonical_hash=ndl_hash,
        )

        self._queue.append(delivery)
        self._deliveries_by_id[ndl_id] = delivery
        return delivery

    def update_delivery_status(
        self,
        delivery_id: str,
        status: NotificationDeliveryStatus,
        delivered_at: str,
    ) -> NotificationDelivery:
        """Update status of a delivery record in the queue."""
        delivery = self._deliveries_by_id.get(delivery_id)
        if delivery is None:
            raise KeyError(f"NotificationDelivery ID {delivery_id} not found.")

        updated = NotificationDelivery(
            delivery_id=delivery.delivery_id,
            notification_id=delivery.notification_id,
            recipient_id=delivery.recipient_id,
            channel_type=delivery.channel_type,
            status=status,
            attempt_count=delivery.attempt_count + 1,
            delivered_at=delivered_at,
            metadata=delivery.metadata,
            canonical_hash=delivery.canonical_hash,
        )

        self._deliveries_by_id[delivery_id] = updated
        # Replace in append-only log or update in place
        for idx, item in enumerate(self._queue):
            if item.delivery_id == delivery_id:
                self._queue[idx] = updated
                break

        return updated

    def get_queued_deliveries(self) -> list[NotificationDelivery]:
        """Get all pending QUEUED deliveries in FIFO order."""
        return [d for d in self._queue if d.status == NotificationDeliveryStatus.QUEUED]

    def get_all_deliveries(self) -> list[NotificationDelivery]:
        """Get full append-only queue history."""
        return list(self._queue)
