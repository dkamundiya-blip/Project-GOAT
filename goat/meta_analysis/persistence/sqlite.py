"""
Project GOAT v0.7 — SQLite Persistence for Meta-Analysis & Research Intelligence Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- MetaAnalysisRepository
- ClusterRepository
- PatternRepository
- TrendRepository
- SummaryRepository
- ReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.meta_analysis.core.models import (
    MetaAnalysisResult,
    ResearchCluster,
    ResearchIntelligenceMetrics,
    ResearchPattern,
    ResearchTrend,
    ScientificSummary,
)


def init_meta_analysis_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for meta-analysis."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_clusters (
                cluster_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                cluster_type TEXT NOT NULL,
                participating_nodes_json TEXT NOT NULL,
                participating_validations_json TEXT NOT NULL,
                participating_hypotheses_json TEXT NOT NULL,
                participating_experiments_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                reproducibility REAL NOT NULL,
                consistency REAL NOT NULL,
                creation_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                frequency INTEGER NOT NULL,
                confidence REAL NOT NULL,
                supporting_clusters_json TEXT NOT NULL,
                supporting_validations_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_trends (
                trend_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                direction TEXT NOT NULL,
                strength REAL NOT NULL,
                persistence REAL NOT NULL,
                evidence_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scientific_summaries (
                summary_id TEXT PRIMARY KEY,
                validated_knowledge_count INTEGER NOT NULL,
                integrated_knowledge_count INTEGER NOT NULL,
                conflict_count INTEGER NOT NULL,
                cluster_count INTEGER NOT NULL,
                pattern_count INTEGER NOT NULL,
                trend_count INTEGER NOT NULL,
                strongest_areas_json TEXT NOT NULL,
                weakest_areas_json TEXT NOT NULL,
                contradictions_json TEXT NOT NULL,
                recommendations_json TEXT NOT NULL,
                creation_timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_analysis_results (
                analysis_id TEXT PRIMARY KEY,
                analyzed_knowledge_states_json TEXT NOT NULL,
                clusters_json TEXT NOT NULL,
                patterns_json TEXT NOT NULL,
                trends_json TEXT NOT NULL,
                contradictions_json TEXT NOT NULL,
                summary_json TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                reproducibility REAL NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_analysis_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class ClusterRepository:
    """Repository for storing and retrieving ResearchCluster models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_meta_analysis_db(self.conn)

    def save_cluster(self, cluster: ResearchCluster) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO research_clusters (
                    cluster_id, title, description, cluster_type,
                    participating_nodes_json, participating_validations_json,
                    participating_hypotheses_json, participating_experiments_json,
                    confidence, reproducibility, consistency, creation_timestamp,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cluster.cluster_id,
                    cluster.title,
                    cluster.description,
                    cluster.cluster_type.value if hasattr(cluster.cluster_type, "value") else str(cluster.cluster_type),
                    json.dumps(cluster.participating_nodes, sort_keys=True),
                    json.dumps(cluster.participating_validations, sort_keys=True),
                    json.dumps(cluster.participating_hypotheses, sort_keys=True),
                    json.dumps(cluster.participating_experiments, sort_keys=True),
                    cluster.confidence,
                    cluster.reproducibility,
                    cluster.consistency,
                    cluster.creation_timestamp,
                    json.dumps(cluster.metadata, sort_keys=True),
                    cluster.canonical_hash,
                ),
            )

    def get_cluster(self, cluster_id: str) -> ResearchCluster | None:
        cursor = self.conn.execute(
            """
            SELECT cluster_id, title, description, cluster_type,
                   participating_nodes_json, participating_validations_json,
                   participating_hypotheses_json, participating_experiments_json,
                   confidence, reproducibility, consistency, creation_timestamp,
                   metadata_json, canonical_hash
            FROM research_clusters WHERE cluster_id = ?
            """,
            (cluster_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ResearchCluster(
            cluster_id=row[0],
            title=row[1],
            description=row[2],
            cluster_type=row[3],
            participating_nodes=json.loads(row[4]),
            participating_validations=json.loads(row[5]),
            participating_hypotheses=json.loads(row[6]),
            participating_experiments=json.loads(row[7]),
            confidence=row[8],
            reproducibility=row[9],
            consistency=row[10],
            creation_timestamp=row[11],
            metadata=json.loads(row[12]),
            canonical_hash=row[13],
        )

    def list_clusters(self) -> list[ResearchCluster]:
        cursor = self.conn.execute("SELECT cluster_id FROM research_clusters ORDER BY cluster_id ASC")
        clusters = []
        for row in cursor.fetchall():
            c = self.get_cluster(row[0])
            if c:
                clusters.append(c)
        return clusters


class PatternRepository:
    """Repository for storing and retrieving ResearchPattern models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_meta_analysis_db(self.conn)

    def save_pattern(self, pattern: ResearchPattern) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO research_patterns (
                    pattern_id, pattern_name, description, category,
                    evidence_json, frequency, confidence, supporting_clusters_json,
                    supporting_validations_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pattern.pattern_id,
                    pattern.pattern_name,
                    pattern.description,
                    pattern.category.value if hasattr(pattern.category, "value") else str(pattern.category),
                    json.dumps(pattern.evidence, sort_keys=True),
                    pattern.frequency,
                    pattern.confidence,
                    json.dumps(pattern.supporting_clusters, sort_keys=True),
                    json.dumps(pattern.supporting_validations, sort_keys=True),
                    json.dumps(pattern.metadata, sort_keys=True),
                    pattern.canonical_hash,
                ),
            )

    def get_pattern(self, pattern_id: str) -> ResearchPattern | None:
        cursor = self.conn.execute(
            """
            SELECT pattern_id, pattern_name, description, category,
                   evidence_json, frequency, confidence, supporting_clusters_json,
                   supporting_validations_json, metadata_json, canonical_hash
            FROM research_patterns WHERE pattern_id = ?
            """,
            (pattern_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ResearchPattern(
            pattern_id=row[0],
            pattern_name=row[1],
            description=row[2],
            category=row[3],
            evidence=json.loads(row[4]),
            frequency=row[5],
            confidence=row[6],
            supporting_clusters=json.loads(row[7]),
            supporting_validations=json.loads(row[8]),
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )

    def list_patterns(self) -> list[ResearchPattern]:
        cursor = self.conn.execute("SELECT pattern_id FROM research_patterns ORDER BY pattern_id ASC")
        patterns = []
        for row in cursor.fetchall():
            p = self.get_pattern(row[0])
            if p:
                patterns.append(p)
        return patterns


class TrendRepository:
    """Repository for storing and retrieving ResearchTrend models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_meta_analysis_db(self.conn)

    def save_trend(self, trend: ResearchTrend) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO research_trends (
                    trend_id, topic, direction, strength, persistence,
                    evidence_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trend.trend_id,
                    trend.topic,
                    trend.direction.value if hasattr(trend.direction, "value") else str(trend.direction),
                    trend.strength,
                    trend.persistence,
                    json.dumps(trend.evidence, sort_keys=True),
                    json.dumps(trend.metadata, sort_keys=True),
                    trend.canonical_hash,
                ),
            )

    def get_trend(self, trend_id: str) -> ResearchTrend | None:
        cursor = self.conn.execute(
            """
            SELECT trend_id, topic, direction, strength, persistence,
                   evidence_json, metadata_json, canonical_hash
            FROM research_trends WHERE trend_id = ?
            """,
            (trend_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ResearchTrend(
            trend_id=row[0],
            topic=row[1],
            direction=row[2],
            strength=row[3],
            persistence=row[4],
            evidence=json.loads(row[5]),
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )

    def list_trends(self) -> list[ResearchTrend]:
        cursor = self.conn.execute("SELECT trend_id FROM research_trends ORDER BY trend_id ASC")
        trends = []
        for row in cursor.fetchall():
            t = self.get_trend(row[0])
            if t:
                trends.append(t)
        return trends


class SummaryRepository:
    """Repository for storing and retrieving ScientificSummary models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_meta_analysis_db(self.conn)

    def save_summary(self, summary: ScientificSummary) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO scientific_summaries (
                    summary_id, validated_knowledge_count, integrated_knowledge_count,
                    conflict_count, cluster_count, pattern_count, trend_count,
                    strongest_areas_json, weakest_areas_json, contradictions_json,
                    recommendations_json, creation_timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.validated_knowledge_count,
                    summary.integrated_knowledge_count,
                    summary.conflict_count,
                    summary.cluster_count,
                    summary.pattern_count,
                    summary.trend_count,
                    json.dumps(summary.strongest_research_areas, sort_keys=True),
                    json.dumps(summary.weakest_research_areas, sort_keys=True),
                    json.dumps(summary.outstanding_contradictions, sort_keys=True),
                    json.dumps(summary.future_investigation_recommendations, sort_keys=True),
                    summary.creation_timestamp,
                    summary.canonical_hash,
                ),
            )

    def get_summary(self, summary_id: str) -> ScientificSummary | None:
        cursor = self.conn.execute(
            """
            SELECT summary_id, validated_knowledge_count, integrated_knowledge_count,
                   conflict_count, cluster_count, pattern_count, trend_count,
                   strongest_areas_json, weakest_areas_json, contradictions_json,
                   recommendations_json, creation_timestamp, canonical_hash
            FROM scientific_summaries WHERE summary_id = ?
            """,
            (summary_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ScientificSummary(
            summary_id=row[0],
            validated_knowledge_count=row[1],
            integrated_knowledge_count=row[2],
            conflict_count=row[3],
            cluster_count=row[4],
            pattern_count=row[5],
            trend_count=row[6],
            strongest_research_areas=json.loads(row[7]),
            weakest_research_areas=json.loads(row[8]),
            outstanding_contradictions=json.loads(row[9]),
            future_investigation_recommendations=json.loads(row[10]),
            creation_timestamp=row[11],
            canonical_hash=row[12],
        )


class MetaAnalysisRepository:
    """Repository for storing and retrieving MetaAnalysisResult models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_meta_analysis_db(self.conn)

    def save_result(self, result: MetaAnalysisResult) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO meta_analysis_results (
                    analysis_id, analyzed_knowledge_states_json, clusters_json,
                    patterns_json, trends_json, contradictions_json, summary_json,
                    metrics_json, confidence, reproducibility, timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.analysis_id,
                    json.dumps(result.analyzed_knowledge_states, sort_keys=True),
                    json.dumps([c.dict() for c in result.clusters], sort_keys=True),
                    json.dumps([p.dict() for p in result.patterns], sort_keys=True),
                    json.dumps([t.dict() for t in result.trends], sort_keys=True),
                    json.dumps(result.contradictions, sort_keys=True),
                    json.dumps(result.scientific_summary.dict(), sort_keys=True),
                    json.dumps(result.intelligence_metrics.dict(), sort_keys=True),
                    result.confidence,
                    result.reproducibility,
                    result.timestamp,
                    result.canonical_hash,
                ),
            )

    def get_result(self, analysis_id: str) -> MetaAnalysisResult | None:
        cursor = self.conn.execute(
            """
            SELECT analysis_id, analyzed_knowledge_states_json, clusters_json,
                   patterns_json, trends_json, contradictions_json, summary_json,
                   metrics_json, confidence, reproducibility, timestamp, canonical_hash
            FROM meta_analysis_results WHERE analysis_id = ?
            """,
            (analysis_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return MetaAnalysisResult(
            analysis_id=row[0],
            analyzed_knowledge_states=json.loads(row[1]),
            clusters=[ResearchCluster(**c) for c in json.loads(row[2])],
            patterns=[ResearchPattern(**p) for p in json.loads(row[3])],
            trends=[ResearchTrend(**t) for t in json.loads(row[4])],
            contradictions=json.loads(row[5]),
            scientific_summary=ScientificSummary(**json.loads(row[6])),
            intelligence_metrics=ResearchIntelligenceMetrics(**json.loads(row[7])),
            confidence=row[8],
            reproducibility=row[9],
            timestamp=row[10],
            canonical_hash=row[11],
        )


class ReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_meta_analysis_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO meta_analysis_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM meta_analysis_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
