"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Hypothesis Subsystem
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


def compute_hypothesis_id(
    title: str,
    null_hypothesis: str,
    alternative_hypothesis: str,
    author: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (hypothesis_id, canonical_hash) deterministically for ScientificHypothesis.

    Returns:
        Tuple of (HYP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "alternative_hypothesis": str(alternative_hypothesis).strip(),
        "author": str(author).strip(),
        "null_hypothesis": str(null_hypothesis).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    hypothesis_id = f"HYP_{digest[:16].upper()}"
    return hypothesis_id, digest.upper()


def compute_revision_id(
    hypothesis_id: str,
    revision_number: int,
    previous_hash: str = "",
    timestamp: str = "",
) -> tuple[str, str]:
    """Compute (revision_id, canonical_hash) deterministically for HypothesisRevision.

    Returns:
        Tuple of (REV_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "hypothesis_id": str(hypothesis_id).strip(),
        "previous_hash": str(previous_hash).strip(),
        "revision_number": int(revision_number),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    revision_id = f"REV_{digest[:16].upper()}"
    return revision_id, digest.upper()


def compute_validation_id(
    hypothesis_id: str,
    reviewer: str,
    timestamp: str = "",
    is_valid: bool = True,
) -> tuple[str, str]:
    """Compute (validation_id, canonical_hash) deterministically for HypothesisValidation.

    Returns:
        Tuple of (HVL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "hypothesis_id": str(hypothesis_id).strip(),
        "is_valid": bool(is_valid),
        "reviewer": str(reviewer).strip(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    validation_id = f"HVL_{digest[:16].upper()}"
    return validation_id, digest.upper()


def compute_approval_id(
    hypothesis_id: str,
    approver: str,
    status: str,
    timestamp: str = "",
) -> tuple[str, str]:
    """Compute (approval_id, canonical_hash) deterministically for HypothesisApproval.

    Returns:
        Tuple of (HAP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "approver": str(approver).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "status": str(status).strip().upper(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    approval_id = f"HAP_{digest[:16].upper()}"
    return approval_id, digest.upper()


def compute_summary_id(
    total_hypotheses: int,
    timestamp: str = "",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically for HypothesisRegistrySummary.

    Returns:
        Tuple of (HRS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_hypotheses": int(total_hypotheses),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"HRS_{digest[:16].upper()}"
    return summary_id, digest.upper()
