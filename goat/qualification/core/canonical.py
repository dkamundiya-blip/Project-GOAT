"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Qualification Engine

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Scientific Qualification and Decision Readiness entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_qualification_id(
    composite_id: str,
    regime_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (qualification_id, canonical_hash) deterministically for ScientificQualification.

    Returns:
        Tuple of (SQL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "composite_id": str(composite_id).strip(),
        "regime_id": str(regime_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    qualification_id = f"SQL_{digest[:16].upper()}"
    return qualification_id, digest.upper()


def compute_gate_id(
    gate_name: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (gate_id, canonical_hash) deterministically for QualificationGate.

    Returns:
        Tuple of (QGT_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "gate_name": str(gate_name).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    gate_id = f"QGT_{digest[:16].upper()}"
    return gate_id, digest.upper()


def compute_evaluation_id(
    gate_id: str,
    qualification_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (evaluation_id, canonical_hash) deterministically for GateEvaluation.

    Returns:
        Tuple of (GEV_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "gate_id": str(gate_id).strip(),
        "qualification_id": str(qualification_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    evaluation_id = f"GEV_{digest[:16].upper()}"
    return evaluation_id, digest.upper()


def compute_readiness_id(
    qualification_id: str,
    readiness_level: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (readiness_id, canonical_hash) deterministically for DecisionReadiness.

    Returns:
        Tuple of (DCR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "qualification_id": str(qualification_id).strip(),
        "readiness_level": str(readiness_level).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    readiness_id = f"DCR_{digest[:16].upper()}"
    return readiness_id, digest.upper()


def compute_qualification_explanation_id(
    qualification_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (explanation_id, canonical_hash) deterministically for QualificationExplainabilityRecord.

    Returns:
        Tuple of (QEX_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "qualification_id": str(qualification_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    explanation_id = f"QEX_{digest[:16].upper()}"
    return explanation_id, digest.upper()


def compute_qualification_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (report_id, canonical_hash) deterministically for Qualification reports.

    Returns:
        Tuple of (SQR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SQR_{digest[:16].upper()}"
    return report_id, digest.upper()
