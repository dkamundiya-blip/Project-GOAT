"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Live Validation Subsystem
"""

import hashlib
import json
from typing import Any


def serialize_canonical_json(data: Any) -> str:
    """Recursively convert arbitrary structure into canonical JSON string with sorted keys.

    Args:
        data: Structure to serialize (dict, list, tuple, set, Enum, primitive, Pydantic model).

    Returns:
        Canonical JSON string formatted with sorted keys and tight separators.
    """
    def _normalize(val: Any) -> Any:
        if isinstance(val, dict):
            return {str(k): _normalize(v) for k, v in sorted(val.items(), key=lambda x: str(x[0]))}
        elif isinstance(val, (list, tuple, set)):
            return [_normalize(item) for item in val]
        elif hasattr(val, "value"):  # Enum support
            return str(val.value)
        elif hasattr(val, "model_dump"):  # Pydantic v2 support
            return _normalize(val.model_dump())
        elif hasattr(val, "dict"):  # Pydantic v1 fallback
            return _normalize(val.dict())
        return val

    normalized = _normalize(data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_canonical_sha256(data: Any) -> str:
    """Compute 64-character uppercase SHA-256 hex digest of canonically serialized data."""
    canonical_json = serialize_canonical_json(data)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest().upper()


def compute_candidate_id(
    hypothesis_id: str,
    evaluation_id: str,
    experiment_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (candidate_id, canonical_hash) deterministically for LiveValidationCandidate.

    Returns:
        Tuple of (LVC_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "evaluation_id": str(evaluation_id).strip(),
        "experiment_id": str(experiment_id).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    candidate_id = f"LVC_{digest[:16].upper()}"
    return candidate_id, digest.upper()


def compute_session_id(
    candidate_id: str,
    start_timestamp: str,
    operator: str = "LIVE_VALIDATION_ENGINE",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (session_id, canonical_hash) deterministically for ValidationSession.

    Returns:
        Tuple of (VSN_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "candidate_id": str(candidate_id).strip(),
        "operator": str(operator).strip(),
        "start_timestamp": str(start_timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    session_id = f"VSN_{digest[:16].upper()}"
    return session_id, digest.upper()


def compute_observation_id(
    session_id: str,
    timestamp: str,
    live_outcome: float,
    expected_outcome: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (observation_id, canonical_hash) deterministically for ValidationObservation.

    Returns:
        Tuple of (VOB_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "expected_outcome": float(expected_outcome),
        "live_outcome": float(live_outcome),
        "session_id": str(session_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    observation_id = f"VOB_{digest[:16].upper()}"
    return observation_id, digest.upper()


def compute_validation_decision_id(
    session_id: str,
    candidate_id: str,
    decision: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (decision_id, canonical_hash) deterministically for ValidationDecision.

    Returns:
        Tuple of (VDC_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "candidate_id": str(candidate_id).strip(),
        "decision": str(decision).strip().upper(),
        "session_id": str(session_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    decision_id = f"VDC_{digest[:16].upper()}"
    return decision_id, digest.upper()


def compute_summary_id(
    total_candidates: int,
    total_sessions: int,
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically for ValidationSummary.

    Returns:
        Tuple of (VSM_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_candidates": int(total_candidates),
        "total_sessions": int(total_sessions),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"VSM_{digest[:16].upper()}"
    return summary_id, digest.upper()


def compute_audit_id(
    session_id: str,
    action: str,
    timestamp: str,
    operator: str = "SYSTEM",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (audit_id, canonical_hash) deterministically for ValidationAudit.

    Returns:
        Tuple of (VAU_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "action": str(action).strip().upper(),
        "operator": str(operator).strip(),
        "session_id": str(session_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    audit_id = f"VAU_{digest[:16].upper()}"
    return audit_id, digest.upper()
