"""
Project GOAT v0.7 — Portfolio Governance Policy Model

Defines the immutable PortfolioGovernancePolicy model (GOV_<HEX16>) specifying approval workflows and compliance metadata.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_governance_policy_id(name: str, review_cadence: str = "quarterly") -> tuple[str, str]:
    """Compute deterministic Governance Policy ID (GOV_<HEX16>) and full SHA-256 policy hash.

    Args:
        name: Governance policy name.
        review_cadence: Review cadence string.

    Returns:
        Tuple of (policy_id, policy_hash).
    """
    payload = {
        "cadence": str(review_cadence).strip(),
        "name": str(name).strip(),
    }
    digest = compute_canonical_sha256(payload)
    policy_id = f"GOV_{digest[:16].upper()}"
    return policy_id, digest


class PortfolioGovernancePolicy(BaseModel):
    """Immutable scientific governance policy specifying approval rules, review cadence, and audit rules."""

    policy_id: str = Field(
        ...,
        description="Unique Governance Policy ID formatted as GOV_<HEX16>",
        pattern=r"^GOV_[A-Fa-f0-9]{16}$",
    )
    approval_workflow: str = Field(default="peer_review_consensus", description="Approval workflow specification")
    review_cadence: str = Field(default="quarterly", description="Review cadence classification")
    archival_rules: dict[str, Any] = Field(default_factory=dict, description="Archival policy rules")
    dependency_rules: dict[str, Any] = Field(default_factory=dict, description="Dependency governance rules")
    audit_policy: dict[str, Any] = Field(default_factory=dict, description="Audit logging policy rules")
    compliance_metadata: dict[str, Any] = Field(default_factory=dict, description="Compliance and regulatory metadata")
    policy_hash: str = Field(..., description="Full 64-character SHA-256 canonical policy hash digest")

    class Config:
        frozen = True
        extra = "forbid"
