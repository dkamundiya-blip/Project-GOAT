"""
Project GOAT v0.8 — Notification Platform Persistence Repositories

Implements transactional SQLite persistence for:
- NotificationRepository
- RecipientRepository
- DeliveryRepository
- AuditRepository
- NotificationReportRepository

Enforces WAL journal mode, foreign key constraints, replayability, ON CONFLICT DO UPDATE, and deterministic serialization.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.notifications.core.models import (
    Notification,
    NotificationAudit,
    NotificationChannel,
    NotificationDelivery,
    NotificationPayload,
    NotificationRecipient,
)

NOTIFICATION_SCHEMA_VERSION = 1


class SQLiteNotificationRepository:
    """Transactional SQLite WAL repository managing notification platform entities."""

    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Initialize database schema with versioning and foreign keys."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS notification_schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO notification_schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id TEXT PRIMARY KEY,
                    notification_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    payload_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS recipients (
                    recipient_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    notification_id TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempt_count INTEGER NOT NULL,
                    delivered_at TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (notification_id) REFERENCES notifications(notification_id) ON DELETE CASCADE,
                    FOREIGN KEY (recipient_id) REFERENCES recipients(recipient_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS notification_audits (
                    audit_id TEXT PRIMARY KEY,
                    notification_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notification_reports (
                    report_id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );
            """)

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Notification Operations
    # ------------------------------------------------------------------

    def save_notification(self, notification: Notification) -> None:
        json_str = notification.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO notifications (
                    notification_id, notification_type, priority, subject, body,
                    payload_id, created_at, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(notification_id) DO UPDATE SET
                    priority=excluded.priority,
                    subject=excluded.subject,
                    body=excluded.body,
                    json_data=excluded.json_data
                """,
                (
                    notification.notification_id,
                    notification.notification_type.value if hasattr(notification.notification_type, "value") else str(notification.notification_type),
                    notification.priority.value if hasattr(notification.priority, "value") else str(notification.priority),
                    notification.subject,
                    notification.body,
                    notification.payload_id,
                    notification.created_at,
                    notification.canonical_hash,
                    json_str,
                ),
            )

    def get_notification(self, notification_id: str) -> Notification | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM notifications WHERE notification_id = ?",
            (notification_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Notification.model_validate_json(row["json_data"])

    def get_all_notifications(self) -> list[Notification]:
        cursor = self._conn.execute("SELECT json_data FROM notifications ORDER BY created_at ASC")
        return [Notification.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Recipient Operations
    # ------------------------------------------------------------------

    def save_recipient(self, recipient: NotificationRecipient) -> None:
        json_str = recipient.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO recipients (
                    recipient_id, name, role, destination, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(recipient_id) DO UPDATE SET
                    name=excluded.name,
                    role=excluded.role,
                    destination=excluded.destination,
                    json_data=excluded.json_data
                """,
                (
                    recipient.recipient_id,
                    recipient.name,
                    recipient.role,
                    recipient.destination,
                    recipient.canonical_hash,
                    json_str,
                ),
            )

    def get_recipient(self, recipient_id: str) -> NotificationRecipient | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM recipients WHERE recipient_id = ?",
            (recipient_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return NotificationRecipient.model_validate_json(row["json_data"])

    def get_all_recipients(self) -> list[NotificationRecipient]:
        cursor = self._conn.execute("SELECT json_data FROM recipients")
        return [NotificationRecipient.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Delivery Operations
    # ------------------------------------------------------------------

    def save_delivery(self, delivery: NotificationDelivery) -> None:
        json_str = delivery.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO deliveries (
                    delivery_id, notification_id, recipient_id, channel_type, status,
                    attempt_count, delivered_at, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(delivery_id) DO UPDATE SET
                    status=excluded.status,
                    attempt_count=excluded.attempt_count,
                    delivered_at=excluded.delivered_at,
                    json_data=excluded.json_data
                """,
                (
                    delivery.delivery_id,
                    delivery.notification_id,
                    delivery.recipient_id,
                    delivery.channel_type.value if hasattr(delivery.channel_type, "value") else str(delivery.channel_type),
                    delivery.status.value if hasattr(delivery.status, "value") else str(delivery.status),
                    delivery.attempt_count,
                    delivery.delivered_at,
                    delivery.canonical_hash,
                    json_str,
                ),
            )

    def get_deliveries(self, notification_id: str) -> list[NotificationDelivery]:
        cursor = self._conn.execute(
            "SELECT json_data FROM deliveries WHERE notification_id = ? ORDER BY delivered_at ASC",
            (notification_id,),
        )
        return [NotificationDelivery.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Audit & Report Operations
    # ------------------------------------------------------------------

    def save_audit(self, audit: NotificationAudit) -> None:
        json_str = audit.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO notification_audits (
                    audit_id, notification_id, event_type, reason, timestamp,
                    canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.audit_id,
                    audit.notification_id,
                    audit.event_type.value if hasattr(audit.event_type, "value") else str(audit.event_type),
                    audit.reason,
                    audit.timestamp,
                    audit.canonical_hash,
                    json_str,
                ),
            )

    def get_audits(self, notification_id: str) -> list[NotificationAudit]:
        cursor = self._conn.execute(
            "SELECT json_data FROM notification_audits WHERE notification_id = ? ORDER BY timestamp ASC",
            (notification_id,),
        )
        return [NotificationAudit.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    def save_report(self, report_id: str, report_type: str, timestamp: str, content: str, json_data: dict[str, Any]) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO notification_reports (
                    report_id, report_type, timestamp, content, json_data
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    report_type,
                    timestamp,
                    content,
                    json.dumps(json_data, sort_keys=True),
                ),
            )


# Named repository exports mapped to the unified SQLite WAL repository
class NotificationRepository(SQLiteNotificationRepository):
    pass

class RecipientRepository(SQLiteNotificationRepository):
    pass

class DeliveryRepository(SQLiteNotificationRepository):
    pass

class AuditRepository(SQLiteNotificationRepository):
    pass

class NotificationReportRepository(SQLiteNotificationRepository):
    pass
