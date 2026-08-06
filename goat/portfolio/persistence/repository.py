"""
Project GOAT v0.8 — Portfolio Persistence Repositories

Implements transactional SQLite persistence for:
- PortfolioRepository
- PositionRepository
- ClosedPositionRepository
- ExposureRepository
- PerformanceRepository
- AccountRepository
- AuditRepository
- ReportRepository

Enforces WAL journal mode, foreign key constraints, replayability, and deterministic serialization.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.portfolio.core.models import (
    AccountSnapshot,
    ClosedPosition,
    ExposureSummary,
    PerformanceSummary,
    Portfolio,
    PortfolioAudit,
    PortfolioSnapshot,
    Position,
)

PORTFOLIO_SCHEMA_VERSION = 1


class SQLitePortfolioRepository:
    """Transactional SQLite WAL repository managing all portfolio subsystem data entities."""

    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Initialize database schema with versioning and foreign keys."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS portfolio_schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO portfolio_schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS portfolios (
                    portfolio_id TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    portfolio_name TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    initial_balance REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS positions (
                    position_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    status TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS closed_positions (
                    closed_position_id TEXT PRIMARY KEY,
                    position_id TEXT NOT NULL,
                    portfolio_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    realized_pnl REAL NOT NULL,
                    closed_at TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    equity REAL NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS exposure_summaries (
                    exposure_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    net_exposure REAL NOT NULL,
                    gross_exposure REAL NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS performance_summaries (
                    performance_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    total_pnl REAL NOT NULL,
                    win_rate REAL NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS account_snapshots (
                    account_snapshot_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    account_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    balance REAL NOT NULL,
                    equity REAL NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS portfolio_audits (
                    audit_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS portfolio_reports (
                    report_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );
            """)

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Portfolio Operations
    # ------------------------------------------------------------------

    def save_portfolio(self, portfolio: Portfolio) -> None:
        json_str = portfolio.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO portfolios (
                    portfolio_id, account_id, portfolio_name, currency, initial_balance,
                    created_at, status, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    portfolio.portfolio_id,
                    portfolio.account_id,
                    portfolio.portfolio_name,
                    portfolio.currency,
                    portfolio.initial_balance,
                    portfolio.created_at,
                    portfolio.status.value if hasattr(portfolio.status, "value") else str(portfolio.status),
                    portfolio.canonical_hash,
                    json_str,
                ),
            )

    def get_portfolio(self, portfolio_id: str) -> Portfolio | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM portfolios WHERE portfolio_id = ?",
            (portfolio_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Portfolio.model_validate_json(row["json_data"])

    # ------------------------------------------------------------------
    # Position Operations
    # ------------------------------------------------------------------

    def save_position(self, position: Position) -> None:
        json_str = position.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO positions (
                    position_id, portfolio_id, symbol, side, quantity, entry_price,
                    current_price, status, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    position.position_id,
                    position.portfolio_id,
                    position.symbol,
                    position.side.value if hasattr(position.side, "value") else str(position.side),
                    position.quantity,
                    position.entry_price,
                    position.current_price,
                    position.status.value if hasattr(position.status, "value") else str(position.status),
                    position.canonical_hash,
                    json_str,
                ),
            )

    def get_position(self, position_id: str) -> Position | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM positions WHERE position_id = ?",
            (position_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Position.model_validate_json(row["json_data"])

    def get_open_positions(self, portfolio_id: str) -> list[Position]:
        cursor = self._conn.execute(
            "SELECT json_data FROM positions WHERE portfolio_id = ? AND status != 'CLOSED'",
            (portfolio_id,),
        )
        return [Position.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # ClosedPosition Operations
    # ------------------------------------------------------------------

    def save_closed_position(self, closed_position: ClosedPosition) -> None:
        json_str = closed_position.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO closed_positions (
                    closed_position_id, position_id, portfolio_id, symbol, side,
                    quantity, entry_price, exit_price, realized_pnl, closed_at,
                    canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    closed_position.closed_position_id,
                    closed_position.position_id,
                    closed_position.portfolio_id,
                    closed_position.symbol,
                    closed_position.side.value if hasattr(closed_position.side, "value") else str(closed_position.side),
                    closed_position.quantity,
                    closed_position.entry_price,
                    closed_position.exit_price,
                    closed_position.realized_pnl,
                    closed_position.closed_at,
                    closed_position.canonical_hash,
                    json_str,
                ),
            )

    def get_closed_positions(self, portfolio_id: str) -> list[ClosedPosition]:
        cursor = self._conn.execute(
            "SELECT json_data FROM closed_positions WHERE portfolio_id = ? ORDER BY closed_at ASC",
            (portfolio_id,),
        )
        return [ClosedPosition.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Portfolio Snapshot Operations
    # ------------------------------------------------------------------

    def save_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        json_str = snapshot.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO portfolio_snapshots (
                    snapshot_id, portfolio_id, timestamp, equity, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.portfolio_id,
                    snapshot.timestamp,
                    snapshot.equity,
                    snapshot.canonical_hash,
                    json_str,
                ),
            )

    def get_snapshots(self, portfolio_id: str) -> list[PortfolioSnapshot]:
        cursor = self._conn.execute(
            "SELECT json_data FROM portfolio_snapshots WHERE portfolio_id = ? ORDER BY timestamp ASC",
            (portfolio_id,),
        )
        return [PortfolioSnapshot.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Exposure Operations
    # ------------------------------------------------------------------

    def save_exposure(self, exposure: ExposureSummary) -> None:
        json_str = exposure.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO exposure_summaries (
                    exposure_id, portfolio_id, timestamp, net_exposure, gross_exposure,
                    canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exposure.exposure_id,
                    exposure.portfolio_id,
                    exposure.timestamp,
                    exposure.net_exposure,
                    exposure.gross_exposure,
                    exposure.canonical_hash,
                    json_str,
                ),
            )

    def get_exposures(self, portfolio_id: str) -> list[ExposureSummary]:
        cursor = self._conn.execute(
            "SELECT json_data FROM exposure_summaries WHERE portfolio_id = ? ORDER BY timestamp ASC",
            (portfolio_id,),
        )
        return [ExposureSummary.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Performance Operations
    # ------------------------------------------------------------------

    def save_performance(self, performance: PerformanceSummary) -> None:
        json_str = performance.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO performance_summaries (
                    performance_id, portfolio_id, timestamp, total_pnl, win_rate,
                    canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    performance.performance_id,
                    performance.portfolio_id,
                    performance.timestamp,
                    performance.total_pnl,
                    performance.win_rate,
                    performance.canonical_hash,
                    json_str,
                ),
            )

    def get_performances(self, portfolio_id: str) -> list[PerformanceSummary]:
        cursor = self._conn.execute(
            "SELECT json_data FROM performance_summaries WHERE portfolio_id = ? ORDER BY timestamp ASC",
            (portfolio_id,),
        )
        return [PerformanceSummary.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Account Operations
    # ------------------------------------------------------------------

    def save_account_snapshot(self, account_snapshot: AccountSnapshot) -> None:
        json_str = account_snapshot.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO account_snapshots (
                    account_snapshot_id, portfolio_id, account_id, timestamp, balance,
                    equity, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_snapshot.account_snapshot_id,
                    account_snapshot.portfolio_id,
                    account_snapshot.account_id,
                    account_snapshot.timestamp,
                    account_snapshot.balance,
                    account_snapshot.equity,
                    account_snapshot.canonical_hash,
                    json_str,
                ),
            )

    def get_account_snapshots(self, portfolio_id: str) -> list[AccountSnapshot]:
        cursor = self._conn.execute(
            "SELECT json_data FROM account_snapshots WHERE portfolio_id = ? ORDER BY timestamp ASC",
            (portfolio_id,),
        )
        return [AccountSnapshot.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Audit Operations
    # ------------------------------------------------------------------

    def save_audit(self, audit: PortfolioAudit) -> None:
        json_str = audit.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO portfolio_audits (
                    audit_id, portfolio_id, event_type, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.audit_id,
                    audit.portfolio_id,
                    audit.event_type.value if hasattr(audit.event_type, "value") else str(audit.event_type),
                    audit.timestamp,
                    audit.canonical_hash,
                    json_str,
                ),
            )

    def get_audits(self, portfolio_id: str) -> list[PortfolioAudit]:
        cursor = self._conn.execute(
            "SELECT json_data FROM portfolio_audits WHERE portfolio_id = ? ORDER BY timestamp ASC",
            (portfolio_id,),
        )
        return [PortfolioAudit.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Report Operations
    # ------------------------------------------------------------------

    def save_report(self, report_id: str, portfolio_id: str, report_type: str, timestamp: str, content: str, json_data: dict[str, Any]) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO portfolio_reports (
                    report_id, portfolio_id, report_type, timestamp, content, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    portfolio_id,
                    report_type,
                    timestamp,
                    content,
                    json.dumps(json_data, sort_keys=True),
                ),
            )

    def get_reports(self, portfolio_id: str) -> list[dict[str, Any]]:
        cursor = self._conn.execute(
            "SELECT report_id, portfolio_id, report_type, timestamp, content, json_data FROM portfolio_reports WHERE portfolio_id = ?",
            (portfolio_id,),
        )
        results = []
        for row in cursor.fetchall():
            results.append({
                "report_id": row["report_id"],
                "portfolio_id": row["portfolio_id"],
                "report_type": row["report_type"],
                "timestamp": row["timestamp"],
                "content": row["content"],
                "json_data": json.loads(row["json_data"]),
            })
        return results


# Export individually named repositories pointing to the unified SQLite WAL repository
class PortfolioRepository(SQLitePortfolioRepository):
    pass

class PositionRepository(SQLitePortfolioRepository):
    pass

class ClosedPositionRepository(SQLitePortfolioRepository):
    pass

class ExposureRepository(SQLitePortfolioRepository):
    pass

class PerformanceRepository(SQLitePortfolioRepository):
    pass

class AccountRepository(SQLitePortfolioRepository):
    pass

class AuditRepository(SQLitePortfolioRepository):
    pass

class ReportRepository(SQLitePortfolioRepository):
    pass
