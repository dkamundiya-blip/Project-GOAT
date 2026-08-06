"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Scientific Alpha Engine

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Scientific Alpha entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_edge_id(
    title: str,
    originating_hypotheses: list[str],
    originating_validations: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (edge_id, canonical_hash) deterministically for a ScientificEdge.

    Returns:
        Tuple of (SED_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "originating_hypotheses": sorted([str(h).strip() for h in originating_hypotheses]),
        "originating_validations": sorted([str(v).strip() for v in originating_validations]),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    edge_id = f"SED_{digest[:16].upper()}"
    return edge_id, digest.upper()


def compute_evidence_id(
    edge_id: str,
    source_reference: str,
    source_type: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (evidence_id, canonical_hash) deterministically for EdgeEvidence.

    Returns:
        Tuple of (EEV_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "edge_id": str(edge_id).strip(),
        "source_reference": str(source_reference).strip(),
        "source_type": str(source_type).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    evidence_id = f"EEV_{digest[:16].upper()}"
    return evidence_id, digest.upper()


def compute_score_id(
    edge_id: str,
    overall_edge_score: float,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (score_id, canonical_hash) deterministically for EdgeScore.

    Returns:
        Tuple of (ESC_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "edge_id": str(edge_id).strip(),
        "overall_edge_score": float(overall_edge_score),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    score_id = f"ESC_{digest[:16].upper()}"
    return score_id, digest.upper()


def compute_ranking_id(
    ranked_edges: list[str],
    ranking_timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (ranking_id, canonical_hash) deterministically for EdgeRanking.

    Returns:
        Tuple of (ERK_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "ranked_edges": [str(e).strip() for e in ranked_edges],  # Preserve rank order
        "ranking_timestamp": str(ranking_timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    ranking_id = f"ERK_{digest[:16].upper()}"
    return ranking_id, digest.upper()


def compute_explanation_id(
    edge_id: str,
    origin: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (explanation_id, canonical_hash) deterministically for EdgeExplainabilityRecord.

    Returns:
        Tuple of (EEX_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "edge_id": str(edge_id).strip(),
        "origin": str(origin).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    explanation_id = f"EEX_{digest[:16].upper()}"
    return explanation_id, digest.upper()


def compute_alpha_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (report_id, canonical_hash) deterministically for Alpha reports.

    Returns:
        Tuple of (SAR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SAR_{digest[:16].upper()}"
    return report_id, digest.upper()
