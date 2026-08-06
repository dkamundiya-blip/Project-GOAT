"""
Project GOAT v0.8 — Step 7.5 Persistence, Reporting, and Public API Dedicated Tests
"""

import tempfile
from pathlib import Path

import pytest

import goat.portfolio as portfolio_pkg
from goat.portfolio import (
    AccountSnapshot,
    ClosedPosition,
    ExposureSummary,
    PerformanceSummary,
    Portfolio,
    PortfolioAudit,
    PortfolioEngine,
    PortfolioReportEngine,
    PortfolioSnapshot,
    Position,
    SQLitePortfolioRepository,
)


def test_public_api_exports():
    expected_exports = [
        "PortfolioEngine",
        "PositionEngine",
        "AccountEngine",
        "ExposureEngine",
        "PerformanceEngine",
        "PortfolioReconciliationEngine",
        "PortfolioReportEngine",
        "Portfolio",
        "Position",
        "ClosedPosition",
        "PortfolioSnapshot",
        "ExposureSummary",
        "PerformanceSummary",
        "AccountSnapshot",
        "PortfolioAudit",
        "ReconciliationItem",
        "PositionSide",
        "PositionStatus",
        "PortfolioStatus",
        "CloseReason",
        "PortfolioAuditEventType",
        "ReconciliationMismatchType",
        "compute_portfolio_id",
        "compute_position_id",
        "compute_closed_position_id",
        "compute_portfolio_snapshot_id",
        "compute_exposure_summary_id",
        "compute_performance_summary_id",
        "compute_account_snapshot_id",
        "compute_portfolio_audit_id",
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
    for item in expected_exports:
        assert hasattr(portfolio_pkg, item)
    assert set(portfolio_pkg.__all__) == set(expected_exports)


def test_sqlite_persistence_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_portfolio.db"
        engine = PortfolioEngine("Test Portfolio", "BAC_1234567890ABCDEF", initial_balance=10000.0, db_path=db_path)

        pos = engine.process_execution_fill("EURUSD", "LONG", 1.0, 1.0800, "2026-08-01T00:00:00Z")
        engine.update_market_data({"EURUSD": 1.0900}, "2026-08-01T01:00:00Z")
        closed_pos = engine.process_position_close(pos.position_id, 1.0950, "2026-08-01T02:00:00Z")

        # Verify DB records
        repo = SQLitePortfolioRepository(db_path)
        db_ptf = repo.get_portfolio(engine.portfolio.portfolio_id)
        assert db_ptf is not None
        assert db_ptf.portfolio_name == "Test Portfolio"

        db_closed = repo.get_closed_positions(engine.portfolio.portfolio_id)
        assert len(db_closed) == 1
        assert db_closed[0].closed_position_id == closed_pos.closed_position_id

        db_snapshots = repo.get_snapshots(engine.portfolio.portfolio_id)
        assert len(db_snapshots) >= 1

        db_audits = repo.get_audits(engine.portfolio.portfolio_id)
        assert len(db_audits) >= 3
        repo.close()
        engine.close()


def test_portfolio_report_engine():
    engine = PortfolioEngine("Reporting Portfolio", "BAC_1234567890ABCDEF", initial_balance=10000.0)
    pos = engine.process_execution_fill("EURUSD", "LONG", 1.0, 1.0800, "2026-08-01T00:00:00Z")
    engine.update_market_data({"EURUSD": 1.0900}, "2026-08-01T01:00:00Z")

    md, js = engine.generate_executive_report("2026-08-01T01:00:00Z")
    assert "# GOAT Portfolio Executive Report" in md
    assert js["portfolio"]["portfolio_name"] == "Reporting Portfolio"
    assert js["reconciliation_status"] == "RECONCILED"
