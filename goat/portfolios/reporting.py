"""
Project GOAT v0.7 — Portfolio Reporting Module

Implements immutable PortfolioReport summarizing research portfolio execution, governance policies, program statistics, and audit logs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.portfolios.design import PortfolioDesign
from goat.portfolios.governance import PortfolioGovernancePolicy
from goat.portfolios.model import ScientificResearchPortfolio
from goat.portfolios.result import PortfolioResult
from goat.research.edge.canonical import compute_canonical_sha256


class PortfolioReport(BaseModel):
    """Immutable report summarizing scientific research portfolio execution and audit findings."""

    report_id: str = Field(..., description="Unique Portfolio Report ID (PREP_<HEX16>)")
    portfolio_id: str = Field(..., description="Parent Portfolio ID (PFO_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    final_status: str = Field(..., description="Final PortfolioStatus string")
    design_summary: dict[str, Any] = Field(default_factory=dict, description="Portfolio design summary")
    governance_summary: dict[str, Any] = Field(default_factory=dict, description="Governance policy summary")
    program_statistics: dict[str, Any] = Field(default_factory=dict, description="Program counts and statistics")
    study_statistics: dict[str, Any] = Field(default_factory=dict, description="Study counts")
    experiment_statistics: dict[str, Any] = Field(default_factory=dict, description="Experiment counts")
    evidence_statistics: dict[str, Any] = Field(default_factory=dict, description="Evidence references count")
    knowledge_statistics: dict[str, Any] = Field(default_factory=dict, description="Knowledge references count")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit log event statistics")
    execution_timeline: list[str] = Field(default_factory=list, description="Execution timeline milestones")

    class Config:
        frozen = True
        extra = "forbid"


def generate_portfolio_report(
    portfolio: ScientificResearchPortfolio,
    design: PortfolioDesign | None = None,
    governance_policy: PortfolioGovernancePolicy | None = None,
    result: PortfolioResult | None = None,
    audit_events: list[Any] | None = None,
    timestamp: str = "",
) -> PortfolioReport:
    """Generate deterministic PortfolioReport.

    Args:
        portfolio: ScientificResearchPortfolio instance.
        design: Optional PortfolioDesign instance.
        governance_policy: Optional PortfolioGovernancePolicy instance.
        result: Optional PortfolioResult instance.
        audit_events: Optional list of PortfolioAuditEvents.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable PortfolioReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    payload = {
        "portfolio_id": portfolio.portfolio_id,
        "status": portfolio.portfolio_status.value,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"PREP_{digest[:16].upper()}"

    des_summary = {
        "roadmap": design.strategic_roadmap if design else "",
        "version": design.design_version if design else "",
    }

    gov_summary = {
        "cadence": governance_policy.review_cadence if governance_policy else "quarterly",
        "policy_id": governance_policy.policy_id if governance_policy else "",
    }

    prg_count = len(result.program_references) if result else 0
    std_count = len(result.study_references) if result else 0
    exp_count = len(result.experiment_references) if result else 0
    evd_count = len(result.evidence_references) if result else 0
    knw_count = len(result.knowledge_references) if result else 0

    timeline = [
        f"Created research portfolio '{portfolio.portfolio_title}' at {portfolio.creation_timestamp}.",
        f"Organization: {portfolio.organization_name}.",
        f"Status: {portfolio.portfolio_status.value}.",
    ]
    if result:
        timeline.append(f"Completed research portfolio with {prg_count} programs at {result.completion_timestamp}.")

    return PortfolioReport(
        report_id=report_id,
        portfolio_id=portfolio.portfolio_id,
        timestamp=ts,
        final_status=portfolio.portfolio_status.value,
        design_summary=des_summary,
        governance_summary=gov_summary,
        program_statistics={"total_executed_programs": prg_count},
        study_statistics={"total_executed_studies": std_count},
        experiment_statistics={"total_executed_experiments": exp_count},
        evidence_statistics={"total_evidence_references": evd_count},
        knowledge_statistics={"total_knowledge_references": knw_count},
        audit_summary={"total_audit_events": len(audit_events or [])},
        execution_timeline=timeline,
    )
