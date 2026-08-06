"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Signal Engine

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Scientific Signal Generation entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_signal_id(
    qualification_id: str,
    simulation_result_id: str,
    risk_assessment_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (signal_id, canonical_hash) deterministically for TradingSignal.

    Returns:
        Tuple of (SIG_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "qualification_id": str(qualification_id).strip(),
        "risk_assessment_id": str(risk_assessment_id).strip(),
        "simulation_result_id": str(simulation_result_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    signal_id = f"SIG_{digest[:16].upper()}"
    return signal_id, digest.upper()


def compute_payload_id(
    signal_id: str,
    payload_format: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (payload_id, canonical_hash) deterministically for SignalPayload.

    Returns:
        Tuple of (SPL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "payload_format": str(payload_format).strip().upper(),
        "signal_id": str(signal_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    payload_id = f"SPL_{digest[:16].upper()}"
    return payload_id, digest.upper()


def compute_lifecycle_event_id(
    signal_id: str,
    previous_state: str,
    current_state: str,
    event_timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (lifecycle_event_id, canonical_hash) deterministically for SignalLifecycleEvent.

    Returns:
        Tuple of (SLE_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "current_state": str(current_state).strip().upper(),
        "event_timestamp": str(event_timestamp).strip(),
        "previous_state": str(previous_state).strip().upper(),
        "signal_id": str(signal_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    event_id = f"SLE_{digest[:16].upper()}"
    return event_id, digest.upper()


def compute_readiness_id(
    signal_id: str,
    execution_status: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (readiness_id, canonical_hash) deterministically for ExecutionReadiness.

    Returns:
        Tuple of (EXR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "execution_status": str(execution_status).strip().upper(),
        "signal_id": str(signal_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    readiness_id = f"EXR_{digest[:16].upper()}"
    return readiness_id, digest.upper()


def compute_signal_audit_id(
    signal_id: str,
    qualification_reference: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (audit_id, canonical_hash) deterministically for SignalAuditRecord.

    Returns:
        Tuple of (SAD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "qualification_reference": str(qualification_reference).strip(),
        "signal_id": str(signal_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    audit_id = f"SAD_{digest[:16].upper()}"
    return audit_id, digest.upper()


def compute_signal_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (report_id, canonical_hash) deterministically for Signal reports.

    Returns:
        Tuple of (SSR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SSR_{digest[:16].upper()}"
    return report_id, digest.upper()
