"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Governance Subsystem
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


def compute_edge_id(
    hypothesis_id: str,
    title: str,
    author: str = "QUANT_RESEARCH",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (edge_id, canonical_hash) deterministically for EdgeCandidate.

    Returns:
        Tuple of (EDG_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "author": str(author).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    edge_id = f"EDG_{digest[:16].upper()}"
    return edge_id, digest.upper()


def compute_promotion_assessment_id(
    edge_id: str,
    hypothesis_id: str,
    evaluator: str = "PROMOTION_ENGINE",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (assessment_id, canonical_hash) deterministically for PromotionAssessment.

    Returns:
        Tuple of (PRA_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "edge_id": str(edge_id).strip(),
        "evaluator": str(evaluator).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"PRA_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_retirement_assessment_id(
    edge_id: str,
    hypothesis_id: str,
    evaluator: str = "RETIREMENT_ENGINE",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (assessment_id, canonical_hash) deterministically for RetirementAssessment.

    Returns:
        Tuple of (RTA_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "edge_id": str(edge_id).strip(),
        "evaluator": str(evaluator).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"RTA_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_governance_decision_id(
    edge_id: str,
    decision: str,
    reason: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (decision_id, canonical_hash) deterministically for GovernanceDecision.

    Returns:
        Tuple of (GOV_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "decision": str(decision).strip().upper(),
        "edge_id": str(edge_id).strip(),
        "reason": str(reason).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    decision_id = f"GOV_{digest[:16].upper()}"
    return decision_id, digest.upper()


def compute_governance_audit_id(
    decision_id: str,
    action: str,
    timestamp: str,
    operator: str = "GOVERNANCE_BOARD",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (audit_id, canonical_hash) deterministically for GovernanceAudit.

    Returns:
        Tuple of (AUD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "action": str(action).strip().upper(),
        "decision_id": str(decision_id).strip(),
        "operator": str(operator).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    audit_id = f"AUD_{digest[:16].upper()}"
    return audit_id, digest.upper()


def compute_summary_id(
    total_edges: int,
    total_decisions: int,
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically for GovernanceSummary.

    Returns:
        Tuple of (GSM_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_decisions": int(total_decisions),
        "total_edges": int(total_edges),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"GSM_{digest[:16].upper()}"
    return summary_id, digest.upper()
