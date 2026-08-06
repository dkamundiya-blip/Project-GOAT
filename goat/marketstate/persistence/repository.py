"""
Project GOAT v0.8 — Market State Persistence Repositories

Provides SQLite repositories enforcing foreign keys (PRAGMA foreign_keys = ON),
round-trip serialization, and query methods for:
- MarketStateRepository
- VolatilityRepository
- LiquidityRepository
- StructureRepository
- QualityRepository
- MarketStateReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from goat.marketstate.core.enums import (
    ActivityState,
    LiquidityState,
    QualityState,
    SpreadState,
    StructureState,
    TrendState,
    VolatilityState,
)
from goat.marketstate.core.models import (
    LiquidityAssessment,
    MarketQualityAssessment,
    MarketState,
    StructureAssessment,
    VolatilityAssessment,
)


def init_marketstate_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database for Market State subsystem with PRAGMA foreign_keys = ON."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS volatility_assessments (
                assessment_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                realized_volatility REAL NOT NULL,
                volatility_class TEXT NOT NULL,
                volatility_score REAL NOT NULL,
                explanation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS liquidity_assessments (
                assessment_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                spread REAL NOT NULL,
                spread_quality TEXT NOT NULL,
                liquidity_score REAL NOT NULL,
                market_depth_proxy REAL NOT NULL,
                activity_state TEXT NOT NULL,
                liquidity_state TEXT NOT NULL,
                explanation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS structure_assessments (
                assessment_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                structure_state TEXT NOT NULL,
                trend_state TEXT NOT NULL,
                higher_highs INTEGER NOT NULL,
                lower_lows INTEGER NOT NULL,
                higher_lows INTEGER NOT NULL,
                lower_highs INTEGER NOT NULL,
                trend_strength REAL NOT NULL,
                explanation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quality_assessments (
                assessment_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                data_quality TEXT NOT NULL,
                stream_health TEXT NOT NULL,
                latency_quality TEXT NOT NULL,
                replay_quality TEXT NOT NULL,
                overall_quality TEXT NOT NULL,
                explanation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_states (
                state_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                trend_state TEXT NOT NULL,
                volatility_state TEXT NOT NULL,
                liquidity_state TEXT NOT NULL,
                spread_state TEXT NOT NULL,
                activity_state TEXT NOT NULL,
                structure_state TEXT NOT NULL,
                overall_quality TEXT NOT NULL,
                confidence REAL NOT NULL,
                explanation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_state_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                markdown_content TEXT NOT NULL,
                json_content TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
    return conn


class VolatilityRepository:
    """SQLite repository for VolatilityAssessment persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, vol: VolatilityAssessment) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO volatility_assessments (
                    assessment_id, symbol, timeframe, realized_volatility, volatility_class,
                    volatility_score, explanation, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    vol.assessment_id,
                    vol.symbol,
                    vol.timeframe,
                    vol.realized_volatility,
                    vol.volatility_class.value,
                    vol.volatility_score,
                    vol.explanation,
                    json.dumps(vol.metadata, sort_keys=True),
                    vol.canonical_hash,
                ),
            )

    def get_by_id(self, assessment_id: str) -> VolatilityAssessment | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM volatility_assessments WHERE assessment_id = ?;", (assessment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return VolatilityAssessment(
            assessment_id=row[0],
            symbol=row[1],
            timeframe=row[2],
            realized_volatility=row[3],
            volatility_class=VolatilityState(row[4]),
            volatility_score=row[5],
            explanation=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class LiquidityRepository:
    """SQLite repository for LiquidityAssessment persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, liq: LiquidityAssessment) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO liquidity_assessments (
                    assessment_id, symbol, spread, spread_quality, liquidity_score,
                    market_depth_proxy, activity_state, liquidity_state, explanation, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    liq.assessment_id,
                    liq.symbol,
                    liq.spread,
                    liq.spread_quality.value,
                    liq.liquidity_score,
                    liq.market_depth_proxy,
                    liq.activity_state.value,
                    liq.liquidity_state.value,
                    liq.explanation,
                    json.dumps(liq.metadata, sort_keys=True),
                    liq.canonical_hash,
                ),
            )

    def get_by_id(self, assessment_id: str) -> LiquidityAssessment | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM liquidity_assessments WHERE assessment_id = ?;", (assessment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return LiquidityAssessment(
            assessment_id=row[0],
            symbol=row[1],
            spread=row[2],
            spread_quality=SpreadState(row[3]),
            liquidity_score=row[4],
            market_depth_proxy=row[5],
            activity_state=ActivityState(row[6]),
            liquidity_state=LiquidityState(row[7]),
            explanation=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class StructureRepository:
    """SQLite repository for StructureAssessment persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, struct: StructureAssessment) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO structure_assessments (
                    assessment_id, symbol, structure_state, trend_state, higher_highs,
                    lower_lows, higher_lows, lower_highs, trend_strength, explanation, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    struct.assessment_id,
                    struct.symbol,
                    struct.structure_state.value,
                    struct.trend_state.value,
                    struct.higher_highs,
                    struct.lower_lows,
                    struct.higher_lows,
                    struct.lower_highs,
                    struct.trend_strength,
                    struct.explanation,
                    json.dumps(struct.metadata, sort_keys=True),
                    struct.canonical_hash,
                ),
            )

    def get_by_id(self, assessment_id: str) -> StructureAssessment | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM structure_assessments WHERE assessment_id = ?;", (assessment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return StructureAssessment(
            assessment_id=row[0],
            symbol=row[1],
            structure_state=StructureState(row[2]),
            trend_state=TrendState(row[3]),
            higher_highs=row[4],
            lower_lows=row[5],
            higher_lows=row[6],
            lower_highs=row[7],
            trend_strength=row[8],
            explanation=row[9],
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )


