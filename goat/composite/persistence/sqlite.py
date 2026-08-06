"""
Project GOAT v0.7 — SQLite Persistence for Composite Edge Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- CompositeRepository
- CompositeEvidenceRepository
- CompositeScoreRepository
- CompositeRankingRepository
- CompositeReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
)


def init_composite_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for Composite Edge Engine."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS composite_edges (
                composite_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                participating_edges_json TEXT NOT NULL,
                participating_hypotheses_json TEXT NOT NULL,
                participating_validations_json TEXT NOT NULL,
                participating_clusters_json TEXT NOT NULL,
                participating_patterns_json TEXT NOT NULL,
                participating_regimes_json TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                creation_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS composite_evidence (
                evidence_id TEXT PRIMARY KEY,
                composite_id TEXT NOT NULL,
                contributing_edge TEXT NOT NULL,
                contribution_strength REAL NOT NULL,
                explanation TEXT NOT NULL,
                supporting_sources_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (composite_id) REFERENCES composite_edges(composite_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS composite_scores (
                score_id TEXT PRIMARY KEY,
                composite_id TEXT NOT NULL,
                synergy_score REAL NOT NULL,
                robustness_score REAL NOT NULL,
                stability_score REAL NOT NULL,
                diversity_score REAL NOT NULL,
                conflict_penalty REAL NOT NULL,
                explainability_score REAL NOT NULL,
                reproducibility_score REAL NOT NULL,
                overall_score REAL NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (composite_id) REFERENCES composite_edges(composite_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS composite_rankings (
                ranking_id TEXT PRIMARY KEY,
                ranked_composites_json TEXT NOT NULL,
                composite_scores_json TEXT NOT NULL,
                ranking_timestamp TEXT NOT NULL,
                ranking_rules_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS composite_explainability_records (
                explanation_id TEXT PRIMARY KEY,
                composite_id TEXT NOT NULL,
                participating_edges_json TEXT NOT NULL,
                supporting_hypotheses_json TEXT NOT NULL,
                supporting_validations_json TEXT NOT NULL,
                supporting_knowledge_json TEXT NOT NULL,
                supporting_trends_json TEXT NOT NULL,
                supporting_regimes_json TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                scientific_explanation TEXT NOT NULL,
                compatibility_explanation TEXT NOT NULL,
                conflict_explanation TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (composite_id) REFERENCES composite_edges(composite_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS composite_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class CompositeRepository:
    """Repository for storing and retrieving CompositeEdge models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_composite_db(self.conn)

    def save_composite(self, composite: CompositeEdge) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO composite_edges (
                    composite_id, title, description, participating_edges_json,
                    participating_hypotheses_json, participating_validations_json,
                    participating_clusters_json, participating_patterns_json,
                    participating_regimes_json, supporting_evidence_json,
                    creation_timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    composite.composite_id,
                    composite.title,
                    composite.description,
                    json.dumps(composite.participating_edges, sort_keys=True),
                    json.dumps(composite.participating_hypotheses, sort_keys=True),
                    json.dumps(composite.participating_validations, sort_keys=True),
                    json.dumps(composite.participating_clusters, sort_keys=True),
                    json.dumps(composite.participating_patterns, sort_keys=True),
                    json.dumps(composite.participating_regimes, sort_keys=True),
                    json.dumps(composite.supporting_evidence, sort_keys=True),
                    composite.creation_timestamp,
                    json.dumps(composite.metadata, sort_keys=True),
                    composite.canonical_hash,
                ),
            )

    def get_composite(self, composite_id: str) -> CompositeEdge | None:
        cursor = self.conn.execute(
            """
            SELECT composite_id, title, description, participating_edges_json,
                   participating_hypotheses_json, participating_validations_json,
                   participating_clusters_json, participating_patterns_json,
                   participating_regimes_json, supporting_evidence_json,
                   creation_timestamp, metadata_json, canonical_hash
            FROM composite_edges WHERE composite_id = ?
            """,
            (composite_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return CompositeEdge(
            composite_id=row[0],
            title=row[1],
            description=row[2],
            participating_edges=json.loads(row[3]),
            participating_hypotheses=json.loads(row[4]),
            participating_validations=json.loads(row[5]),
            participating_clusters=json.loads(row[6]),
            participating_patterns=json.loads(row[7]),
            participating_regimes=json.loads(row[8]),
            supporting_evidence=json.loads(row[9]),
            creation_timestamp=row[10],
            metadata=json.loads(row[11]),
            canonical_hash=row[12],
        )

    def list_composites(self) -> list[CompositeEdge]:
        cursor = self.conn.execute("SELECT composite_id FROM composite_edges ORDER BY composite_id ASC")
        composites = []
        for row in cursor.fetchall():
            c = self.get_composite(row[0])
            if c:
                composites.append(c)
        return composites


class CompositeEvidenceRepository:
    """Repository for storing and retrieving CompositeEvidence and CompositeExplainabilityRecord models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_composite_db(self.conn)

    def save_evidence(self, evidence: CompositeEvidence) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO composite_evidence (
                    evidence_id, composite_id, contributing_edge,
                    contribution_strength, explanation, supporting_sources_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence.evidence_id,
                    evidence.composite_id,
                    evidence.contributing_edge,
                    evidence.contribution_strength,
                    evidence.explanation,
                    json.dumps(evidence.supporting_sources, sort_keys=True),
                    evidence.canonical_hash,
                ),
            )

    def get_evidence(self, evidence_id: str) -> CompositeEvidence | None:
        cursor = self.conn.execute(
            """
            SELECT evidence_id, composite_id, contributing_edge,
                   contribution_strength, explanation, supporting_sources_json, canonical_hash
            FROM composite_evidence WHERE evidence_id = ?
            """,
            (evidence_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return CompositeEvidence(
            evidence_id=row[0],
            composite_id=row[1],
            contributing_edge=row[2],
            contribution_strength=row[3],
            explanation=row[4],
            supporting_sources=json.loads(row[5]),
            canonical_hash=row[6],
        )

    def save_explanation(self, record: CompositeExplainabilityRecord) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO composite_explainability_records (
                    explanation_id, composite_id, participating_edges_json,
                    supporting_hypotheses_json, supporting_validations_json,
                    supporting_knowledge_json, supporting_trends_json,
                    supporting_regimes_json, supporting_evidence_json,
                    scientific_explanation, compatibility_explanation,
                    conflict_explanation, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.explanation_id,
                    record.composite_id,
                    json.dumps(record.participating_edges, sort_keys=True),
                    json.dumps(record.supporting_hypotheses, sort_keys=True),
                    json.dumps(record.supporting_validations, sort_keys=True),
                    json.dumps(record.supporting_knowledge, sort_keys=True),
                    json.dumps(record.supporting_trends, sort_keys=True),
                    json.dumps(record.supporting_regimes, sort_keys=True),
                    json.dumps(record.supporting_evidence, sort_keys=True),
                    record.scientific_explanation,
                    record.compatibility_explanation,
                    record.conflict_explanation,
                    record.canonical_hash,
                ),
            )

    def get_explanation(self, explanation_id: str) -> CompositeExplainabilityRecord | None:
        cursor = self.conn.execute(
            """
            SELECT explanation_id, composite_id, participating_edges_json,
                   supporting_hypotheses_json, supporting_validations_json,
                   supporting_knowledge_json, supporting_trends_json,
                   supporting_regimes_json, supporting_evidence_json,
                   scientific_explanation, compatibility_explanation,
                   conflict_explanation, canonical_hash
            FROM composite_explainability_records WHERE explanation_id = ?
            """,
            (explanation_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return CompositeExplainabilityRecord(
            explanation_id=row[0],
            composite_id=row[1],
            participating_edges=json.loads(row[2]),
            supporting_hypotheses=json.loads(row[3]),
            supporting_validations=json.loads(row[4]),
            supporting_knowledge=json.loads(row[5]),
            supporting_trends=json.loads(row[6]),
            supporting_regimes=json.loads(row[7]),
            supporting_evidence=json.loads(row[8]),
            scientific_explanation=row[9],
            compatibility_explanation=row[10],
            conflict_explanation=row[11],
            canonical_hash=row[12],
        )


class CompositeScoreRepository:
    """Repository for storing and retrieving CompositeScore models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_composite_db(self.conn)

    def save_score(self, score: CompositeScore) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO composite_scores (
                    score_id, composite_id, synergy_score, robustness_score,
                    stability_score, diversity_score, conflict_penalty,
                    explainability_score, reproducibility_score, overall_score,
                    timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    score.score_id,
                    score.composite_id,
                    score.synergy_score,
                    score.robustness_score,
                    score.stability_score,
                    score.diversity_score,
                    score.conflict_penalty,
                    score.explainability_score,
                    score.reproducibility_score,
                    score.overall_score,
                    score.timestamp,
                    score.canonical_hash,
                ),
            )

    def get_score(self, score_id: str) -> CompositeScore | None:
        cursor = self.conn.execute(
            """
            SELECT score_id, composite_id, synergy_score, robustness_score,
                   stability_score, diversity_score, conflict_penalty,
                   explainability_score, reproducibility_score, overall_score,
                   timestamp, canonical_hash
            FROM composite_scores WHERE score_id = ?
            """,
            (score_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return CompositeScore(
            score_id=row[0],
            composite_id=row[1],
            synergy_score=row[2],
            robustness_score=row[3],
            stability_score=row[4],
            diversity_score=row[5],
            conflict_penalty=row[6],
            explainability_score=row[7],
            reproducibility_score=row[8],
            overall_score=row[9],
            timestamp=row[10],
            canonical_hash=row[11],
        )


class CompositeRankingRepository:
    """Repository for storing and retrieving CompositeRanking models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_composite_db(self.conn)

    def save_ranking(self, ranking: CompositeRanking) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO composite_rankings (
                    ranking_id, ranked_composites_json, composite_scores_json,
                    ranking_timestamp, ranking_rules_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ranking.ranking_id,
                    json.dumps(ranking.ranked_composites, sort_keys=False),
                    json.dumps([s.dict() for s in ranking.composite_scores], sort_keys=True),
                    ranking.ranking_timestamp,
                    json.dumps(ranking.ranking_rules, sort_keys=True),
                    json.dumps(ranking.metadata, sort_keys=True),
                    ranking.canonical_hash,
                ),
            )

    def get_ranking(self, ranking_id: str) -> CompositeRanking | None:
        cursor = self.conn.execute(
            """
            SELECT ranking_id, ranked_composites_json, composite_scores_json,
                   ranking_timestamp, ranking_rules_json, metadata_json, canonical_hash
            FROM composite_rankings WHERE ranking_id = ?
            """,
            (ranking_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return CompositeRanking(
            ranking_id=row[0],
            ranked_composites=json.loads(row[1]),
            composite_scores=[CompositeScore(**s) for s in json.loads(row[2])],
            ranking_timestamp=row[3],
            ranking_rules=json.loads(row[4]),
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class CompositeReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_composite_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO composite_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM composite_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
