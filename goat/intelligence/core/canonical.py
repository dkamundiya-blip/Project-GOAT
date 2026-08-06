"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Research Intelligence Subsystem
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


def compute_research_insight_id(
    category: str,
    title: str,
    impact: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (insight_id, canonical_hash) for ResearchInsight (Prefix: RIN_)."""
    payload = {
        "category": str(category).strip().upper(),
        "impact": str(impact).strip().upper(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    insight_id = f"RIN_{digest[:16].upper()}"
    return insight_id, digest.upper()


def compute_meta_analysis_id(
    analysis_title: str,
    sample_size: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (meta_analysis_id, canonical_hash) for MetaAnalysis (Prefix: MTA_)."""
    payload = {
        "analysis_title": str(analysis_title).strip(),
        "sample_size": int(sample_size),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    meta_id = f"MTA_{digest[:16].upper()}"
    return meta_id, digest.upper()


def compute_research_trend_id(
    metric_name: str,
    direction: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (trend_id, canonical_hash) for ResearchTrend (Prefix: TRD_)."""
    payload = {
        "direction": str(direction).strip().upper(),
        "metric_name": str(metric_name).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    trend_id = f"TRD_{digest[:16].upper()}"
    return trend_id, digest.upper()


def compute_institutional_recommendation_id(
    priority: str,
    topic: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (recommendation_id, canonical_hash) for InstitutionalRecommendation (Prefix: REC_)."""
    payload = {
        "priority": str(priority).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "topic": str(topic).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    rec_id = f"REC_{digest[:16].upper()}"
    return rec_id, digest.upper()


def compute_research_health_id(
    status: str,
    health_score: float,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (health_id, canonical_hash) for ResearchHealth (Prefix: RHL_)."""
    payload = {
        "health_score": round(float(health_score), 4),
        "status": str(status).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    health_id = f"RHL_{digest[:16].upper()}"
    return health_id, digest.upper()


def compute_intelligence_summary_id(
    timestamp: str,
    total_insights: int,
    total_recommendations: int,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) for IntelligenceSummary (Prefix: ISM_)."""
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_insights": int(total_insights),
        "total_recommendations": int(total_recommendations),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"ISM_{digest[:16].upper()}"
    return summary_id, digest.upper()
