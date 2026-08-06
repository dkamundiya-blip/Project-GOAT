"""
Project GOAT v0.7 — Scientific Research Portfolio Model

Defines the immutable ScientificResearchPortfolio model (PFO_<HEX16>) representing top-level research portfolio governance.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.portfolios.enums import PortfolioStatus
from goat.research.edge.canonical import compute_canonical_sha256


def compute_portfolio_fingerprint(
    title: str,
    organization: str,
    vision: str,
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Scientific Portfolio Fingerprint (PFFP_<HEX64>).

    Args:
        title: Portfolio title string.
        organization: Organization name string.
        vision: Strategic vision string.
        version: Governance version string.

    Returns:
        String formatted as 'PFFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "organization": str(organization).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
        "vision": str(vision).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PFFP_{digest.upper()}"


def compute_portfolio_id(title: str, fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Scientific Portfolio ID (PFO_<HEX16>) and full SHA-256 canonical hash.

    Args:
        title: Portfolio title.
        fingerprint: Scientific Portfolio Fingerprint (PFFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (portfolio_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    portfolio_id = f"PFO_{digest[:16].upper()}"
    return portfolio_id, digest


class ScientificResearchPortfolio(BaseModel):
    """Immutable master object representing a scientific research portfolio governing multiple research programs."""

    portfolio_id: str = Field(
        ...,
        description="Unique Portfolio ID formatted as PFO_<HEX16>",
        pattern=r"^PFO_[A-Fa-f0-9]{16}$",
    )
    scientific_fingerprint: str = Field(..., description="Scientific Portfolio Fingerprint (PFFP_<HEX64>)")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    portfolio_title: str = Field(..., description="Portfolio title")
    organization_name: str = Field(..., description="Governing organization name")
    portfolio_description: str = Field(..., description="Comprehensive portfolio description")
    strategic_vision: str = Field(..., description="Formal strategic vision statement")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    completion_timestamp: str = Field(default="", description="ISO 8601 UTC completion timestamp")
    portfolio_status: PortfolioStatus = Field(default=PortfolioStatus.PROPOSED, description="Portfolio lifecycle status")
    governance_version: str = Field(default="1.0.0", description="Governance policy version string")
    provenance_metadata: dict[str, Any] = Field(default_factory=dict, description="Scientific provenance annotations")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
