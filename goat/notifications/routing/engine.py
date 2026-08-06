"""
Project GOAT v0.8 — Notification Routing Engine

Determines recipient subscription targets, resolves priority classification,
and enforces deterministic duplicate notification suppression rules.
"""

from __future__ import annotations

from typing import Any

from goat.notifications.core.enums import NotificationChannelType, NotificationPriority, NotificationType
from goat.notifications.core.models import Notification, NotificationRecipient


DEFAULT_PRIORITY_MAP: dict[NotificationType, NotificationPriority] = {
    NotificationType.SIGNAL_GENERATED: NotificationPriority.MEDIUM,
    NotificationType.SIGNAL_QUALIFIED: NotificationPriority.MEDIUM,
    NotificationType.EXECUTION_SUBMITTED: NotificationPriority.MEDIUM,
    NotificationType.EXECUTION_ACCEPTED: NotificationPriority.MEDIUM,
    NotificationType.EXECUTION_FAILED: NotificationPriority.CRITICAL,
    NotificationType.TRADE_OPENED: NotificationPriority.HIGH,
    NotificationType.TRADE_MODIFIED: NotificationPriority.MEDIUM,
    NotificationType.STOP_LOSS_UPDATED: NotificationPriority.HIGH,
    NotificationType.TAKE_PROFIT_UPDATED: NotificationPriority.HIGH,
    NotificationType.TRAILING_STOP_UPDATED: NotificationPriority.MEDIUM,
    NotificationType.PARTIAL_CLOSE: NotificationPriority.HIGH,
    NotificationType.TRADE_CLOSED: NotificationPriority.HIGH,
    NotificationType.PORTFOLIO_UPDATE: NotificationPriority.LOW,
    NotificationType.RISK_ALERT: NotificationPriority.URGENT,
    NotificationType.LIFECYCLE_ALERT: NotificationPriority.HIGH,
    NotificationType.SYSTEM_WARNING: NotificationPriority.CRITICAL,
    NotificationType.HEALTH_NOTIFICATION: NotificationPriority.LOW,
    NotificationType.REPLAY_NOTIFICATION: NotificationPriority.LOW,
    NotificationType.GENERAL_ANNOUNCEMENT: NotificationPriority.LOW,
}


class NotificationRoutingEngine:
    """Engine resolving routing targets, priority levels, and duplicate suppression rules."""

    def __init__(self, suppression_window_seconds: float = 60.0):
        self.suppression_window_seconds = float(suppression_window_seconds)
        self._recipients: dict[str, NotificationRecipient] = {}  # recipient_id -> NotificationRecipient
        self._recent_fingerprints: dict[str, str] = {}  # fingerprint -> timestamp

    def register_recipient(self, recipient: NotificationRecipient) -> None:
        """Register a recipient target in the routing directory."""
        self._recipients[recipient.recipient_id] = recipient

    def resolve_priority(self, notification_type: NotificationType) -> NotificationPriority:
        """Resolve priority for a notification event type."""
        return DEFAULT_PRIORITY_MAP.get(notification_type, NotificationPriority.MEDIUM)

    def is_duplicate(self, notification_type: NotificationType, subject: str, body: str) -> bool:
        """Check if notification is a duplicate based on content fingerprint."""
        fingerprint = f"{notification_type.value}:{subject}:{body}"
        return fingerprint in self._recent_fingerprints

    def record_fingerprint(self, notification_type: NotificationType, subject: str, body: str, timestamp: str) -> None:
        """Record content fingerprint to enforce duplicate suppression."""
        fingerprint = f"{notification_type.value}:{subject}:{body}"
        self._recent_fingerprints[fingerprint] = timestamp

    def route_notification(
        self,
        notification: Notification,
        requested_channels: list[NotificationChannelType] | None = None,
    ) -> list[tuple[NotificationRecipient, NotificationChannelType]]:
        """Route notification to matching recipients and subscribed delivery channels."""
        targets: list[tuple[NotificationRecipient, NotificationChannelType]] = []
        filter_channels = set(requested_channels) if requested_channels else None

        for recipient in self._recipients.values():
            for channel in recipient.channels:
                if filter_channels and channel not in filter_channels:
                    continue
                targets.append((recipient, channel))

        return targets

    def get_all_recipients(self) -> list[NotificationRecipient]:
        return list(self._recipients.values())
