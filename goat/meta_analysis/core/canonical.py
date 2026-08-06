"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Meta-Analysis

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Meta-Analysis entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_cluster_id(
    title: str,
    participating_nodes: list[str],
    cluster_type: str = "THEME",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (cluster_id, canonical_hash) deterministically.

    Returns:
        Tuple of (RCL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "cluster_type": str(cluster_type).strip().upper(),
        "participating_nodes": sorted([str(n).strip() for n in participating_nodes]),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    cluster_id = f"RCL_{digest[:16].upper()}"
    return cluster_id, digest.upper()


def compute_pattern_id(
    pattern_name: str,
    evidence: list[str],
    category: str = "RECURRING_EVIDENCE",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (pattern_id, canonical_hash) deterministically.

    Returns:
        Tuple of (RPT_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "category": str(category).strip().upper(),
        "evidence": sorted([str(e).strip() for e in evidence]),
        "pattern_name": str(pattern_name).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    pattern_id = f"RPT_{digest[:16].upper()}"
    return pattern_id, digest.upper()


def compute_trend_id(
    topic: str,
    direction: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (trend_id, canonical_hash) deterministically.

    Returns:
        Tuple of (RTD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "direction": str(direction).strip().upper(),
        "topic": str(topic).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    trend_id = f"RTD_{digest[:16].upper()}"
    return trend_id, digest.upper()


def compute_summary_id(
    validated_knowledge_count: int,
    integrated_knowledge_count: int,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically.

    Returns:
        Tuple of (SCS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "integrated_knowledge_count": int(integrated_knowledge_count),
        "timestamp": str(timestamp).strip(),
        "validated_knowledge_count": int(validated_knowledge_count),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"SCS_{digest[:16].upper()}"
    return summary_id, digest.upper()


def compute_metrics_id(
    knowledge_density: float,
    evidence_density: float,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (metrics_id, canonical_hash) deterministically.

    Returns:
        Tuple of (RIM_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "evidence_density": float(evidence_density),
        "knowledge_density": float(knowledge_density),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    metrics_id = f"RIM_{digest[:16].upper()}"
    return metrics_id, digest.upper()


def compute_meta_analysis_id(
    analyzed_knowledge_states: list[str],
    cluster_ids: list[str],
    pattern_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (analysis_id, canonical_hash) deterministically.

    Returns:
        Tuple of (MAR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "analyzed_knowledge_states": sorted([str(s).strip() for s in analyzed_knowledge_states]),
        "cluster_ids": sorted([str(c).strip() for c in cluster_ids]),
        "pattern_ids": sorted([str(p).strip() for p in pattern_ids]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    analysis_id = f"MAR_{digest[:16].upper()}"
    return analysis_id, digest.upper()