class QualityRepository:
    """SQLite repository for MarketQualityAssessment persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, qual: MarketQualityAssessment) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO quality_assessments (
                    assessment_id, symbol, data_quality, stream_health, latency_quality,
                    replay_quality, overall_quality, explanation, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    qual.assessment_id,
                    qual.symbol,
                    qual.data_quality.value,
                    qual.stream_health.value,
                    qual.latency_quality.value,
                    qual.replay_quality.value,
                    qual.overall_quality.value,
                    qual.explanation,
                    json.dumps(qual.metadata, sort_keys=True),
                    qual.canonical_hash,
                ),
            )

    def get_by_id(self, assessment_id: str) -> MarketQualityAssessment | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM quality_assessments WHERE assessment_id = ?;", (assessment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return MarketQualityAssessment(
            assessment_id=row[0],
            symbol=row[1],
            data_quality=QualityState(row[2]),
            stream_health=QualityState(row[3]),
            latency_quality=QualityState(row[4]),
            replay_quality=QualityState(row[5]),
            overall_quality=QualityState(row[6]),
            explanation=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class MarketStateRepository:
    """SQLite repository for MarketState persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, state: MarketState) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_states (
                    state_id, symbol, timestamp, trend_state, volatility_state, liquidity_state,
                    spread_state, activity_state, structure_state, overall_quality, confidence,
                    explanation, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    state.state_id,
                    state.symbol,
                    state.timestamp,
                    state.trend_state.value,
                    state.volatility_state.value,
                    state.liquidity_state.value,
                    state.spread_state.value,
                    state.activity_state.value,
                    state.structure_state.value,
                    state.overall_quality.value,
                    state.confidence,
                    state.explanation,
                    json.dumps(state.metadata, sort_keys=True),
                    state.canonical_hash,
                ),
            )

    def get_by_id(self, state_id: str) -> MarketState | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM market_states WHERE state_id = ?;", (state_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return MarketState(
            state_id=row[0],
            symbol=row[1],
            timestamp=row[2],
            trend_state=TrendState(row[3]),
            volatility_state=VolatilityState(row[4]),
            liquidity_state=LiquidityState(row[5]),
            spread_state=SpreadState(row[6]),
            activity_state=ActivityState(row[7]),
            structure_state=StructureState(row[8]),
            overall_quality=QualityState(row[9]),
            confidence=row[10],
            explanation=row[11],
            metadata=json.loads(row[12]),
            canonical_hash=row[13],
        )


class MarketStateReportRepository:
    """SQLite repository for storing generated MarketState reports."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_report(
        self,
        report_id: str,
        report_type: str,
        symbol: str,
        timestamp: str,
        markdown_content: str,
        json_content: str,
        canonical_hash: str,
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_state_reports (
                    report_id, report_type, symbol, timestamp, markdown_content, json_content, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    report_id,
                    report_type,
                    symbol,
                    timestamp,
                    markdown_content,
                    json_content,
                    canonical_hash,
                ),
            )
