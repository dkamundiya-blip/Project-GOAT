"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Notification Platform

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- Notification (NTF_<HEX16>)
- NotificationRecipient (NRC_<HEX16>)
- NotificationChannel (NCH_<HEX16>)
- NotificationPayload (NPL_<HEX16>)
- NotificationDelivery (NDL_<HEX16>)
- NotificationAudit (NAD_<HEX16>)
- NotificationSummary (NSM_<HEX16>)
"""

from goat.research.edge.canonical import compute_canonical_sha256


def compute_notification_id(
    notification_type: str,
    subject: str,
    created_at: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "created_at": str(created_at).strip(),
        "notification_type": str(notification_type).strip().upper(),
        "subject": str(subject).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NTF_{digest[:16].upper()}", digest.upper()


def compute_recipient_id(
    name: str,
    destination: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "destination": str(destination).strip(),
        "name": str(name).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NRC_{digest[:16].upper()}", digest.upper()


def compute_channel_id(
    channel_type: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "channel_type": str(channel_type).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NCH_{digest[:16].upper()}", digest.upper()


def compute_payload_id(
    event_type: str,
    source_subsystem: str,
    created_at: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "created_at": str(created_at).strip(),
        "event_type": str(event_type).strip().upper(),
        "source_subsystem": str(source_subsystem).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NPL_{digest[:16].upper()}", digest.upper()


def compute_delivery_id(
    notification_id: str,
    recipient_id: str,
    channel_type: str,
    delivered_at: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "channel_type": str(channel_type).strip().upper(),
        "delivered_at": str(delivered_at).strip(),
        "notification_id": str(notification_id).strip(),
        "recipient_id": str(recipient_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NDL_{digest[:16].upper()}", digest.upper()


def compute_audit_id(
    notification_id: str,
    event_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "event_type": str(event_type).strip().upper(),
        "notification_id": str(notification_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NAD_{digest[:16].upper()}", digest.upper()


def compute_summary_id(
    total_notifications: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_notifications": int(total_notifications),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NSM_{digest[:16].upper()}", digest.upper()
