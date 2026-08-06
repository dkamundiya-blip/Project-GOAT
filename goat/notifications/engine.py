"""
Project GOAT v0.8 — Notification Engine Master Coordinator

Master coordinator implementing canonical notification and distribution platform.
Integrates NotificationRoutingEngine, NotificationChannelEngine, NotificationQueueEngine,
NotificationTemplateEngine, SQLiteNotificationRepository, and NotificationReportEngine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from goat.notifications.channels.engine import NotificationChannelEngine
from goat.notifications.core.canonical import (
    compute_audit_id,
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
    NotificationDelivery,
    NotificationPayload,
    NotificationRecipient,
    NotificationSummary,
)
from goat.notifications.persistence.repository import SQLiteNotificationRepository
from goat.notifications.queue.engine import NotificationQueueEngine
from goat.notifications.reporting.reports import NotificationExecutiveReport, NotificationReportEngine
from goat.notifications.routing.engine import NotificationRoutingEngine
from goat.notifications.templates.engine import NotificationTemplateEngine


class NotificationEngine:
    """Master coordinator managing notification routing, formatting, queuing, and dispatch planning."""

    def __init__(self, db_path: str | Path | None = None):
        self.routing_engine = NotificationRoutingEngine()
        self.channel_engine = NotificationChannelEngine()
        self.queue_engine = NotificationQueueEngine()
        self.template_engine = NotificationTemplateEngine()
        self.report_engine = NotificationReportEngine()

        self.repository = SQLiteNotificationRepository(db_path) if db_path else None

        self._audit_log: list[NotificationAudit] = []
        self._notifications: dict[str, Notification] = {}  # notification_id -> Notification

    def close(self) -> None:
        """Close database connection if active."""
        if self.repository:
            self.repository.close()

    def _record_audit(
        self,
        notification_id: str,
        event_type: NotificationAuditEventType | str,
        reason: str,
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> NotificationAudit:
        evt_enum = (
            NotificationAuditEventType(str(event_type).upper())
            if not isinstance(event_type, NotificationAuditEventType)
            else event_type
        )
        audit_id, audit_hash = compute_audit_id(
            notification_id=notification_id,
            event_type=evt_enum.value,
            timestamp=timestamp,
        )

        audit = NotificationAudit(
            audit_id=audit_id,
            notification_id=notification_id,
            event_type=evt_enum,
            reason=reason,
            timestamp=timestamp,
            metadata=metadata or {},
            canonical_hash=audit_hash,
        )

        self._audit_log.append(audit)
        if self.repository:
            self.repository.save_audit(audit)
        return audit

    def register_recipient(
        self,
        name: str,
        role: str,
        destination: str,
        channels: list[NotificationChannelType | str],
        metadata: dict[str, Any] | None = None,
    ) -> NotificationRecipient:
        """Register subscriber recipient target."""
        parsed_channels = [
            c if isinstance(c, NotificationChannelType) else NotificationChannelType(str(c).upper())
            for c in channels
        ]

        nrc_id, nrc_hash = compute_recipient_id(name=name, destination=destination)

        recipient = NotificationRecipient(
            recipient_id=nrc_id,
            name=name,
            role=role,
            destination=destination,
            channels=parsed_channels,
            metadata=metadata or {},
            canonical_hash=nrc_hash,
        )

        self.routing_engine.register_recipient(recipient)
        if self.repository:
            self.repository.save_recipient(recipient)

        return recipient

    def create_payload(
        self,
        event_type: str,
        source_subsystem: str,
        payload_data: dict[str, Any],
        created_at: str,
    ) -> NotificationPayload:
        """Create an immutable event payload reference."""
        npl_id, npl_hash = compute_payload_id(
            event_type=event_type,
            source_subsystem=source_subsystem,
            created_at=created_at,
        )
        return NotificationPayload(
            payload_id=npl_id,
            event_type=event_type,
            source_subsystem=source_subsystem,
            payload_data=payload_data,
            created_at=created_at,
            canonical_hash=npl_hash,
        )

    def notify(
        self,
        notification_type: NotificationType | str,
        subject: str,
        body: str,
        timestamp: str,
        priority: NotificationPriority | str | None = None,
        payload_id: str = "",
        metadata: dict[str, Any] | None = None,
        requested_channels: list[NotificationChannelType | str] | None = None,
    ) -> tuple[Notification, list[NotificationDelivery]]:
        """Publish and route notification to subscribed recipient channels."""
        ntype_enum = (
            NotificationType(str(notification_type).upper())
            if not isinstance(notification_type, NotificationType)
            else notification_type
        )

        if priority is None:
            prio_enum = self.routing_engine.resolve_priority(ntype_enum)
        else:
            prio_enum = (
                NotificationPriority(str(priority).upper())
                if not isinstance(priority, NotificationPriority)
                else priority
            )

        # Check duplicate suppression
        if self.routing_engine.is_duplicate(ntype_enum, subject, body):
            ntf_id, ntf_hash = compute_notification_id(ntype_enum.value, subject, timestamp)
            notification = Notification(
                notification_id=ntf_id,
                notification_type=ntype_enum,
                priority=prio_enum,
                subject=subject,
                body=body,
                payload_id=payload_id,
                created_at=timestamp,
                metadata=metadata or {},
                canonical_hash=ntf_hash,
            )
            self._record_audit(
                notification_id=ntf_id,
                event_type=NotificationAuditEventType.DUPLICATE_SUPPRESSED,
                reason=f"Duplicate notification suppressed: {subject}",
                timestamp=timestamp,
            )
            return notification, []

        self.routing_engine.record_fingerprint(ntype_enum, subject, body, timestamp)

        ntf_id, ntf_hash = compute_notification_id(ntype_enum.value, subject, timestamp)
        notification = Notification(
            notification_id=ntf_id,
            notification_type=ntype_enum,
            priority=prio_enum,
            subject=subject,
            body=body,
            payload_id=payload_id,
            created_at=timestamp,
            metadata=metadata or {},
            canonical_hash=ntf_hash,
        )

        self._notifications[ntf_id] = notification
        if self.repository:
            self.repository.save_notification(notification)

        self._record_audit(
            notification_id=ntf_id,
            event_type=NotificationAuditEventType.NOTIFICATION_CREATED,
            reason=f"Created notification [{ntype_enum.value}]: {subject}",
            timestamp=timestamp,
        )

        # Route to target recipients and channels
        req_channels_parsed = None
        if requested_channels:
            req_channels_parsed = [
                c if isinstance(c, NotificationChannelType) else NotificationChannelType(str(c).upper())
                for c in requested_channels
            ]

        targets = self.routing_engine.route_notification(notification, req_channels_parsed)
        deliveries: list[NotificationDelivery] = []

        for recipient, channel in targets:
            delivery = self.queue_engine.enqueue_delivery(
                notification=notification,
                recipient=recipient,
                channel_type=channel,
                delivered_at=timestamp,
                status=NotificationDeliveryStatus.QUEUED,
            )
            deliveries.append(delivery)

            if self.repository:
                self.repository.save_delivery(delivery)

            self._record_audit(
                notification_id=ntf_id,
                event_type=NotificationAuditEventType.NOTIFICATION_ENQUEUED,
                reason=f"Enqueued delivery to {recipient.name} via {channel.value}",
                timestamp=timestamp,
            )

        return notification, deliveries

    def process_queue(self, timestamp: str) -> list[NotificationDelivery]:
        """Process queued delivery items and execute dispatch planning."""
        queued = self.queue_engine.get_queued_deliveries()
        processed: list[NotificationDelivery] = []

        for delivery in queued:
            # Execute dispatch planning via channel engine
            notification = self._notifications.get(delivery.notification_id)
            recipients = {r.recipient_id: r for r in self.routing_engine.get_all_recipients()}
            recipient = recipients.get(delivery.recipient_id)

            if notification and recipient:
                dispatch_plan = self.channel_engine.plan_dispatch(notification, recipient, delivery.channel_type)

            updated = self.queue_engine.update_delivery_status(
                delivery_id=delivery.delivery_id,
                status=NotificationDeliveryStatus.DELIVERED,
                delivered_at=timestamp,
            )
            processed.append(updated)

            if self.repository:
                self.repository.save_delivery(updated)

            self._record_audit(
                notification_id=delivery.notification_id,
                event_type=NotificationAuditEventType.DELIVERY_RECORDED,
                reason=f"Delivered to {delivery.recipient_id} via {delivery.channel_type.value}",
                timestamp=timestamp,
            )

        return processed

    def render_template(
        self,
        notification_type: NotificationType | str,
        subject: str,
        body: str,
        format_type: str = "markdown",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Render notification using specified format template."""
        fmt = str(format_type).lower()
        if fmt == "markdown":
            return self.template_engine.render_markdown(notification_type, subject, body, metadata)
        elif fmt == "json":
            return self.template_engine.render_canonical_json(notification_type, subject, body, metadata)
        elif fmt == "html":
            return self.template_engine.render_html(notification_type, subject, body, metadata)
        else:
            return self.template_engine.render_plain_text(notification_type, subject, body, metadata)

    def get_summary(self, timestamp: str) -> NotificationSummary:
        """Compute aggregated NotificationSummary metrics."""
        total_ntf = len(self._notifications)
        all_deliv = self.queue_engine.get_all_deliveries()
        total_deliv = len(all_deliv)
        pending = sum(1 for d in all_deliv if d.status == NotificationDeliveryStatus.QUEUED)
        delivered = sum(1 for d in all_deliv if d.status == NotificationDeliveryStatus.DELIVERED)
        failed = sum(1 for d in all_deliv if d.status == NotificationDeliveryStatus.FAILED)

        nsm_id, nsm_hash = compute_summary_id(total_ntf, timestamp)
        return NotificationSummary(
            summary_id=nsm_id,
            total_notifications=total_ntf,
            total_deliveries=total_deliv,
            pending_deliveries=pending,
            delivered_count=delivered,
            failed_count=failed,
            timestamp=timestamp,
            canonical_hash=nsm_hash,
        )

    def generate_executive_report(self, timestamp: str) -> NotificationExecutiveReport:
        """Generate complete NotificationExecutiveReport in Markdown and JSON formats."""
        summary = self.get_summary(timestamp)
        recipients = self.routing_engine.get_all_recipients()
        recent_deliveries = self.queue_engine.get_all_deliveries()[-20:]

        report = self.report_engine.build_executive_report(summary, recipients, recent_deliveries)

        if self.repository:
            self.repository.save_report(f"REP_{summary.summary_id[4:]}", "EXECUTIVE", timestamp, report.to_markdown(), report.get_dict())

        return report

    def get_audit_log(self) -> list[NotificationAudit]:
        return list(self._audit_log)
