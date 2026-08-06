"""
Project GOAT v0.7 — SQLite Persistence for Scientific Risk Management Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- RiskProfileRepository
- PositionSizingRepository
- CapitalAllocationRepository
- ExposureRepository
- RiskAssessmentRepository
- RiskReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.risk.core.models import (
    CapitalAllocation,
    ExposureAssessment,
    PositionSizingDecision,
    RiskAssessment,
    RiskProfile,
)


def init_risk_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for Scientific Risk Management Engine."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_profiles (
                risk_profile_id TEXT PRIMARY KEY,
                qualification_id TEXT NOT NULL,
                simulation_result_id TEXT NOT NULL,
                account_currency TEXT NOT NULL,
                account_balance REAL NOT NULL,
                maximum_risk_percent REAL NOT NULL,
                maximum_portfolio_exposure REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS position_sizing_decisions (
                sizing_id TEXT PRIMARY KEY,
                risk_profile_id TEXT NOT NULL,
                instrument TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss_price REAL NOT NULL,
                take_profit_price REAL NOT NULL,
                stop_distance REAL NOT NULL,
                reward_distance REAL NOT NULL,
                risk_reward_ratio REAL NOT NULL,
                position_size REAL NOT NULL,
                minimum_lot_size REAL NOT NULL,
                recommended_lot_size REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (risk_profile_id) REFERENCES risk_profiles(risk_profile_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS capital_allocations (
                allocation_id TEXT PRIMARY KEY,
                qualification_id TEXT NOT NULL,
                allocated_capital REAL NOT NULL,
                available_capital REAL NOT NULL,
                reserved_capital REAL NOT NULL,
                utilization_percent REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exposure_assessments (
                exposure_id TEXT PRIMARY KEY,
                active_positions_json TEXT NOT NULL,
                portfolio_exposure REAL NOT NULL,
                instrument_exposure REAL NOT NULL,
                correlated_exposure REAL NOT NULL,
                exposure_status TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_assessments (
                assessment_id TEXT PRIMARY KEY,
                sizing_id TEXT NOT NULL,
                total_risk REAL NOT NULL,
                monetary_risk REAL NOT NULL,
                expected_reward REAL NOT NULL,
                expected_return_percent REAL NOT NULL,
                drawdown_impact REAL NOT NULL,
                assessment_summary TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (sizing_id) REFERENCES position_sizing_decisions(sizing_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class RiskProfileRepository:
    """Repository for storing and retrieving RiskProfile models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_risk_db(self.conn)

    def save_profile(self, profile: RiskProfile) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO risk_profiles (
                    risk_profile_id, qualification_id, simulation_result_id,
                    account_currency, account_balance, maximum_risk_percent,
                    maximum_portfolio_exposure, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.risk_profile_id,
                    profile.qualification_id,
                    profile.simulation_result_id,
                    profile.account_currency,
                    profile.account_balance,
                    profile.maximum_risk_percent,
                    profile.maximum_portfolio_exposure,
                    json.dumps(profile.metadata, sort_keys=True),
                    profile.canonical_hash,
                ),
            )

    def get_profile(self, risk_profile_id: str) -> RiskProfile | None:
        cursor = self.conn.execute(
            """
            SELECT risk_profile_id, qualification_id, simulation_result_id,
                   account_currency, account_balance, maximum_risk_percent,
                   maximum_portfolio_exposure, metadata_json, canonical_hash
            FROM risk_profiles WHERE risk_profile_id = ?
            """,
            (risk_profile_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return RiskProfile(
            risk_profile_id=row[0],
            qualification_id=row[1],
            simulation_result_id=row[2],
            account_currency=row[3],
            account_balance=row[4],
            maximum_risk_percent=row[5],
            maximum_portfolio_exposure=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )

    def list_profiles(self) -> list[RiskProfile]:
        cursor = self.conn.execute("SELECT risk_profile_id FROM risk_profiles ORDER BY risk_profile_id ASC")
        profiles = []
        for row in cursor.fetchall():
            p = self.get_profile(row[0])
            if p:
                profiles.append(p)
        return profiles


class PositionSizingRepository:
    """Repository for storing and retrieving PositionSizingDecision models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_risk_db(self.conn)

    def save_sizing(self, sizing: PositionSizingDecision) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO position_sizing_decisions (
                    sizing_id, risk_profile_id, instrument, entry_price,
                    stop_loss_price, take_profit_price, stop_distance,
                    reward_distance, risk_reward_ratio, position_size,
                    minimum_lot_size, recommended_lot_size, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sizing.sizing_id,
                    sizing.risk_profile_id,
                    sizing.instrument,
                    sizing.entry_price,
                    sizing.stop_loss_price,
                    sizing.take_profit_price,
                    sizing.stop_distance,
                    sizing.reward_distance,
                    sizing.risk_reward_ratio,
                    sizing.position_size,
                    sizing.minimum_lot_size,
                    sizing.recommended_lot_size,
                    json.dumps(sizing.metadata, sort_keys=True),
                    sizing.canonical_hash,
                ),
            )

    def get_sizing(self, sizing_id: str) -> PositionSizingDecision | None:
        cursor = self.conn.execute(
            """
            SELECT sizing_id, risk_profile_id, instrument, entry_price,
                   stop_loss_price, take_profit_price, stop_distance,
                   reward_distance, risk_reward_ratio, position_size,
                   minimum_lot_size, recommended_lot_size, metadata_json, canonical_hash
            FROM position_sizing_decisions WHERE sizing_id = ?
            """,
            (sizing_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return PositionSizingDecision(
            sizing_id=row[0],
            risk_profile_id=row[1],
            instrument=row[2],
            entry_price=row[3],
            stop_loss_price=row[4],
            take_profit_price=row[5],
            stop_distance=row[6],
            reward_distance=row[7],
            risk_reward_ratio=row[8],
            position_size=row[9],
            minimum_lot_size=row[10],
            recommended_lot_size=row[11],
            metadata=json.loads(row[12]),
            canonical_hash=row[13],
        )


class CapitalAllocationRepository:
    """Repository for storing and retrieving CapitalAllocation models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_risk_db(self.conn)

    def save_allocation(self, allocation: CapitalAllocation) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO capital_allocations (
                    allocation_id, qualification_id, allocated_capital,
                    available_capital, reserved_capital, utilization_percent,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    allocation.allocation_id,
                    allocation.qualification_id,
                    allocation.allocated_capital,
                    allocation.available_capital,
                    allocation.reserved_capital,
                    allocation.utilization_percent,
                    json.dumps(allocation.metadata, sort_keys=True),
                    allocation.canonical_hash,
                ),
            )

    def get_allocation(self, allocation_id: str) -> CapitalAllocation | None:
        cursor = self.conn.execute(
            """
            SELECT allocation_id, qualification_id, allocated_capital,
                   available_capital, reserved_capital, utilization_percent,
                   metadata_json, canonical_hash
            FROM capital_allocations WHERE allocation_id = ?
            """,
            (allocation_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return CapitalAllocation(
            allocation_id=row[0],
            qualification_id=row[1],
            allocated_capital=row[2],
            available_capital=row[3],
            reserved_capital=row[4],
            utilization_percent=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ExposureRepository:
    """Repository for storing and retrieving ExposureAssessment models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_risk_db(self.conn)

    def save_exposure(self, exposure: ExposureAssessment) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO exposure_assessments (
                    exposure_id, active_positions_json, portfolio_exposure,
                    instrument_exposure, correlated_exposure, exposure_status,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exposure.exposure_id,
                    json.dumps(exposure.active_positions, sort_keys=True),
                    exposure.portfolio_exposure,
                    exposure.instrument_exposure,
                    exposure.correlated_exposure,
                    exposure.exposure_status.value if hasattr(exposure.exposure_status, "value") else str(exposure.exposure_status),
                    json.dumps(exposure.metadata, sort_keys=True),
                    exposure.canonical_hash,
                ),
            )

    def get_exposure(self, exposure_id: str) -> ExposureAssessment | None:
        cursor = self.conn.execute(
            """
            SELECT exposure_id, active_positions_json, portfolio_exposure,
                   instrument_exposure, correlated_exposure, exposure_status,
                   metadata_json, canonical_hash
            FROM exposure_assessments WHERE exposure_id = ?
            """,
            (exposure_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ExposureAssessment(
            exposure_id=row[0],
            active_positions=json.loads(row[1]),
            portfolio_exposure=row[2],
            instrument_exposure=row[3],
            correlated_exposure=row[4],
            exposure_status=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class RiskAssessmentRepository:
    """Repository for storing and retrieving RiskAssessment models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_risk_db(self.conn)

    def save_assessment(self, assessment: RiskAssessment) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO risk_assessments (
                    assessment_id, sizing_id, total_risk, monetary_risk,
                    expected_reward, expected_return_percent, drawdown_impact,
                    assessment_summary, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment.assessment_id,
                    assessment.sizing_id,
                    assessment.total_risk,
                    assessment.monetary_risk,
                    assessment.expected_reward,
                    assessment.expected_return_percent,
                    assessment.drawdown_impact,
                    assessment.assessment_summary,
                    json.dumps(assessment.metadata, sort_keys=True),
                    assessment.canonical_hash,
                ),
            )

    def get_assessment(self, assessment_id: str) -> RiskAssessment | None:
        cursor = self.conn.execute(
            """
            SELECT assessment_id, sizing_id, total_risk, monetary_risk,
                   expected_reward, expected_return_percent, drawdown_impact,
                   assessment_summary, metadata_json, canonical_hash
            FROM risk_assessments WHERE assessment_id = ?
            """,
            (assessment_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return RiskAssessment(
            assessment_id=row[0],
            sizing_id=row[1],
            total_risk=row[2],
            monetary_risk=row[3],
            expected_reward=row[4],
            expected_return_percent=row[5],
            drawdown_impact=row[6],
            assessment_summary=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class RiskReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_risk_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO risk_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM risk_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
