"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Risk Engine

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Scientific Risk Management entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_risk_profile_id(
    qualification_id: str,
    simulation_result_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (risk_profile_id, canonical_hash) deterministically for RiskProfile.

    Returns:
        Tuple of (RPF_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "qualification_id": str(qualification_id).strip(),
        "simulation_result_id": str(simulation_result_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    risk_profile_id = f"RPF_{digest[:16].upper()}"
    return risk_profile_id, digest.upper()


def compute_sizing_id(
    risk_profile_id: str,
    instrument: str,
    entry_price: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (sizing_id, canonical_hash) deterministically for PositionSizingDecision.

    Returns:
        Tuple of (PSD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "risk_profile_id": str(risk_profile_id).strip(),
        "instrument": str(instrument).strip().upper(),
        "entry_price": float(entry_price),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    sizing_id = f"PSD_{digest[:16].upper()}"
    return sizing_id, digest.upper()


def compute_allocation_id(
    qualification_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (allocation_id, canonical_hash) deterministically for CapitalAllocation.

    Returns:
        Tuple of (CAL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "qualification_id": str(qualification_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    allocation_id = f"CAL_{digest[:16].upper()}"
    return allocation_id, digest.upper()


def compute_exposure_id(
    active_positions_count: int,
    portfolio_exposure: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (exposure_id, canonical_hash) deterministically for ExposureAssessment.

    Returns:
        Tuple of (EXP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "active_positions_count": int(active_positions_count),
        "portfolio_exposure": float(portfolio_exposure),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    exposure_id = f"EXP_{digest[:16].upper()}"
    return exposure_id, digest.upper()


def compute_risk_assessment_id(
    sizing_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (assessment_id, canonical_hash) deterministically for RiskAssessment.

    Returns:
        Tuple of (RSA_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "sizing_id": str(sizing_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"RSA_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_risk_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (report_id, canonical_hash) deterministically for Risk reports.

    Returns:
        Tuple of (SRR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SRR_{digest[:16].upper()}"
    return report_id, digest.upper()
