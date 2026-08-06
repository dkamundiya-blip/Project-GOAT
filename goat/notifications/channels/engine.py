"""
Project GOAT v0.8 — Notification Channel Engine

Provides logical channel abstractions for payload formatting, serialization, and dispatch planning.
Supports 9 delivery channels: Dashboard, Desktop, Mobile, Telegram, Discord, Webhook, Email, SMS, File Export.

Strictly non-network: No live APIs, SDKs, sockets, or HTTP connections.
"""

from __future__ import annotations

import json
from typing import Any

from goat.notifications.core.enums import NotificationChannelType
from goat.notifications.core.models import Notification, NotificationChannel, NotificationRecipient


class BaseNotificationChannelHandler:
    """Base channel handler contract for payload serialization and dispatch planning."""

    def __init__(self, channel_type: NotificationChannelType):
        self.channel_type = channel_type

    def prepare_dispatch_payload(
        self,
        notification: Notification,
        recipient: NotificationRecipient,
        channel_config: NotificationChannel | None = None,
    ) -> dict[str, Any]:
        """Serialize notification into channel-specific payload dictionary."""
        return {
            "channel_type": self.channel_type.value,
            "recipient_id": recipient.recipient_id,
            "destination": recipient.destination,
            "subject": notification.subject,
            "body": notification.body,
            "priority": notification.priority.value,
            "notification_type": notification.notification_type.value,
            "created_at": notification.created_at,
            "metadata": notification.metadata,
        }


class DashboardChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.DASHBOARD)


class DesktopChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.DESKTOP)


class MobileChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.MOBILE)


class TelegramChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.TELEGRAM)

    def prepare_dispatch_payload(self, notification: Notification, recipient: NotificationRecipient, channel_config: NotificationChannel | None = None) -> dict[str, Any]:
        base = super().prepare_dispatch_payload(notification, recipient, channel_config)
        base["parse_mode"] = "MarkdownV2"
        base["chat_id"] = recipient.destination
        return base


class DiscordChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.DISCORD)

    def prepare_dispatch_payload(self, notification: Notification, recipient: NotificationRecipient, channel_config: NotificationChannel | None = None) -> dict[str, Any]:
        base = super().prepare_dispatch_payload(notification, recipient, channel_config)
        base["embeds"] = [{"title": notification.subject, "description": notification.body}]
        return base


class WebhookChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.WEBHOOK)


class EmailChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.EMAIL)


class SMSChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.SMS)


class FileExportChannelHandler(BaseNotificationChannelHandler):
    def __init__(self):
        super().__init__(NotificationChannelType.FILE_EXPORT)


class NotificationChannelEngine:
    """Engine managing logical channel dispatch planning and serialization."""

    def __init__(self):
        self._handlers: dict[NotificationChannelType, BaseNotificationChannelHandler] = {
            NotificationChannelType.DASHBOARD: DashboardChannelHandler(),
            NotificationChannelType.DESKTOP: DesktopChannelHandler(),
            NotificationChannelType.MOBILE: MobileChannelHandler(),
            NotificationChannelType.TELEGRAM: TelegramChannelHandler(),
            NotificationChannelType.DISCORD: DiscordChannelHandler(),
            NotificationChannelType.WEBHOOK: WebhookChannelHandler(),
            NotificationChannelType.EMAIL: EmailChannelHandler(),
            NotificationChannelType.SMS: SMSChannelHandler(),
            NotificationChannelType.FILE_EXPORT: FileExportChannelHandler(),
        }

    def get_handler(self, channel_type: NotificationChannelType) -> BaseNotificationChannelHandler:
        handler = self._handlers.get(channel_type)
        if handler is None:
            raise ValueError(f"Unsupported notification channel type: {channel_type}")
        return handler

    def plan_dispatch(
        self,
        notification: Notification,
        recipient: NotificationRecipient,
        channel_type: NotificationChannelType,
    ) -> dict[str, Any]:
        """Generate deterministic dispatch payload dictionary for channel."""
        handler = self.get_handler(channel_type)
        return handler.prepare_dispatch_payload(notification, recipient)
