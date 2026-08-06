"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Regimes Engine

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Market Regime and Edge Applicability entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_regime_id(
    regime_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (regime_id, canonical_hash) deterministically for a MarketRegime.

    Returns:
        Tuple of (MRG_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "regime_type": str(regime_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    regime_id = f"MRG_{digest[:16].upper()}"
    return regime_id, digest.upper()


def compute_assessment_id(
    edge_id: str,
    regime_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (assessment_id, canonical_hash) deterministically for ApplicabilityAssessment.

    Returns:
        Tuple of (APA_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "edge_id": str(edge_id).strip(),
        "regime_id": str(regime_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"APA_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_rule_id(
    name: str,
    expected_regime: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (rule_id, canonical_hash) deterministically for RegimeRule.

    Returns:
        Tuple of (RGR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "expected_regime": str(expected_regime).strip().upper(),
        "name": str(name).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    rule_id = f"RGR_{digest[:16].upper()}"
    return rule_id, digest.upper()


def compute_decision_id(
    active_edges: list[str],
    suppressed_edges: list[str],
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (decision_id, canonical_hash) deterministically for ApplicabilityDecision.

    Returns:
        Tuple of (APD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "active_edges": sorted([str(e).strip() for e in active_edges]),
        "suppressed_edges": sorted([str(e).strip() for e in suppressed_edges]),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    decision_id = f"APD_{digest[:16].upper()}"
    return decision_id, digest.upper()


def compute_regime_explanation_id(
    regime_id: str,
    assessment_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (explanation_id, canonical_hash) deterministically for RegimeExplainabilityRecord.

    Returns:
        Tuple of (REX_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "assessment_id": str(assessment_id).strip(),
        "regime_id": str(regime_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    explanation_id = f"REX_{digest[:16].upper()}"
    return explanation_id, digest.upper()


def compute_regime_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (report_id, canonical_hash) deterministically for Regime reports.

    Returns:
        Tuple of (MRR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"MRR_{digest[:16].upper()}"
    return report_id, digest.upper()
