"""
Project GOAT v0.8 — Notification Platform Core Exports
"""

from goat.notifications.core.canonical import (
    compute_audit_id,
    compute_channel_id,
    compute_delivery_id,
    compute_notification_id,
    compute_payload_id,
    compute_recipient_id,
    compute_summary_id,
)
from goat.notifications.core.enums import (
    NotificationAuditEventType,
    NotificationChannelType,
    NotificationDeliveryStatus,
    NotificationPriority,
    NotificationType,
)
from goat.notifications.core.models import (
    Notification,
    NotificationAudit,
    NotificationChannel,
    NotificationDelivery,
    NotificationPayload,
    NotificationRecipient,
    NotificationSummary,
)

__all__ = [
    "NotificationType",
    "NotificationChannelType",
    "NotificationPriority",
    "NotificationDeliveryStatus",
    "NotificationAuditEventType",
    "compute_notification_id",
    "compute_recipient_id",
    "compute_channel_id",
    "compute_payload_id",
    "compute_delivery_id",
    "compute_audit_id",
    "compute_summary_id",
    "Notification",
    "NotificationRecipient",
    "NotificationChannel",
    "NotificationPayload",
    "NotificationDelivery",
    "NotificationAudit",
    "NotificationSummary",
]
