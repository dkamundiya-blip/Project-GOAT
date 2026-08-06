"""
Project GOAT v0.8 — Core Immutable Domain Models for Notification & Distribution Platform

Defines immutable Pydantic V2 models using ConfigDict(frozen=True, extra="forbid"):
- Notification (NTF_<HEX16>)
- NotificationRecipient (NRC_<HEX16>)
- NotificationChannel (NCH_<HEX16>)
- NotificationPayload (NPL_<HEX16>)
- NotificationDelivery (NDL_<HEX16>)
- NotificationAudit (NAD_<HEX16>)
- NotificationSummary (NSM_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.notifications.core.enums import (
    NotificationAuditEventType,
    NotificationChannelType,
    NotificationDeliveryStatus,
    NotificationPriority,
    NotificationType,
)


class Notification(BaseModel):
    """Immutable model representing a notification message entity."""

    notification_id: str = Field(
        ...,
        description="Unique notification ID formatted as NTF_<HEX16>",
        pattern=r"^NTF_[A-Fa-f0-9]{16}$",
    )
    notification_type: NotificationType = Field(..., description="Notification event type enum")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Priority classification")
    subject: str = Field(..., description="Notification title / subject line")
    body: str = Field(..., description="Formatted notification text body")
    payload_id: str = Field(default="", description="Associated NotificationPayload ID reference")
    created_at: str = Field(..., description="ISO 8601 UTC timestamp of creation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class NotificationRecipient(BaseModel):
    """Immutable model representing a notification destination recipient."""

    recipient_id: str = Field(
        ...,
        description="Unique recipient ID formatted as NRC_<HEX16>",
        pattern=r"^NRC_[A-Fa-f0-9]{16}$",
    )
    name: str = Field(..., description="Recipient display name or subscriber ID")
    role: str = Field(default="USER", description="Role classification (ADMIN, TRADER, SYSTEM, AUDITOR)")
    destination: str = Field(..., description="Target endpoint string (chat_id, webhook URL, email address, file path)")
    channels: list[NotificationChannelType] = Field(default_factory=list, description="Subscribed channel types")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class NotificationChannel(BaseModel):
    """Immutable model representing a delivery channel configuration."""

    channel_id: str = Field(
        ...,
        description="Unique channel ID formatted as NCH_<HEX16>",
        pattern=r"^NCH_[A-Fa-f0-9]{16}$",
    )
    channel_type: NotificationChannelType = Field(..., description="Delivery channel classification")
    enabled: bool = Field(default=True, description="Channel activation status flag")
    config: dict[str, Any] = Field(default_factory=dict, description="Channel configuration parameters")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class NotificationPayload(BaseModel):
    """Immutable model representing underlying event telemetry payload data."""

    payload_id: str = Field(
        ...,
        description="Unique payload ID formatted as NPL_<HEX16>",
        pattern=r"^NPL_[A-Fa-f0-9]{16}$",
    )
    event_type: str = Field(..., description="Source event type name")
    source_subsystem: str = Field(..., description="Originating subsystem (Step 7.4, 7.5, 7.6)")
    payload_data: dict[str, Any] = Field(default_factory=dict, description="Raw structured payload dictionary")
    created_at: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class NotificationDelivery(BaseModel):
    """Immutable model representing a planned or executed notification delivery record."""

    delivery_id: str = Field(
        ...,
        description="Unique delivery record ID formatted as NDL_<HEX16>",
        pattern=r"^NDL_[A-Fa-f0-9]{16}$",
    )
    notification_id: str = Field(..., description="Target Notification ID")
    recipient_id: str = Field(..., description="Target NotificationRecipient ID")
    channel_type: NotificationChannelType = Field(..., description="Delivery channel enum")
    status: NotificationDeliveryStatus = Field(default=NotificationDeliveryStatus.QUEUED, description="Delivery status")
    attempt_count: int = Field(default=0, ge=0, description="Delivery attempt count")
    delivered_at: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class NotificationAudit(BaseModel):
    """Immutable audit trail record for notification routing and queue events."""

    audit_id: str = Field(
        ...,
        description="Unique audit ID formatted as NAD_<HEX16>",
        pattern=r"^NAD_[A-Fa-f0-9]{16}$",
    )
    notification_id: str = Field(..., description="Target Notification ID")
    event_type: NotificationAuditEventType = Field(..., description="Audit event category enum")
    reason: str = Field(..., description="Detailed rationale")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class NotificationSummary(BaseModel):
    """Immutable summary record for notification subsystem metrics."""

    summary_id: str = Field(
        ...,
        description="Unique summary ID formatted as NSM_<HEX16>",
        pattern=r"^NSM_[A-Fa-f0-9]{16}$",
    )
    total_notifications: int = Field(..., ge=0, description="Total notifications generated")
    total_deliveries: int = Field(..., ge=0, description="Total delivery records created")
    pending_deliveries: int = Field(..., ge=0, description="Pending queued deliveries")
    delivered_count: int = Field(..., ge=0, description="Successfully delivered count")
    failed_count: int = Field(..., ge=0, description="Failed delivery count")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")
