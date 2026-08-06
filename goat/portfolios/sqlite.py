"""
Project GOAT v0.7 — SQLite Portfolio Repository

Implements transactional SQLite persistence for Portfolios, Portfolio Designs, Governance Policies, Results, Contexts, Program Registries, and Audit history.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.portfolios.audit import PortfolioAuditEvent
from goat.portfolios.context import PortfolioContext
from goat.portfolios.design import PortfolioDesign
from goat.portfolios.governance import PortfolioGovernancePolicy
from goat.portfolios.model import ScientificResearchPortfolio
from goat.portfolios.registry import PortfolioProgramRecord
from goat.portfolios.result import PortfolioResult


class SQLitePortfolioRepository:
    """Transactional SQLite repository for scientific research portfolio persistence."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Enforce Schema v1 tables."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    portfolio_id TEXT PRIMARY KEY,
                    scientific_fingerprint TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    portfolio_title TEXT NOT NULL,
                    portfolio_status TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS portfolio_designs (
                    design_id TEXT PRIMARY KEY,
                    design_version TEXT NOT NULL,
                    strategic_roadmap TEXT NOT NULL,
                    design_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS governance_policies (
                    policy_id TEXT PRIMARY KEY,
                    review_cadence TEXT NOT NULL,
                    policy_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS portfolio_results (
                    result_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    completion_timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS portfolio_contexts (
                    portfolio_id TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS program_registry (
                    program_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    execution_order INTEGER NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS portfolio_audit (
                    event_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
                );
            """)

    def save_portfolio(self, portfolio: ScientificResearchPortfolio) -> None:
        """Persist a ScientificResearchPortfolio transactionally."""
        json_str = portfolio.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO portfolios (
                    portfolio_id, scientific_fingerprint, canonical_hash, semantic_version, portfolio_title, portfolio_status, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(portfolio_id) DO UPDATE SET portfolio_status = excluded.portfolio_status, json_data = excluded.json_data;
                """,
                (
                    portfolio.portfolio_id,
                    portfolio.scientific_fingerprint,
                    portfolio.canonical_hash,
                    portfolio.semantic_version,
                    portfolio.portfolio_title,
                    portfolio.portfolio_status.value,
                    json_str,
                ),
            )

    def get_portfolio(self, portfolio_id: str) -> ScientificResearchPortfolio | None:
        """Retrieve ScientificResearchPortfolio by Portfolio ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM portfolios WHERE portfolio_id = ?;", (portfolio_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificResearchPortfolio(**json.loads(row["json_data"]))

    def save_design(self, design: PortfolioDesign) -> None:
        """Persist a PortfolioDesign."""
        json_str = design.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO portfolio_designs (design_id, design_version, strategic_roadmap, design_hash, json_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(design_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (design.design_id, design.design_version, design.strategic_roadmap, design.design_hash, json_str),
            )

    def get_design(self, design_id: str) -> PortfolioDesign | None:
        """Retrieve PortfolioDesign."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM portfolio_designs WHERE design_id = ?;", (design_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return PortfolioDesign(**json.loads(row["json_data"]))

    def save_governance_policy(self, policy: PortfolioGovernancePolicy) -> None:
        """Persist a PortfolioGovernancePolicy."""
        json_str = policy.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO governance_policies (policy_id, review_cadence, policy_hash, json_data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(policy_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (policy.policy_id, policy.review_cadence, policy.policy_hash, json_str),
            )

    def get_governance_policy(self, policy_id: str) -> PortfolioGovernancePolicy | None:
        """Retrieve PortfolioGovernancePolicy."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM governance_policies WHERE policy_id = ?;", (policy_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return PortfolioGovernancePolicy(**json.loads(row["json_data"]))

    def save_program_record(self, record: PortfolioProgramRecord) -> None:
        """Persist a PortfolioProgramRecord."""
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO program_registry (program_id, portfolio_id, execution_order, json_data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(program_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (record.program_id, record.portfolio_id, record.execution_order, json_str),
            )

    def get_portfolio_programs(self, portfolio_id: str) -> list[PortfolioProgramRecord]:
        """Retrieve all registered program records for a portfolio."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM program_registry WHERE portfolio_id = ? ORDER BY execution_order ASC;", (portfolio_id,))
        rows = cursor.fetchall()
        return [PortfolioProgramRecord(**json.loads(r["json_data"])) for r in rows]

    def save_result(self, result: PortfolioResult) -> None:
        """Persist a PortfolioResult."""
        json_str = result.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO portfolio_results (result_id, portfolio_id, completion_timestamp, canonical_hash, json_data)
                VALUES (?, ?, ?, ?, ?);
                """,
                (result.result_id, result.portfolio_id, result.completion_timestamp, result.canonical_hash, json_str),
            )

    def get_result(self, result_id: str) -> PortfolioResult | None:
        """Retrieve PortfolioResult."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM portfolio_results WHERE result_id = ?;", (result_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return PortfolioResult(**json.loads(row["json_data"]))

    def log_audit_event(self, event: PortfolioAuditEvent) -> None:
        """Log audit event."""
        json_str = event.model_dump_json()
        with self._conn:
            self._conn.execute(
                "INSERT INTO portfolio_audit (event_id, portfolio_id, event_type, timestamp, json_data) VALUES (?, ?, ?, ?, ?);",
                (event.event_id, event.portfolio_id, event.event_type, event.timestamp, json_str),
            )

    def get_audit_trail(self, portfolio_id: str) -> list[PortfolioAuditEvent]:
        """Retrieve audit trail for a portfolio."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM portfolio_audit WHERE portfolio_id = ? ORDER BY timestamp ASC;", (portfolio_id,))
        rows = cursor.fetchall()
        return [PortfolioAuditEvent(**json.loads(r["json_data"])) for r in rows]

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
