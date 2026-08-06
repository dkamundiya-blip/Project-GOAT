"""
Project GOAT v0.8 — Step 7.7 Public API Dedicated Unit Tests
"""

import pytest

import goat.notifications as notifications_pkg


def test_public_api_exports():
    expected_exports = [
        "NotificationEngine",
        "NotificationRoutingEngine",
        "NotificationChannelEngine",
        "NotificationQueueEngine",
        "NotificationTemplateEngine",
        "NotificationReportEngine",
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
        "BaseNotificationChannelHandler",
        "DashboardChannelHandler",
        "DesktopChannelHandler",
        "MobileChannelHandler",
        "TelegramChannelHandler",
        "DiscordChannelHandler",
        "WebhookChannelHandler",
        "EmailChannelHandler",
        "SMSChannelHandler",
        "FileExportChannelHandler",
        "SQLiteNotificationRepository",
        "NotificationRepository",
        "RecipientRepository",
        "DeliveryRepository",
        "AuditRepository",
        "NotificationReportRepository",
        "BaseNotificationReport",
        "NotificationReport",
        "DeliveryReport",
        "RecipientReport",
        "AuditReport",
        "NotificationExecutiveReport",
    ]

    for item in expected_exports:
        assert hasattr(notifications_pkg, item)
    assert set(notifications_pkg.__all__) == set(expected_exports)
