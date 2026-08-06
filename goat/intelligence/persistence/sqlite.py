"""
Project GOAT v0.9 — SQLite Persistence Repositories for Research Intelligence Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.intelligence.core.enums import (
    HealthStatus,
    InsightCategory,
    InsightImpact,
    RecommendationPriority,
    TrendDirection,
)
from goat.intelligence.core.models import (
    InstitutionalRecommendation,
    IntelligenceSummary,
    MetaAnalysis,
    ResearchHealth,
    ResearchInsight,
    ResearchTrend,
)


def init_intelligence_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables, indexes, and pragmas for Intelligence subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_insights (
                insight_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                impact TEXT NOT NULL,
                title TEXT NOT NULL,
                findings_statement TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                supporting_data_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_analyses (
                meta_analysis_id TEXT PRIMARY KEY,
                analysis_title TEXT NOT NULL,
                sample_size INTEGER NOT NULL,
                pooled_effect_size REAL NOT NULL,
                heterogeneity_i2 REAL NOT NULL,
                p_value REAL NOT NULL,
                key_findings_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_trends (
                trend_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                direction TEXT NOT NULL,
                historical_values_json TEXT NOT NULL,
                percentage_change REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS institutional_recommendations (
                recommendation_id TEXT PRIMARY KEY,
                priority TEXT NOT NULL,
                topic TEXT NOT NULL,
                rationale TEXT NOT NULL,
                expected_utility REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_health (
                health_id TEXT PRIMARY KEY,
                health_score REAL NOT NULL,
                status TEXT NOT NULL,
                success_rate REAL NOT NULL,
                efficiency_score REAL NOT NULL,
                waste_percentage REAL NOT NULL,
                diagnostics_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_summaries (
                summary_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                total_insights INTEGER NOT NULL,
                total_meta_analyses INTEGER NOT NULL,
                total_recommendations INTEGER NOT NULL,
                overall_health_score REAL NOT NULL,
                insights_by_category_json TEXT NOT NULL,
                recommendations_by_priority_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class InsightRepository:
    """Repository for ResearchInsight instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, insight: ResearchInsight) -> ResearchInsight:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO research_insights (
                    insight_id, category, impact, title, findings_statement,
                    confidence_level, supporting_data_json, timestamp,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    insight.insight_id,
                    insight.category.value,
                    insight.impact.value,
                    insight.title,
                    insight.findings_statement,
                    insight.confidence_level,
                    json.dumps(insight.supporting_data),
                    insight.timestamp,
                    json.dumps(insight.metadata),
                    insight.canonical_hash,
                ),
            )
        return insight

    def get_by_id(self, insight_id: str) -> ResearchInsight | None:
        cursor = self._conn.execute("SELECT * FROM research_insights WHERE insight_id = ?", (insight_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[ResearchInsight]:
        cursor = self._conn.execute("SELECT * FROM research_insights ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ResearchInsight:
        return ResearchInsight(
            insight_id=row[0],
            category=InsightCategory(row[1]),
            impact=InsightImpact(row[2]),
            title=row[3],
            findings_statement=row[4],
            confidence_level=float(row[5]),
            supporting_data=json.loads(row[6]),
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class MetaAnalysisRepository:
    """Repository for MetaAnalysis instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, meta: MetaAnalysis) -> MetaAnalysis:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO meta_analyses (
                    meta_analysis_id, analysis_title, sample_size, pooled_effect_size,
                    heterogeneity_i2, p_value, key_findings_json, timestamp,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meta.meta_analysis_id,
                    meta.analysis_title,
                    meta.sample_size,
                    meta.pooled_effect_size,
                    meta.heterogeneity_i2,
                    meta.p_value,
                    json.dumps(meta.key_findings),
                    meta.timestamp,
                    json.dumps(meta.metadata),
                    meta.canonical_hash,
                ),
            )
        return meta

    def get_by_id(self, meta_analysis_id: str) -> MetaAnalysis | None:
        cursor = self._conn.execute("SELECT * FROM meta_analyses WHERE meta_analysis_id = ?", (meta_analysis_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[MetaAnalysis]:
        cursor = self._conn.execute("SELECT * FROM meta_analyses ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> MetaAnalysis:
        return MetaAnalysis(
            meta_analysis_id=row[0],
            analysis_title=row[1],
            sample_size=int(row[2]),
            pooled_effect_size=float(row[3]),
            heterogeneity_i2=float(row[4]),
            p_value=float(row[5]),
            key_findings=json.loads(row[6]),
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class TrendRepository:
    """Repository for ResearchTrend instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, trend: ResearchTrend) -> ResearchTrend:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO research_trends (
                    trend_id, metric_name, direction, historical_values_json,
                    percentage_change, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trend.trend_id,
                    trend.metric_name,
                    trend.direction.value,
                    json.dumps(trend.historical_values),
                    trend.percentage_change,
                    trend.timestamp,
                    json.dumps(trend.metadata),
                    trend.canonical_hash,
                ),
            )
        return trend

    def get_by_id(self, trend_id: str) -> ResearchTrend | None:
        cursor = self._conn.execute("SELECT * FROM research_trends WHERE trend_id = ?", (trend_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[ResearchTrend]:
        cursor = self._conn.execute("SELECT * FROM research_trends ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ResearchTrend:
        return ResearchTrend(
            trend_id=row[0],
            metric_name=row[1],
            direction=TrendDirection(row[2]),
            historical_values=json.loads(row[3]),
            percentage_change=float(row[4]),
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class RecommendationRepository:
    """Repository for InstitutionalRecommendation instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, rec: InstitutionalRecommendation) -> InstitutionalRecommendation:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO institutional_recommendations (
                    recommendation_id, priority, topic, rationale,
                    expected_utility, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.recommendation_id,
                    rec.priority.value,
                    rec.topic,
                    rec.rationale,
                    rec.expected_utility,
                    rec.timestamp,
                    json.dumps(rec.metadata),
                    rec.canonical_hash,
                ),
            )
        return rec

    def get_by_id(self, recommendation_id: str) -> InstitutionalRecommendation | None:
        cursor = self._conn.execute("SELECT * FROM institutional_recommendations WHERE recommendation_id = ?", (recommendation_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[InstitutionalRecommendation]:
        cursor = self._conn.execute("SELECT * FROM institutional_recommendations ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> InstitutionalRecommendation:
        return InstitutionalRecommendation(
            recommendation_id=row[0],
            priority=RecommendationPriority(row[1]),
            topic=row[2],
            rationale=row[3],
            expected_utility=float(row[4]),
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class HealthRepository:
    """Repository for ResearchHealth instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, health: ResearchHealth) -> ResearchHealth:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO research_health (
                    health_id, health_score, status, success_rate,
                    efficiency_score, waste_percentage, diagnostics_json,
                    timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    health.health_id,
                    health.health_score,
                    health.status.value,
                    health.success_rate,
                    health.efficiency_score,
                    health.waste_percentage,
                    json.dumps(health.diagnostics),
                    health.timestamp,
                    json.dumps(health.metadata),
                    health.canonical_hash,
                ),
            )
        return health

    def get_by_id(self, health_id: str) -> ResearchHealth | None:
        cursor = self._conn.execute("SELECT * FROM research_health WHERE health_id = ?", (health_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[ResearchHealth]:
        cursor = self._conn.execute("SELECT * FROM research_health ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ResearchHealth:
        return ResearchHealth(
            health_id=row[0],
            health_score=float(row[1]),
            status=HealthStatus(row[2]),
            success_rate=float(row[3]),
            efficiency_score=float(row[4]),
            waste_percentage=float(row[5]),
            diagnostics=json.loads(row[6]),
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class SummaryRepository:
    """Repository for IntelligenceSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: IntelligenceSummary) -> IntelligenceSummary:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_summaries (
                    summary_id, timestamp, total_insights, total_meta_analyses,
                    total_recommendations, overall_health_score,
                    insights_by_category_json, recommendations_by_priority_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.timestamp,
                    summary.total_insights,
                    summary.total_meta_analyses,
                    summary.total_recommendations,
                    summary.overall_health_score,
                    json.dumps(summary.insights_by_category),
                    json.dumps(summary.recommendations_by_priority),
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> IntelligenceSummary | None:
        cursor = self._conn.execute("SELECT * FROM intelligence_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[IntelligenceSummary]:
        cursor = self._conn.execute("SELECT * FROM intelligence_summaries ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> IntelligenceSummary:
        return IntelligenceSummary(
            summary_id=row[0],
            timestamp=row[1],
            total_insights=int(row[2]),
            total_meta_analyses=int(row[3]),
            total_recommendations=int(row[4]),
            overall_health_score=float(row[5]),
            insights_by_category=json.loads(row[6]),
            recommendations_by_priority=json.loads(row[7]),
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class IntelligencePersistenceContext:
    """Unified Persistence Database Context wrapping all Research Intelligence repositories."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_intelligence_db(self.conn)
        self.insights = InsightRepository(self.conn)
        self.meta_analyses = MetaAnalysisRepository(self.conn)
        self.trends = TrendRepository(self.conn)
        self.recommendations = RecommendationRepository(self.conn)
        self.health = HealthRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
