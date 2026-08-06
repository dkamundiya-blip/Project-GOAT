"""
Project GOAT v0.8 — Portfolio & Position Management Engine

Export all public objects via __all__. No namespace leakage.
"""

from goat.portfolio.account.engine import AccountEngine
from goat.portfolio.core.canonical import (
    compute_account_snapshot_id,
    compute_closed_position_id,
    compute_exposure_summary_id,
    compute_performance_summary_id,
    compute_portfolio_audit_id,
    compute_portfolio_id,
    compute_portfolio_snapshot_id,
    compute_position_id,
)
from goat.portfolio.core.enums import (
    CloseReason,
    PortfolioAuditEventType,
    PortfolioStatus,
    PositionSide,
    PositionStatus,
    ReconciliationMismatchType,
)
from goat.portfolio.core.models import (
    AccountSnapshot,
    ClosedPosition,
    ExposureSummary,
    PerformanceSummary,
    Portfolio,
    PortfolioAudit,
    PortfolioSnapshot,
    Position,
    ReconciliationItem,
)
from goat.portfolio.engine import PortfolioEngine
from goat.portfolio.exposure.engine import ExposureEngine
from goat.portfolio.performance.engine import PerformanceEngine
from goat.portfolio.persistence.repository import (
    AccountRepository,
    AuditRepository,
    ClosedPositionRepository,
    ExposureRepository,
    PerformanceRepository,
    PortfolioRepository,
    PositionRepository,
    ReportRepository,
    SQLitePortfolioRepository,
)
from goat.portfolio.positions.engine import PositionEngine
from goat.portfolio.reconciliation.engine import PortfolioReconciliationEngine
from goat.portfolio.reporting.reports import PortfolioReportEngine

__all__ = [
    # Master Engine
    "PortfolioEngine",
    # Subsystem Engines
    "PositionEngine",
    "AccountEngine",
    "ExposureEngine",
    "PerformanceEngine",
    "PortfolioReconciliationEngine",
    "PortfolioReportEngine",
    # Domain Models
    "Portfolio",
    "Position",
    "ClosedPosition",
    "PortfolioSnapshot",
    "ExposureSummary",
    "PerformanceSummary",
    "AccountSnapshot",
    "PortfolioAudit",
    "ReconciliationItem",
    # Enums
    "PositionSide",
    "PositionStatus",
    "PortfolioStatus",
    "CloseReason",
    "PortfolioAuditEventType",
    "ReconciliationMismatchType",
    # Canonical SHA-256 Generators
    "compute_portfolio_id",
    "compute_position_id",
    "compute_closed_position_id",
    "compute_portfolio_snapshot_id",
    "compute_exposure_summary_id",
    "compute_performance_summary_id",
    "compute_account_snapshot_id",
    "compute_portfolio_audit_id",
    # SQLite Repositories
    "SQLitePortfolioRepository",
    "PortfolioRepository",
    "PositionRepository",
    "ClosedPositionRepository",
    "ExposureRepository",
    "PerformanceRepository",
    "AccountRepository",
    "AuditRepository",
    "ReportRepository",
]
