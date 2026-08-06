"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Broker Abstraction

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- BrokerProfile (BRK_<HEX16>)
- BrokerConnection (BCN_<HEX16>)
- BrokerAccount (BAC_<HEX16>)
- BrokerOrderIntent (BOI_<HEX16>)
- BrokerError (BRE_<HEX16>)
- BrokerReport (BRR_<HEX16>)
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_broker_profile_id(
    broker_name: str,
    broker_type: str,
    api_version: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (broker_id, canonical_hash) for BrokerProfile.

    Returns:
        Tuple of (BRK_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "api_version": str(api_version).strip(),
        "broker_name": str(broker_name).strip().upper(),
        "broker_type": str(broker_type).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    broker_id = f"BRK_{digest[:16].upper()}"
    return broker_id, digest.upper()


def compute_connection_id(
    broker_id: str,
    connected_at: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (connection_id, canonical_hash) for BrokerConnection.

    Returns:
        Tuple of (BCN_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "broker_id": str(broker_id).strip(),
        "connected_at": str(connected_at).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    connection_id = f"BCN_{digest[:16].upper()}"
    return connection_id, digest.upper()


def compute_account_id(
    broker_id: str,
    account_type: str,
    account_currency: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (account_id, canonical_hash) for BrokerAccount.

    Returns:
        Tuple of (BAC_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "account_currency": str(account_currency).strip().upper(),
        "account_type": str(account_type).strip().upper(),
        "broker_id": str(broker_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    account_id = f"BAC_{digest[:16].upper()}"
    return account_id, digest.upper()


def compute_order_intent_id(
    broker_id: str,
    symbol: str,
    side: str,
    quantity: float,
    order_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (intent_id, canonical_hash) for BrokerOrderIntent.

    Returns:
        Tuple of (BOI_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "broker_id": str(broker_id).strip(),
        "order_type": str(order_type).strip().upper(),
        "quantity": round(float(quantity), 6),
        "side": str(side).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    intent_id = f"BOI_{digest[:16].upper()}"
    return intent_id, digest.upper()


def compute_error_id(
    code: str,
    category: str,
    message: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (error_id, canonical_hash) for BrokerError.

    Returns:
        Tuple of (BRE_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "category": str(category).strip().upper(),
        "code": str(code).strip().upper(),
        "message": str(message).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    error_id = f"BRE_{digest[:16].upper()}"
    return error_id, digest.upper()


def compute_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (report_id, canonical_hash) for Broker reports.

    Returns:
        Tuple of (BRR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"BRR_{digest[:16].upper()}"
    return report_id, digest.upper()
