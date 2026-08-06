"""
Project GOAT v0.9 — SQLite Persistence Repositories for Deriv Market Microstructure Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.microstructure.core.enums import (
    ExecutionQualityRating,
    JumpDirection,
    MicrostructureMetricType,
    ObservationCategory,
    SyntheticIndexType,
    VolatilityRegime,
)
from goat.microstructure.core.models import (
    ExecutionProfile,
    JumpProfile,
    LiquidityProfile,
    MarketProfile,
    MicrostructureObservation,
    ResearchSummary,
    VolatilityProfile,
)


def init_microstructure_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables, indexes, and pragmas for Microstructure subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS microstructure_observations (
                observation_id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL,
                category TEXT NOT NULL,
                symbol TEXT NOT NULL,
                index_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                window_seconds INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS volatility_profiles (
                profile_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                index_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                window_seconds INTEGER NOT NULL,
                realized_volatility REAL NOT NULL,
                volatility_clustering_coeff REAL NOT NULL,
                volatility_persistence REAL NOT NULL,
                expansion_ratio REAL NOT NULL,
                contraction_ratio REAL NOT NULL,
                regime TEXT NOT NULL,
                observation_ids_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jump_profiles (
                profile_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                index_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                window_seconds INTEGER NOT NULL,
                jump_count INTEGER NOT NULL,
                jump_frequency REAL NOT NULL,
                mean_jump_magnitude REAL NOT NULL,
                max_jump_magnitude REAL NOT NULL,
                mean_jump_spacing_sec REAL NOT NULL,
                jump_persistence REAL NOT NULL,
                jump_clustering_index REAL NOT NULL,
                dominant_direction TEXT NOT NULL,
                observation_ids_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS liquidity_profiles (
                profile_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                index_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                window_seconds INTEGER NOT NULL,
                average_spread REAL NOT NULL,
                spread_stdev REAL NOT NULL,
                spread_stability REAL NOT NULL,
                quote_continuity_score REAL NOT NULL,
                ticks_per_second REAL NOT NULL,
                tick_density REAL NOT NULL,
                activity_score REAL NOT NULL,
                observation_ids_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_profiles (
                profile_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                index_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                window_seconds INTEGER NOT NULL,
                sample_count INTEGER NOT NULL,
                mean_latency_ms REAL NOT NULL,
                median_latency_ms REAL NOT NULL,
                p95_latency_ms REAL NOT NULL,
                fill_time_ms REAL NOT NULL,
                consistency_score REAL NOT NULL,
                rating TEXT NOT NULL,
                observation_ids_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_profiles (
                profile_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                index_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                volatility_profile_id TEXT NOT NULL,
                jump_profile_id TEXT NOT NULL,
                liquidity_profile_id TEXT NOT NULL,
                execution_profile_id TEXT NOT NULL,
                observation_count INTEGER NOT NULL,
                overall_health_score REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (volatility_profile_id) REFERENCES volatility_profiles (profile_id) ON DELETE CASCADE,
                FOREIGN KEY (jump_profile_id) REFERENCES jump_profiles (profile_id) ON DELETE CASCADE,
                FOREIGN KEY (liquidity_profile_id) REFERENCES liquidity_profiles (profile_id) ON DELETE CASCADE,
                FOREIGN KEY (execution_profile_id) REFERENCES execution_profiles (profile_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_summaries (
                summary_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                symbols_profiled_json TEXT NOT NULL,
                total_observations INTEGER NOT NULL,
                total_volatility_profiles INTEGER NOT NULL,
                total_jump_profiles INTEGER NOT NULL,
                total_liquidity_profiles INTEGER NOT NULL,
                total_execution_profiles INTEGER NOT NULL,
                total_market_profiles INTEGER NOT NULL,
                category_breakdown_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class ObservationRepository:
    """Repository for MicrostructureObservation instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, observation: MicrostructureObservation) -> MicrostructureObservation:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO microstructure_observations (
                    observation_id, metric_type, category, symbol, index_type, timestamp,
                    value, unit, window_seconds, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.observation_id,
                    observation.metric_type.value,
                    observation.category.value,
                    observation.symbol,
                    observation.index_type.value,
                    observation.timestamp,
                    observation.value,
                    observation.unit,
                    observation.window_seconds,
                    json.dumps(observation.metadata),
                    observation.canonical_hash,
                ),
            )
        return observation

    def get_by_id(self, observation_id: str) -> MicrostructureObservation | None:
        cursor = self._conn.execute("SELECT * FROM microstructure_observations WHERE observation_id = ?", (observation_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_by_symbol(self, symbol: str) -> list[MicrostructureObservation]:
        cursor = self._conn.execute(
            "SELECT * FROM microstructure_observations WHERE symbol = ? ORDER BY timestamp ASC", (symbol,)
        )
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def list_all(self) -> list[MicrostructureObservation]:
        cursor = self._conn.execute("SELECT * FROM microstructure_observations ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> MicrostructureObservation:
        return MicrostructureObservation(
            observation_id=row[0],
            metric_type=MicrostructureMetricType(row[1]),
            category=ObservationCategory(row[2]),
            symbol=row[3],
            index_type=SyntheticIndexType(row[4]),
            timestamp=row[5],
            value=float(row[6]),
            unit=row[7],
            window_seconds=int(row[8]),
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class VolatilityRepository:
    """Repository for VolatilityProfile instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, profile: VolatilityProfile) -> VolatilityProfile:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO volatility_profiles (
                    profile_id, symbol, index_type, timestamp, window_seconds, realized_volatility,
                    volatility_clustering_coeff, volatility_persistence, expansion_ratio,
                    contraction_ratio, regime, observation_ids_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.profile_id,
                    profile.symbol,
                    profile.index_type.value,
                    profile.timestamp,
                    profile.window_seconds,
                    profile.realized_volatility,
                    profile.volatility_clustering_coeff,
                    profile.volatility_persistence,
                    profile.expansion_ratio,
                    profile.contraction_ratio,
                    profile.regime.value,
                    json.dumps(profile.observation_ids),
                    json.dumps(profile.metadata),
                    profile.canonical_hash,
                ),
            )
        return profile

    def get_by_id(self, profile_id: str) -> VolatilityProfile | None:
        cursor = self._conn.execute("SELECT * FROM volatility_profiles WHERE profile_id = ?", (profile_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[VolatilityProfile]:
        cursor = self._conn.execute("SELECT * FROM volatility_profiles ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> VolatilityProfile:
        return VolatilityProfile(
            profile_id=row[0],
            symbol=row[1],
            index_type=SyntheticIndexType(row[2]),
            timestamp=row[3],
            window_seconds=int(row[4]),
            realized_volatility=float(row[5]),
            volatility_clustering_coeff=float(row[6]),
            volatility_persistence=float(row[7]),
            expansion_ratio=float(row[8]),
            contraction_ratio=float(row[9]),
            regime=VolatilityRegime(row[10]),
            observation_ids=json.loads(row[11]),
            metadata=json.loads(row[12]),
            canonical_hash=row[13],
        )


class JumpRepository:
    """Repository for JumpProfile instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, profile: JumpProfile) -> JumpProfile:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO jump_profiles (
                    profile_id, symbol, index_type, timestamp, window_seconds, jump_count,
                    jump_frequency, mean_jump_magnitude, max_jump_magnitude, mean_jump_spacing_sec,
                    jump_persistence, jump_clustering_index, dominant_direction, observation_ids_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.profile_id,
                    profile.symbol,
                    profile.index_type.value,
                    profile.timestamp,
                    profile.window_seconds,
                    profile.jump_count,
                    profile.jump_frequency,
                    profile.mean_jump_magnitude,
                    profile.max_jump_magnitude,
                    profile.mean_jump_spacing_sec,
                    profile.jump_persistence,
                    profile.jump_clustering_index,
                    profile.dominant_direction.value,
                    json.dumps(profile.observation_ids),
                    json.dumps(profile.metadata),
                    profile.canonical_hash,
                ),
            )
        return profile

    def get_by_id(self, profile_id: str) -> JumpProfile | None:
        cursor = self._conn.execute("SELECT * FROM jump_profiles WHERE profile_id = ?", (profile_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[JumpProfile]:
        cursor = self._conn.execute("SELECT * FROM jump_profiles ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> JumpProfile:
        return JumpProfile(
            profile_id=row[0],
            symbol=row[1],
            index_type=SyntheticIndexType(row[2]),
            timestamp=row[3],
            window_seconds=int(row[4]),
            jump_count=int(row[5]),
            jump_frequency=float(row[6]),
            mean_jump_magnitude=float(row[7]),
            max_jump_magnitude=float(row[8]),
            mean_jump_spacing_sec=float(row[9]),
            jump_persistence=float(row[10]),
            jump_clustering_index=float(row[11]),
            dominant_direction=JumpDirection(row[12]),
            observation_ids=json.loads(row[13]),
            metadata=json.loads(row[14]),
            canonical_hash=row[15],
        )


class LiquidityRepository:
    """Repository for LiquidityProfile instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, profile: LiquidityProfile) -> LiquidityProfile:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO liquidity_profiles (
                    profile_id, symbol, index_type, timestamp, window_seconds, average_spread,
                    spread_stdev, spread_stability, quote_continuity_score, ticks_per_second,
                    tick_density, activity_score, observation_ids_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.profile_id,
                    profile.symbol,
                    profile.index_type.value,
                    profile.timestamp,
                    profile.window_seconds,
                    profile.average_spread,
                    profile.spread_stdev,
                    profile.spread_stability,
                    profile.quote_continuity_score,
                    profile.ticks_per_second,
                    profile.tick_density,
                    profile.activity_score,
                    json.dumps(profile.observation_ids),
                    json.dumps(profile.metadata),
                    profile.canonical_hash,
                ),
            )
        return profile

    def get_by_id(self, profile_id: str) -> LiquidityProfile | None:
        cursor = self._conn.execute("SELECT * FROM liquidity_profiles WHERE profile_id = ?", (profile_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[LiquidityProfile]:
        cursor = self._conn.execute("SELECT * FROM liquidity_profiles ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> LiquidityProfile:
        return LiquidityProfile(
            profile_id=row[0],
            symbol=row[1],
            index_type=SyntheticIndexType(row[2]),
            timestamp=row[3],
            window_seconds=int(row[4]),
            average_spread=float(row[5]),
            spread_stdev=float(row[6]),
            spread_stability=float(row[7]),
            quote_continuity_score=float(row[8]),
            ticks_per_second=float(row[9]),
            tick_density=float(row[10]),
            activity_score=float(row[11]),
            observation_ids=json.loads(row[12]),
            metadata=json.loads(row[13]),
            canonical_hash=row[14],
        )


class ExecutionRepository:
    """Repository for ExecutionProfile instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, profile: ExecutionProfile) -> ExecutionProfile:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO execution_profiles (
                    profile_id, symbol, index_type, timestamp, window_seconds, sample_count,
                    mean_latency_ms, median_latency_ms, p95_latency_ms, fill_time_ms,
                    consistency_score, rating, observation_ids_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.profile_id,
                    profile.symbol,
                    profile.index_type.value,
                    profile.timestamp,
                    profile.window_seconds,
                    profile.sample_count,
                    profile.mean_latency_ms,
                    profile.median_latency_ms,
                    profile.p95_latency_ms,
                    profile.fill_time_ms,
                    profile.consistency_score,
                    profile.rating.value,
                    json.dumps(profile.observation_ids),
                    json.dumps(profile.metadata),
                    profile.canonical_hash,
                ),
            )
        return profile

    def get_by_id(self, profile_id: str) -> ExecutionProfile | None:
        cursor = self._conn.execute("SELECT * FROM execution_profiles WHERE profile_id = ?", (profile_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[ExecutionProfile]:
        cursor = self._conn.execute("SELECT * FROM execution_profiles ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ExecutionProfile:
        return ExecutionProfile(
            profile_id=row[0],
            symbol=row[1],
            index_type=SyntheticIndexType(row[2]),
            timestamp=row[3],
            window_seconds=int(row[4]),
            sample_count=int(row[5]),
            mean_latency_ms=float(row[6]),
            median_latency_ms=float(row[7]),
            p95_latency_ms=float(row[8]),
            fill_time_ms=float(row[9]),
            consistency_score=float(row[10]),
            rating=ExecutionQualityRating(row[11]),
            observation_ids=json.loads(row[12]),
            metadata=json.loads(row[13]),
            canonical_hash=row[14],
        )


class MarketProfileRepository:
    """Repository for MarketProfile instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, profile: MarketProfile) -> MarketProfile:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO market_profiles (
                    profile_id, symbol, index_type, timestamp, volatility_profile_id,
                    jump_profile_id, liquidity_profile_id, execution_profile_id,
                    observation_count, overall_health_score, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.profile_id,
                    profile.symbol,
                    profile.index_type.value,
                    profile.timestamp,
                    profile.volatility_profile_id,
                    profile.jump_profile_id,
                    profile.liquidity_profile_id,
                    profile.execution_profile_id,
                    profile.observation_count,
                    profile.overall_health_score,
                    json.dumps(profile.metadata),
                    profile.canonical_hash,
                ),
            )
        return profile

    def get_by_id(self, profile_id: str) -> MarketProfile | None:
        cursor = self._conn.execute("SELECT * FROM market_profiles WHERE profile_id = ?", (profile_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[MarketProfile]:
        cursor = self._conn.execute("SELECT * FROM market_profiles ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> MarketProfile:
        return MarketProfile(
            profile_id=row[0],
            symbol=row[1],
            index_type=SyntheticIndexType(row[2]),
            timestamp=row[3],
            volatility_profile_id=row[4],
            jump_profile_id=row[5],
            liquidity_profile_id=row[6],
            execution_profile_id=row[7],
            observation_count=int(row[8]),
            overall_health_score=float(row[9]),
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )


class SummaryRepository:
    """Repository for ResearchSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: ResearchSummary) -> ResearchSummary:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO research_summaries (
                    summary_id, timestamp, symbols_profiled_json, total_observations,
                    total_volatility_profiles, total_jump_profiles, total_liquidity_profiles,
                    total_execution_profiles, total_market_profiles, category_breakdown_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.timestamp,
                    json.dumps(summary.symbols_profiled),
                    summary.total_observations,
                    summary.total_volatility_profiles,
                    summary.total_jump_profiles,
                    summary.total_liquidity_profiles,
                    summary.total_execution_profiles,
                    summary.total_market_profiles,
                    json.dumps(summary.category_breakdown),
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> ResearchSummary | None:
        cursor = self._conn.execute("SELECT * FROM research_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[ResearchSummary]:
        cursor = self._conn.execute("SELECT * FROM research_summaries ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ResearchSummary:
        return ResearchSummary(
            summary_id=row[0],
            timestamp=row[1],
            symbols_profiled=json.loads(row[2]),
            total_observations=int(row[3]),
            total_volatility_profiles=int(row[4]),
            total_jump_profiles=int(row[5]),
            total_liquidity_profiles=int(row[6]),
            total_execution_profiles=int(row[7]),
            total_market_profiles=int(row[8]),
            category_breakdown=json.loads(row[9]),
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )


class MicrostructureDatabase:
    """Unified Persistence Database Context wrapping all Microstructure repositories."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_microstructure_db(self.conn)
        self.observations = ObservationRepository(self.conn)
        self.volatility = VolatilityRepository(self.conn)
        self.jumps = JumpRepository(self.conn)
        self.liquidity = LiquidityRepository(self.conn)
        self.execution = ExecutionRepository(self.conn)
        self.market_profiles = MarketProfileRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
