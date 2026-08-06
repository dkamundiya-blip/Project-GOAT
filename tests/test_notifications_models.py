"""
Project GOAT v0.8 — Step 7.7 Notification Models Dedicated Unit Tests
"""

import pytest
from pydantic import ValidationError

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


def test_canonical_id_prefixes():
    ntf_id, ntf_hash = compute_notification_id("SIGNAL_GENERATED", "Test Signal", "2026-08-01T00:00:00Z")
    assert ntf_id.startswith("NTF_")
    assert len(ntf_id) == 20
    assert len(ntf_hash) == 64

    nrc_id, nrc_hash = compute_recipient_id("Trader Joe", "tg_12345")
    assert nrc_id.startswith("NRC_")
    assert len(nrc_id) == 20

    nch_id, nch_hash = compute_channel_id("TELEGRAM")
    assert nch_id.startswith("NCH_")
    assert len(nch_id) == 20

    npl_id, npl_hash = compute_payload_id("EXECUTION_FILLED", "Step 7.4", "2026-08-01T00:00:00Z")
    assert npl_id.startswith("NPL_")
    assert len(npl_id) == 20

    ndl_id, ndl_hash = compute_delivery_id(ntf_id, nrc_id, "TELEGRAM", "2026-08-01T00:00:00Z")
    assert ndl_id.startswith("NDL_")
    assert len(ndl_id) == 20

    nad_id, nad_hash = compute_audit_id(ntf_id, "NOTIFICATION_CREATED", "2026-08-01T00:00:00Z")
    assert nad_id.startswith("NAD_")
    assert len(nad_id) == 20

    nsm_id, nsm_hash = compute_summary_id(10, "2026-08-01T00:00:00Z")
    assert nsm_id.startswith("NSM_")
    assert len(nsm_id) == 20


def test_notification_model_immutability():
    ntf_id, ntf_hash = compute_notification_id("SIGNAL_GENERATED", "Test Signal", "2026-08-01T00:00:00Z")
    notification = Notification(
        notification_id=ntf_id,
        notification_type=NotificationType.SIGNAL_GENERATED,
        subject="Test Signal",
        body="Body text",
        created_at="2026-08-01T00:00:00Z",
        canonical_hash=ntf_hash,
    )

    with pytest.raises(ValidationError):
        notification.subject = "Modified Subject"


def test_notification_model_extra_forbid():
    ntf_id, ntf_hash = compute_notification_id("SIGNAL_GENERATED", "Test Signal", "2026-08-01T00:00:00Z")
    with pytest.raises(ValidationError):
        Notification(
            notification_id=ntf_id,
            notification_type=NotificationType.SIGNAL_GENERATED,
            subject="Test Signal",
            body="Body text",
            created_at="2026-08-01T00:00:00Z",
            canonical_hash=ntf_hash,
            forbidden_extra_field="invalid",
        )


@pytest.mark.parametrize("idx", range(150))
def test_notification_model_serialization_matrix(idx):
    ntf_id, ntf_hash = compute_notification_id(f"SIGNAL_GENERATED_{idx}", f"Test Subject {idx}", f"2026-08-01T00:{idx % 60:02d}:00Z")
    notification = Notification(
        notification_id=ntf_id,
        notification_type=NotificationType.SIGNAL_GENERATED,
        priority=NotificationPriority.HIGH,
        subject=f"Test Subject {idx}",
        body=f"Body text content for index {idx}",
        created_at=f"2026-08-01T00:{idx % 60:02d}:00Z",
        canonical_hash=ntf_hash,
    )
    json_str = notification.model_dump_json()
    reloaded = Notification.model_validate_json(json_str)
    assert reloaded == notification
