"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Lifecycle Engine

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- TradeLifecycle (TRL_<HEX16>)
- TradeState (TST_<HEX16>)
- TradeEvent (TEV_<HEX16>)
- BrokerExecution (BEX_<HEX16>)
- PositionSnapshot (PSP_<HEX16>)
- LifecycleTransition (LTR_<HEX16>)
- LifecycleAudit (LAD_<HEX16>)
- LifecycleSummary (LSM_<HEX16>)
"""

from goat.research.edge.canonical import compute_canonical_sha256


def compute_trade_lifecycle_id(
    intent_id: str,
    symbol: str,
    side: str,
    created_at: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "created_at": str(created_at).strip(),
        "intent_id": str(intent_id).strip(),
        "side": str(side).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"TRL_{digest[:16].upper()}", digest.upper()


def compute_trade_state_id(
    lifecycle_id: str,
    state: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "lifecycle_id": str(lifecycle_id).strip(),
        "state": str(state).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"TST_{digest[:16].upper()}", digest.upper()


def compute_trade_event_id(
    lifecycle_id: str,
    event_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "event_type": str(event_type).strip().upper(),
        "lifecycle_id": str(lifecycle_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"TEV_{digest[:16].upper()}", digest.upper()


def compute_broker_execution_id(
    intent_id: str,
    broker_order_id: str,
    fill_price: float,
    fill_quantity: float,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "broker_order_id": str(broker_order_id).strip(),
        "fill_price": round(float(fill_price), 6),
        "fill_quantity": round(float(fill_quantity), 6),
        "intent_id": str(intent_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"BEX_{digest[:16].upper()}", digest.upper()


def compute_position_snapshot_id(
    position_id: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "position_id": str(position_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PSP_{digest[:16].upper()}", digest.upper()


def compute_lifecycle_transition_id(
    lifecycle_id: str,
    from_state: str,
    to_state: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "from_state": str(from_state).strip().upper(),
        "lifecycle_id": str(lifecycle_id).strip(),
        "timestamp": str(timestamp).strip(),
        "to_state": str(to_state).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"LTR_{digest[:16].upper()}", digest.upper()


def compute_lifecycle_audit_id(
    lifecycle_id: str,
    event_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "event_type": str(event_type).strip().upper(),
        "lifecycle_id": str(lifecycle_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"LAD_{digest[:16].upper()}", digest.upper()


def compute_lifecycle_summary_id(
    total_trades: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_trades": int(total_trades),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"LSM_{digest[:16].upper()}", digest.upper()
