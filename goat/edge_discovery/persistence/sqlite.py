"""
Project GOAT v0.9 — SQLite Persistence Repositories for Quantitative Edge Discovery Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.edge_discovery.core.enums import (
    EdgeCategory,
    NoveltyStatus,
    PatternType,
    QualityTier,
    RejectionReason,
    ValidationStatus,
)
from goat.edge_discovery.core.models import (
    DiscoveryDecision,
    DiscoverySummary,
    EdgeCandidate,
    EdgePattern,
    EdgeScore,
    NoveltyAssessment,
    PatternCluster,
)


def init_edge_discovery_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables, indexes, and pragmas for Edge Discovery subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                sample_size INTEGER NOT NULL,
                effect_size REAL NOT NULL,
                statistical_significance REAL NOT NULL,
                regime_consistency REAL NOT NULL,
                observation_ids_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pattern_clusters (
                cluster_id TEXT PRIMARY KEY,
                cluster_name TEXT NOT NULL,
                pattern_ids_json TEXT NOT NULL,
                centroid_pattern_id TEXT NOT NULL,
                intra_cluster_similarity REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_candidates (
                candidate_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                symbol TEXT NOT NULL,
                pattern_ids_json TEXT NOT NULL,
                hypothesis_statement TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                observation_count INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS novelty_assessments (
                assessment_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                max_similarity_score REAL NOT NULL,
                closest_archived_edge_id TEXT,
                status TEXT NOT NULL,
                is_novel INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (candidate_id) REFERENCES edge_candidates (candidate_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_scores (
                score_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                overall_score REAL NOT NULL,
                support_score REAL NOT NULL,
                stability_score REAL NOT NULL,
                consistency_score REAL NOT NULL,
                robustness_score REAL NOT NULL,
                live_compatibility_score REAL NOT NULL,
                quality_tier TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (candidate_id) REFERENCES edge_candidates (candidate_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS discovery_decisions (
                decision_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                status TEXT NOT NULL,
                rejection_reason TEXT NOT NULL,
                novelty_assessment_id TEXT NOT NULL,
                score_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (candidate_id) REFERENCES edge_candidates (candidate_id) ON DELETE CASCADE,
                FOREIGN KEY (novelty_assessment_id) REFERENCES novelty_assessments (assessment_id) ON DELETE CASCADE,
                FOREIGN KEY (score_id) REFERENCES edge_scores (score_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS discovery_summaries (
                summary_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                total_patterns INTEGER NOT NULL,
                total_clusters INTEGER NOT NULL,
                total_candidates INTEGER NOT NULL,
                total_validated INTEGER NOT NULL,
                total_rejected INTEGER NOT NULL,
                category_counts_json TEXT NOT NULL,
                tier_counts_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class PatternRepository:
    """Repository for EdgePattern instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, pattern: EdgePattern) -> EdgePattern:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO edge_patterns (
                    pattern_id, pattern_type, symbol, sample_size, effect_size,
                    statistical_significance, regime_consistency, observation_ids_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pattern.pattern_id,
                    pattern.pattern_type.value,
                    pattern.symbol,
                    pattern.sample_size,
                    pattern.effect_size,
                    pattern.statistical_significance,
                    pattern.regime_consistency,
                    json.dumps(pattern.observation_ids),
                    json.dumps(pattern.metadata),
                    pattern.canonical_hash,
                ),
            )
        return pattern

    def get_by_id(self, pattern_id: str) -> EdgePattern | None:
        cursor = self._conn.execute("SELECT * FROM edge_patterns WHERE pattern_id = ?", (pattern_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[EdgePattern]:
        cursor = self._conn.execute("SELECT * FROM edge_patterns")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EdgePattern:
        return EdgePattern(
            pattern_id=row[0],
            pattern_type=PatternType(row[1]),
            symbol=row[2],
            sample_size=int(row[3]),
            effect_size=float(row[4]),
            statistical_significance=float(row[5]),
            regime_consistency=float(row[6]),
            observation_ids=json.loads(row[7]),
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class ClusterRepository:
    """Repository for PatternCluster instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, cluster: PatternCluster) -> PatternCluster:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO pattern_clusters (
                    cluster_id, cluster_name, pattern_ids_json, centroid_pattern_id,
                    intra_cluster_similarity, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cluster.cluster_id,
                    cluster.cluster_name,
                    json.dumps(cluster.pattern_ids),
                    cluster.centroid_pattern_id,
                    cluster.intra_cluster_similarity,
                    json.dumps(cluster.metadata),
                    cluster.canonical_hash,
                ),
            )
        return cluster

    def get_by_id(self, cluster_id: str) -> PatternCluster | None:
        cursor = self._conn.execute("SELECT * FROM pattern_clusters WHERE cluster_id = ?", (cluster_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[PatternCluster]:
        cursor = self._conn.execute("SELECT * FROM pattern_clusters")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> PatternCluster:
        return PatternCluster(
            cluster_id=row[0],
            cluster_name=row[1],
            pattern_ids=json.loads(row[2]),
            centroid_pattern_id=row[3],
            intra_cluster_similarity=float(row[4]),
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class EdgeRepository:
    """Repository for EdgeCandidate instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, candidate: EdgeCandidate) -> EdgeCandidate:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO edge_candidates (
                    candidate_id, name, category, symbol, pattern_ids_json,
                    hypothesis_statement, confidence_level, observation_count,
                    timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.candidate_id,
                    candidate.name,
                    candidate.category.value,
                    candidate.symbol,
                    json.dumps(candidate.pattern_ids),
                    candidate.hypothesis_statement,
                    candidate.confidence_level,
                    candidate.observation_count,
                    candidate.timestamp,
                    json.dumps(candidate.metadata),
                    candidate.canonical_hash,
                ),
            )
        return candidate

    def get_by_id(self, candidate_id: str) -> EdgeCandidate | None:
        cursor = self._conn.execute("SELECT * FROM edge_candidates WHERE candidate_id = ?", (candidate_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[EdgeCandidate]:
        cursor = self._conn.execute("SELECT * FROM edge_candidates ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EdgeCandidate:
        return EdgeCandidate(
            candidate_id=row[0],
            name=row[1],
            category=EdgeCategory(row[2]),
            symbol=row[3],
            pattern_ids=json.loads(row[4]),
            hypothesis_statement=row[5],
            confidence_level=float(row[6]),
            observation_count=int(row[7]),
            timestamp=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class NoveltyRepository:
    """Repository for NoveltyAssessment instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, assessment: NoveltyAssessment) -> NoveltyAssessment:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO novelty_assessments (
                    assessment_id, candidate_id, max_similarity_score, closest_archived_edge_id,
                    status, is_novel, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment.assessment_id,
                    assessment.candidate_id,
                    assessment.max_similarity_score,
                    assessment.closest_archived_edge_id,
                    assessment.status.value,
                    1 if assessment.is_novel else 0,
                    json.dumps(assessment.metadata),
                    assessment.canonical_hash,
                ),
            )
        return assessment

    def get_by_id(self, assessment_id: str) -> NoveltyAssessment | None:
        cursor = self._conn.execute("SELECT * FROM novelty_assessments WHERE assessment_id = ?", (assessment_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[NoveltyAssessment]:
        cursor = self._conn.execute("SELECT * FROM novelty_assessments")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> NoveltyAssessment:
        return NoveltyAssessment(
            assessment_id=row[0],
            candidate_id=row[1],
            max_similarity_score=float(row[2]),
            closest_archived_edge_id=row[3],
            status=NoveltyStatus(row[4]),
            is_novel=bool(row[5]),
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ScoreRepository:
    """Repository for EdgeScore instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, score: EdgeScore) -> EdgeScore:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO edge_scores (
                    score_id, candidate_id, overall_score, support_score, stability_score,
                    consistency_score, robustness_score, live_compatibility_score, quality_tier,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    score.score_id,
                    score.candidate_id,
                    score.overall_score,
                    score.support_score,
                    score.stability_score,
                    score.consistency_score,
                    score.robustness_score,
                    score.live_compatibility_score,
                    score.quality_tier.value,
                    json.dumps(score.metadata),
                    score.canonical_hash,
                ),
            )
        return score

    def get_by_id(self, score_id: str) -> EdgeScore | None:
        cursor = self._conn.execute("SELECT * FROM edge_scores WHERE score_id = ?", (score_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[EdgeScore]:
        cursor = self._conn.execute("SELECT * FROM edge_scores")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EdgeScore:
        return EdgeScore(
            score_id=row[0],
            candidate_id=row[1],
            overall_score=float(row[2]),
            support_score=float(row[3]),
            stability_score=float(row[4]),
            consistency_score=float(row[5]),
            robustness_score=float(row[6]),
            live_compatibility_score=float(row[7]),
            quality_tier=QualityTier(row[8]),
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class DecisionRepository:
    """Repository for DiscoveryDecision instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, decision: DiscoveryDecision) -> DiscoveryDecision:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO discovery_decisions (
                    decision_id, candidate_id, status, rejection_reason, novelty_assessment_id,
                    score_id, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.candidate_id,
                    decision.status.value,
                    decision.rejection_reason.value,
                    decision.novelty_assessment_id,
                    decision.score_id,
                    decision.timestamp,
                    json.dumps(decision.metadata),
                    decision.canonical_hash,
                ),
            )
        return decision

    def get_by_id(self, decision_id: str) -> DiscoveryDecision | None:
        cursor = self._conn.execute("SELECT * FROM discovery_decisions WHERE decision_id = ?", (decision_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[DiscoveryDecision]:
        cursor = self._conn.execute("SELECT * FROM discovery_decisions ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> DiscoveryDecision:
        return DiscoveryDecision(
            decision_id=row[0],
            candidate_id=row[1],
            status=ValidationStatus(row[2]),
            rejection_reason=RejectionReason(row[3]),
            novelty_assessment_id=row[4],
            score_id=row[5],
            timestamp=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class SummaryRepository:
    """Repository for DiscoverySummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: DiscoverySummary) -> DiscoverySummary:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO discovery_summaries (
                    summary_id, timestamp, total_patterns, total_clusters, total_candidates,
                    total_validated, total_rejected, category_counts_json, tier_counts_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.timestamp,
                    summary.total_patterns,
                    summary.total_clusters,
                    summary.total_candidates,
                    summary.total_validated,
                    summary.total_rejected,
                    json.dumps(summary.category_counts),
                    json.dumps(summary.tier_counts),
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> DiscoverySummary | None:
        cursor = self._conn.execute("SELECT * FROM discovery_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[DiscoverySummary]:
        cursor = self._conn.execute("SELECT * FROM discovery_summaries ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> DiscoverySummary:
        return DiscoverySummary(
            summary_id=row[0],
            timestamp=row[1],
            total_patterns=int(row[2]),
            total_clusters=int(row[3]),
            total_candidates=int(row[4]),
            total_validated=int(row[5]),
            total_rejected=int(row[6]),
            category_counts=json.loads(row[7]),
            tier_counts=json.loads(row[8]),
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class EdgeDiscoveryPersistenceContext:
    """Unified Persistence Database Context wrapping all Edge Discovery repositories."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_edge_discovery_db(self.conn)
        self.patterns = PatternRepository(self.conn)
        self.clusters = ClusterRepository(self.conn)
        self.edges = EdgeRepository(self.conn)
        self.novelties = NoveltyRepository(self.conn)
        self.scores = ScoreRepository(self.conn)
        self.decisions = DecisionRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
