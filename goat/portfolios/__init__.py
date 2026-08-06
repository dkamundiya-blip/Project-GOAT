"""
Project GOAT v0.7 — Scientific Research Portfolio Engine Package
"""

from goat.portfolios.audit import PortfolioAuditEvent
from goat.portfolios.context import PortfolioContext
from goat.portfolios.coordinator import PortfolioCoordinator, PortfolioValidationError
from goat.portfolios.design import PortfolioDesign, compute_portfolio_design_id
from goat.portfolios.enums import PortfolioStatus
from goat.portfolios.governance import (
    PortfolioGovernancePolicy,
    compute_governance_policy_id,
)
from goat.portfolios.model import (
    ScientificResearchPortfolio,
    compute_portfolio_fingerprint,
    compute_portfolio_id,
)
from goat.portfolios.registry import PortfolioProgramRecord, PortfolioProgramRegistry
from goat.portfolios.reporting import PortfolioReport, generate_portfolio_report
from goat.portfolios.result import PortfolioResult, compute_portfolio_result_id
from goat.portfolios.sqlite import SQLitePortfolioRepository

__all__ = [
    # Enums
    "PortfolioStatus",
    # Domain Models & Identities
    "ScientificResearchPortfolio",
    "compute_portfolio_id",
    "compute_portfolio_fingerprint",
    "PortfolioDesign",
    "compute_portfolio_design_id",
    "PortfolioGovernancePolicy",
    "compute_governance_policy_id",
    "PortfolioProgramRecord",
    "PortfolioProgramRegistry",
    "PortfolioResult",
    "compute_portfolio_result_id",
    "PortfolioContext",
    # Coordinator & Audit
    "PortfolioCoordinator",
    "PortfolioValidationError",
    "PortfolioAuditEvent",
    # Persistence & Reporting
    "SQLitePortfolioRepository",
    "PortfolioReport",
    "generate_portfolio_report",
]
