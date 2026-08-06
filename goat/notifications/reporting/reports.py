"""
Project GOAT v0.8 — Notification Reporting Engine

Generates canonical Markdown and JSON reports for:
- NotificationReport
- DeliveryReport
- RecipientReport
- AuditReport
- NotificationExecutiveReport

Supports to_markdown() and to_json() formatting.
"""

from __future__ import annotations

import json
from typing import Any

from goat.notifications.core.models import (
    Notification,
    NotificationAudit,
    NotificationDelivery,
    NotificationRecipient,
    NotificationSummary,
)


class BaseNotificationReport:
    """Base report class providing to_markdown() and to_json() contract interface."""

    def __init__(self, title: str, markdown_content: str, json_payload: dict[str, Any]):
        self.title = title
        self._markdown = markdown_content
        self._json_payload = json_payload

    def to_markdown(self) -> str:
        return self._markdown

    def to_json(self) -> str:
        return json.dumps(self._json_payload, indent=2, sort_keys=True)

    def get_dict(self) -> dict[str, Any]:
        return dict(self._json_payload)


class NotificationReport(BaseNotificationReport):
    """Report detailing single notification content and routing."""
    pass


class DeliveryReport(BaseNotificationReport):
    """Report detailing delivery attempt logs across target recipients."""
    pass


class RecipientReport(BaseNotificationReport):
    """Report detailing registered subscribers and channel configurations."""
    pass


class AuditReport(BaseNotificationReport):
    """Report detailing audit trail events for notification platform."""
    pass


class NotificationExecutiveReport(BaseNotificationReport):
    """Executive report combining notification summary, channel breakdown, and delivery health."""
    pass


class NotificationReportEngine:
    """Reporting engine generating structured Markdown and JSON reports."""

    def build_notification_report(self, notification: Notification) -> NotificationReport:
        json_data = notification.model_dump()
        markdown = f"""# GOAT Notification Report

- **Notification ID**: `{notification.notification_id}`
- **Type**: `{notification.notification_type.value}`
- **Priority**: `{notification.priority.value}`
- **Subject**: {notification.subject}
- **Created At**: {notification.created_at}

## Body
{notification.body}

---
*Canonical Hash*: `{notification.canonical_hash}`
"""
        return NotificationReport("Notification Report", markdown, json_data)

    def build_delivery_report(self, deliveries: list[NotificationDelivery]) -> DeliveryReport:
        json_data = {
            "deliveries_count": len(deliveries),
            "deliveries": [d.model_dump() for d in deliveries],
        }

        rows = []
        for d in deliveries:
            rows.append(
                f"| `{d.delivery_id[:12]}` | `{d.notification_id[:12]}` | `{d.recipient_id[:12]}` | `{d.channel_type.value}` | `{d.status.value}` | {d.attempt_count} | {d.delivered_at} |"
            )
        table = "\n".join(rows) if rows else "| None | - | - | - | - | - | - |"

        markdown = f"""# GOAT Notification Delivery Report

- **Total Deliveries**: {len(deliveries)}

| Delivery ID | Notification ID | Recipient ID | Channel | Status | Attempts | Timestamp |
|---|---|---|---|---|---|---|
{table}
"""
        return DeliveryReport("Notification Delivery Report", markdown, json_data)

    def build_recipient_report(self, recipients: list[NotificationRecipient]) -> RecipientReport:
        json_data = {
            "recipients_count": len(recipients),
            "recipients": [r.model_dump() for r in recipients],
        }

        rows = []
        for r in recipients:
            channels_str = ", ".join([c.value for c in r.channels])
            rows.append(f"| `{r.recipient_id[:12]}` | {r.name} | `{r.role}` | `{r.destination}` | `{channels_str}` |")
        table = "\n".join(rows) if rows else "| None | - | - | - | - |"

        markdown = f"""# GOAT Notification Recipient Directory Report

- **Total Registered Recipients**: {len(recipients)}

| Recipient ID | Name | Role | Destination | Subscribed Channels |
|---|---|---|---|---|
{table}
"""
        return RecipientReport("Notification Recipient Directory Report", markdown, json_data)

    def build_audit_report(self, audits: list[NotificationAudit], notification_id: str = "") -> AuditReport:
        json_data = {
            "notification_id": notification_id,
            "audits_count": len(audits),
            "audits": [a.model_dump() for a in audits],
        }

        rows = []
        for a in audits:
            rows.append(f"| `{a.audit_id[:12]}` | `{a.event_type.value}` | {a.reason} | {a.timestamp} |")
        table = "\n".join(rows) if rows else "| None | - | - | - |"

        markdown = f"""# GOAT Notification Audit Trail Report

- **Target Notification ID**: `{notification_id or 'ALL'}`
- **Total Audit Logs**: {len(audits)}

| Audit ID | Event Type | Reason | Timestamp |
|---|---|---|---|
{table}
"""
        return AuditReport("Notification Audit Trail Report", markdown, json_data)

    def build_executive_report(
        self,
        summary: NotificationSummary,
        recipients: list[NotificationRecipient],
        recent_deliveries: list[NotificationDelivery],
    ) -> NotificationExecutiveReport:
        json_data = {
            "summary": summary.model_dump(),
            "recipients_count": len(recipients),
            "recent_deliveries_count": len(recent_deliveries),
            "recent_deliveries": [d.model_dump() for d in recent_deliveries],
        }

        markdown = f"""# GOAT Notification Platform Executive Report

- **Timestamp**: {summary.timestamp}
- **Summary ID**: `{summary.summary_id}`

## Delivery Metrics
- **Total Notifications**: {summary.total_notifications}
- **Total Delivery Records**: {summary.total_deliveries}
- **Successfully Delivered**: {summary.delivered_count}
- **Pending / Queued**: {summary.pending_deliveries}
- **Failed Deliveries**: {summary.failed_count}

## Subscriber Directory
- **Registered Recipients**: {len(recipients)}
"""
        return NotificationExecutiveReport("Notification Platform Executive Report", markdown, json_data)
