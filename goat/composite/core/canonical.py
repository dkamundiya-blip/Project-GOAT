"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Composite Engine

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Composite Edge entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_composite_id(
    participating_edges: list[str],
    title: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (composite_id, canonical_hash) deterministically for a CompositeEdge.

    Returns:
        Tuple of (CMP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "participating_edges": sorted([str(e).strip() for e in participating_edges]),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    composite_id = f"CMP_{digest[:16].upper()}"
    return composite_id, digest.upper()


def compute_composite_evidence_id(
    composite_id: str,
    contributing_edge: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (evidence_id, canonical_hash) deterministically for CompositeEvidence.

    Returns:
        Tuple of (CEV_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "composite_id": str(composite_id).strip(),
        "contributing_edge": str(contributing_edge).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    evidence_id = f"CEV_{digest[:16].upper()}"
    return evidence_id, digest.upper()


def compute_composite_score_id(
    composite_id: str,
    overall_score: float,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (score_id, canonical_hash) deterministically for CompositeScore.

    Returns:
        Tuple of (CSC_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "composite_id": str(composite_id).strip(),
        "overall_score": float(overall_score),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    score_id = f"CSC_{digest[:16].upper()}"
    return score_id, digest.upper()


def compute_composite_ranking_id(
    ranked_composites: list[str],
    ranking_timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (ranking_id, canonical_hash) deterministically for CompositeRanking.

    Returns:
        Tuple of (CRK_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "ranked_composites": [str(c).strip() for c in ranked_composites],  # Preserve rank order
        "ranking_timestamp": str(ranking_timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    ranking_id = f"CRK_{digest[:16].upper()}"
    return ranking_id, digest.upper()


def compute_composite_explanation_id(
    composite_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (explanation_id, canonical_hash) deterministically for CompositeExplainabilityRecord.

    Returns:
        Tuple of (CEX_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "composite_id": str(composite_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    explanation_id = f"CEX_{digest[:16].upper()}"
    return explanation_id, digest.upper()


def compute_composite_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (report_id, canonical_hash) deterministically for Composite reports.

    Returns:
        Tuple of (CAR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"CAR_{digest[:16].upper()}"
    return report_id, digest.upper()
