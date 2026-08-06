"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Deriv Adapter

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- DerivSession (DRS_<HEX16>)
- DerivAuthentication (DAT_<HEX16>)
- DerivAccountSnapshot (DAC_<HEX16>)
- DerivMarketSubscription (DMS_<HEX16>)
- DerivOrderPayload (DOP_<HEX16>)
- DerivExecutionResponse (DER_<HEX16>)
- DerivHeartbeat (DHB_<HEX16>)
- DerivReport (DRR_<HEX16>)
"""

from goat.research.edge.canonical import compute_canonical_sha256


def compute_deriv_session_id(broker_id: str, server_time: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"broker_id": str(broker_id).strip(), "server_time": str(server_time).strip(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DRS_{digest[:16].upper()}", digest.upper()


def compute_deriv_auth_id(app_id: int, user_id: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"app_id": int(app_id), "user_id": str(user_id).strip(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DAT_{digest[:16].upper()}", digest.upper()


def compute_deriv_account_snapshot_id(login_id: str, currency: str, balance: float, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"balance": round(float(balance), 2), "currency": str(currency).strip().upper(), "login_id": str(login_id).strip(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DAC_{digest[:16].upper()}", digest.upper()


def compute_deriv_subscription_id(symbol: str, request_id: int, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"request_id": int(request_id), "symbol": str(symbol).strip().upper(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DMS_{digest[:16].upper()}", digest.upper()


def compute_deriv_order_payload_id(intent_id: str, symbol: str, amount: float, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"amount": round(float(amount), 2), "intent_id": str(intent_id).strip(), "symbol": str(symbol).strip().upper(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DOP_{digest[:16].upper()}", digest.upper()


def compute_deriv_execution_id(contract_id: str, buy_price: float, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"buy_price": round(float(buy_price), 2), "contract_id": str(contract_id).strip(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DER_{digest[:16].upper()}", digest.upper()


def compute_deriv_heartbeat_id(ping_timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"ping_timestamp": str(ping_timestamp).strip(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DHB_{digest[:16].upper()}", digest.upper()


def compute_deriv_report_id(report_type: str, timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {"report_type": str(report_type).strip().upper(), "timestamp": str(timestamp).strip(), "version": str(version).strip()}
    digest = compute_canonical_sha256(payload)
    return f"DRR_{digest[:16].upper()}", digest.upper()
