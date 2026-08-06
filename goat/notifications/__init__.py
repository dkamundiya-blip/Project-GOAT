"""
Project GOAT v0.8 — Notification & Distribution Platform

Export all public symbols via __all__. No implementation leakage.
"""

from goat.notifications.channels.engine import (
    BaseNotificationChannelHandler,
    DashboardChannelHandler,
    DesktopChannelHandler,
    DiscordChannelHandler,
    EmailChannelHandler,
    FileExportChannelHandler,
    MobileChannelHandler,
    NotificationChannelEngine,
    SMSChannelHandler,
    TelegramChannelHandler,
    WebhookChannelHandler,
)
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
from goat.notifications.engine import NotificationEngine
from goat.notifications.persistence.repository import (
    AuditRepository,
    DeliveryRepository,
    NotificationReportRepository,
    NotificationRepository,
    RecipientRepository,
    SQLiteNotificationRepository,
)
from goat.notifications.queue.engine import NotificationQueueEngine
from goat.notifications.reporting.reports import (
    AuditReport,
    BaseNotificationReport,
    DeliveryReport,
    NotificationExecutiveReport,
    NotificationReport,
    NotificationReportEngine,
    RecipientReport,
)
from goat.notifications.routing.engine import NotificationRoutingEngine
from goat.notifications.templates.engine import NotificationTemplateEngine

__all__ = [
    # Master Coordinator
    "NotificationEngine",
    # Subsystem Engines
    "NotificationRoutingEngine",
    "NotificationChannelEngine",
    "NotificationQueueEngine",
    "NotificationTemplateEngine",
    "NotificationReportEngine",
    # Enums
    "NotificationType",
    "NotificationChannelType",
    "NotificationPriority",
    "NotificationDeliveryStatus",
    "NotificationAuditEventType",
    # Canonical SHA-256 Generators
    "compute_notification_id",
    "compute_recipient_id",
    "compute_channel_id",
    "compute_payload_id",
    "compute_delivery_id",
    "compute_audit_id",
    "compute_summary_id",
    # Domain Models
    "Notification",
    "NotificationRecipient",
    "NotificationChannel",
    "NotificationPayload",
    "NotificationDelivery",
    "NotificationAudit",
    "NotificationSummary",
    # Channel Handlers
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
    # Persistence Repositories
    "SQLiteNotificationRepository",
    "NotificationRepository",
    "RecipientRepository",
    "DeliveryRepository",
    "AuditRepository",
    "NotificationReportRepository",
    # Reports
    "BaseNotificationReport",
    "NotificationReport",
    "DeliveryReport",
    "RecipientReport",
    "AuditReport",
    "NotificationExecutiveReport",
]
