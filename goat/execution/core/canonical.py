"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Execution Engine

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- ExecutionIntent (EXI_<HEX16>)
- ExecutionRequest (EXR_<HEX16>)
- ExecutionDecision (EXD_<HEX16>)
- ExecutionLifecycle (EXL_<HEX16>)
- ExecutionAudit (EXA_<HEX16>)
- ExecutionFailure (EXF_<HEX16>)
- ExecutionSummary (EXS_<HEX16>)
- ExecutionReport (EXM_<HEX16>)
"""

from goat.research.edge.canonical import compute_canonical_sha256


def compute_execution_intent_id(
    signal_id: str,
    broker_id: str,
    symbol: str,
    side: str,
    quantity: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "broker_id": str(broker_id).strip(),
        "quantity": round(float(quantity), 6),
        "side": str(side).strip().upper(),
        "signal_id": str(signal_id).strip(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXI_{digest[:16].upper()}", digest.upper()


def compute_execution_request_id(intent_id: str, broker_id: str, timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {
        "broker_id": str(broker_id).strip(),
        "intent_id": str(intent_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXR_{digest[:16].upper()}", digest.upper()


def compute_execution_decision_id(intent_id: str, approved: bool, timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {
        "approved": bool(approved),
        "intent_id": str(intent_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXD_{digest[:16].upper()}", digest.upper()


def compute_execution_lifecycle_id(intent_id: str, state: str, transition_timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {
        "intent_id": str(intent_id).strip(),
        "state": str(state).strip().upper(),
        "transition_timestamp": str(transition_timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXL_{digest[:16].upper()}", digest.upper()


def compute_execution_audit_id(intent_id: str, event_type: str, timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {
        "event_type": str(event_type).strip().upper(),
        "intent_id": str(intent_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXA_{digest[:16].upper()}", digest.upper()


def compute_execution_failure_id(intent_id: str, category: str, error_code: str, timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {
        "category": str(category).strip().upper(),
        "error_code": str(error_code).strip().upper(),
        "intent_id": str(intent_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXF_{digest[:16].upper()}", digest.upper()


def compute_execution_summary_id(total_intents: int, timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_intents": int(total_intents),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXS_{digest[:16].upper()}", digest.upper()


def compute_execution_report_id(report_type: str, timestamp: str, version: str = "1.0.0") -> tuple[str, str]:
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXM_{digest[:16].upper()}", digest.upper()
