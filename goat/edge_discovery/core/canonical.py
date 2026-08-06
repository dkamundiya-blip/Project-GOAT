"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Edge Discovery Subsystem
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
        elif isinstance(val, float):
            return round(val, 8)
        return val

    normalized = _normalize(data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_canonical_sha256(data: Any) -> str:
    """Compute 64-character uppercase SHA-256 hex digest of canonically serialized data."""
    canonical_json = serialize_canonical_json(data)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest().upper()


def compute_edge_candidate_id(
    name: str,
    category: str,
    pattern_ids: list[str],
    symbol: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (candidate_id, canonical_hash) for EdgeCandidate (Prefix: EDC_)."""
    payload = {
        "category": str(category).strip().upper(),
        "name": str(name).strip(),
        "pattern_ids": sorted([str(p).strip() for p in pattern_ids]),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    candidate_id = f"EDC_{digest[:16].upper()}"
    return candidate_id, digest.upper()


def compute_edge_pattern_id(
    pattern_type: str,
    symbol: str,
    sample_size: int,
    statistical_significance: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (pattern_id, canonical_hash) for EdgePattern (Prefix: EPT_)."""
    payload = {
        "pattern_type": str(pattern_type).strip().upper(),
        "sample_size": int(sample_size),
        "statistical_significance": round(float(statistical_significance), 8),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    pattern_id = f"EPT_{digest[:16].upper()}"
    return pattern_id, digest.upper()


def compute_pattern_cluster_id(
    cluster_name: str,
    pattern_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (cluster_id, canonical_hash) for PatternCluster (Prefix: CLS_)."""
    payload = {
        "cluster_name": str(cluster_name).strip(),
        "pattern_ids": sorted([str(p).strip() for p in pattern_ids]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    cluster_id = f"CLS_{digest[:16].upper()}"
    return cluster_id, digest.upper()


def compute_novelty_assessment_id(
    candidate_id: str,
    similarity_score: float,
    status: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (assessment_id, canonical_hash) for NoveltyAssessment (Prefix: NOV_)."""
    payload = {
        "candidate_id": str(candidate_id).strip(),
        "similarity_score": round(float(similarity_score), 8),
        "status": str(status).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"NOV_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_edge_score_id(
    candidate_id: str,
    overall_score: float,
    tier: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (score_id, canonical_hash) for EdgeScore (Prefix: SCR_)."""
    payload = {
        "candidate_id": str(candidate_id).strip(),
        "overall_score": round(float(overall_score), 8),
        "tier": str(tier).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    score_id = f"SCR_{digest[:16].upper()}"
    return score_id, digest.upper()


def compute_discovery_decision_id(
    candidate_id: str,
    status: str,
    reason: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (decision_id, canonical_hash) for DiscoveryDecision (Prefix: DSC_)."""
    payload = {
        "candidate_id": str(candidate_id).strip(),
        "reason": str(reason).strip().upper(),
        "status": str(status).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    decision_id = f"DSC_{digest[:16].upper()}"
    return decision_id, digest.upper()


def compute_discovery_summary_id(
    timestamp: str,
    total_candidates: int,
    total_validated: int,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) for DiscoverySummary (Prefix: DSM_)."""
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_candidates": int(total_candidates),
        "total_validated": int(total_validated),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"DSM_{digest[:16].upper()}"
    return summary_id, digest.upper()
