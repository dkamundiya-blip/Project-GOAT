"""
Project GOAT v0.7 — SQLite Persistence for Scientific Alpha Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- ScientificEdgeRepository
- EdgeEvidenceRepository
- EdgeScoreRepository
- EdgeRankingRepository
- EdgeReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.alpha.core.models import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    EdgeRanking,
    EdgeScore,
    ScientificEdge,
)


def init_alpha_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for Scientific Alpha Engine."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scientific_edges (
                edge_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                maturity TEXT NOT NULL,
                originating_hypotheses_json TEXT NOT NULL,
                originating_validations_json TEXT NOT NULL,
                originating_clusters_json TEXT NOT NULL,
                originating_patterns_json TEXT NOT NULL,
                originating_trends_json TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                reproducibility REAL NOT NULL,
                robustness REAL NOT NULL,
                stability REAL NOT NULL,
                discovery_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_evidence (
                evidence_id TEXT PRIMARY KEY,
                edge_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_reference TEXT NOT NULL,
                confidence REAL NOT NULL,
                reproducibility REAL NOT NULL,
                explanation TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (edge_id) REFERENCES scientific_edges(edge_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_scores (
                score_id TEXT PRIMARY KEY,
                edge_id TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                reproducibility_score REAL NOT NULL,
                robustness_score REAL NOT NULL,
                stability_score REAL NOT NULL,
                evidence_strength REAL NOT NULL,
                scientific_quality REAL NOT NULL,
                longevity_score REAL NOT NULL,
                conflict_penalty REAL NOT NULL,
                overall_edge_score REAL NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (edge_id) REFERENCES scientific_edges(edge_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_rankings (
                ranking_id TEXT PRIMARY KEY,
                ranked_edges_json TEXT NOT NULL,
                edge_scores_json TEXT NOT NULL,
                ranking_timestamp TEXT NOT NULL,
                ranking_rules_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_explainability_records (
                explanation_id TEXT PRIMARY KEY,
                edge_id TEXT NOT NULL,
                origin TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                supporting_hypotheses_json TEXT NOT NULL,
                supporting_experiments_json TEXT NOT NULL,
                supporting_studies_json TEXT NOT NULL,
                supporting_clusters_json TEXT NOT NULL,
                supporting_trends_json TEXT NOT NULL,
                supporting_reports_json TEXT NOT NULL,
                scientific_explanation TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (edge_id) REFERENCES scientific_edges(edge_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alpha_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class ScientificEdgeRepository:
    """Repository for storing and retrieving ScientificEdge models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_alpha_db(self.conn)

    def save_edge(self, edge: ScientificEdge) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO scientific_edges (
                    edge_id, title, description, maturity,
                    originating_hypotheses_json, originating_validations_json,
                    originating_clusters_json, originating_patterns_json,
                    originating_trends_json, supporting_evidence_json,
                    confidence, reproducibility, robustness, stability,
                    discovery_timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge.edge_id,
                    edge.title,
                    edge.description,
                    edge.maturity.value if hasattr(edge.maturity, "value") else str(edge.maturity),
                    json.dumps(edge.originating_hypotheses, sort_keys=True),
                    json.dumps(edge.originating_validations, sort_keys=True),
                    json.dumps(edge.originating_clusters, sort_keys=True),
                    json.dumps(edge.originating_patterns, sort_keys=True),
                    json.dumps(edge.originating_trends, sort_keys=True),
                    json.dumps(edge.supporting_evidence, sort_keys=True),
                    edge.confidence,
                    edge.reproducibility,
                    edge.robustness,
                    edge.stability,
                    edge.discovery_timestamp,
                    json.dumps(edge.metadata, sort_keys=True),
                    edge.canonical_hash,
                ),
            )

    def get_edge(self, edge_id: str) -> ScientificEdge | None:
        cursor = self.conn.execute(
            """
            SELECT edge_id, title, description, maturity,
                   originating_hypotheses_json, originating_validations_json,
                   originating_clusters_json, originating_patterns_json,
                   originating_trends_json, supporting_evidence_json,
                   confidence, reproducibility, robustness, stability,
                   discovery_timestamp, metadata_json, canonical_hash
            FROM scientific_edges WHERE edge_id = ?
            """,
            (edge_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ScientificEdge(
            edge_id=row[0],
            title=row[1],
            description=row[2],
            maturity=row[3],
            originating_hypotheses=json.loads(row[4]),
            originating_validations=json.loads(row[5]),
            originating_clusters=json.loads(row[6]),
            originating_patterns=json.loads(row[7]),
            originating_trends=json.loads(row[8]),
            supporting_evidence=json.loads(row[9]),
            confidence=row[10],
            reproducibility=row[11],
            robustness=row[12],
            stability=row[13],
            discovery_timestamp=row[14],
            metadata=json.loads(row[15]),
            canonical_hash=row[16],
        )

    def list_edges(self) -> list[ScientificEdge]:
        cursor = self.conn.execute("SELECT edge_id FROM scientific_edges ORDER BY edge_id ASC")
        edges = []
        for row in cursor.fetchall():
            e = self.get_edge(row[0])
            if e:
                edges.append(e)
        return edges


class EdgeEvidenceRepository:
    """Repository for storing and retrieving EdgeEvidence and EdgeExplainabilityRecord models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_alpha_db(self.conn)

    def save_evidence(self, evidence: EdgeEvidence) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO edge_evidence (
                    evidence_id, edge_id, source_type, source_reference,
                    confidence, reproducibility, explanation, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence.evidence_id,
                    evidence.edge_id,
                    evidence.source_type.value if hasattr(evidence.source_type, "value") else str(evidence.source_type),
                    evidence.source_reference,
                    evidence.confidence,
                    evidence.reproducibility,
                    evidence.explanation,
                    evidence.canonical_hash,
                ),
            )

    def get_evidence(self, evidence_id: str) -> EdgeEvidence | None:
        cursor = self.conn.execute(
            """
            SELECT evidence_id, edge_id, source_type, source_reference,
                   confidence, reproducibility, explanation, canonical_hash
            FROM edge_evidence WHERE evidence_id = ?
            """,
            (evidence_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return EdgeEvidence(
            evidence_id=row[0],
            edge_id=row[1],
            source_type=row[2],
            source_reference=row[3],
            confidence=row[4],
            reproducibility=row[5],
            explanation=row[6],
            canonical_hash=row[7],
        )

    def save_explanation(self, record: EdgeExplainabilityRecord) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO edge_explainability_records (
                    explanation_id, edge_id, origin, supporting_evidence_json,
                    supporting_hypotheses_json, supporting_experiments_json,
                    supporting_studies_json, supporting_clusters_json,
                    supporting_trends_json, supporting_reports_json,
                    scientific_explanation, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.explanation_id,
                    record.edge_id,
                    record.origin,
                    json.dumps(record.supporting_evidence, sort_keys=True),
                    json.dumps(record.supporting_hypotheses, sort_keys=True),
                    json.dumps(record.supporting_experiments, sort_keys=True),
                    json.dumps(record.supporting_studies, sort_keys=True),
                    json.dumps(record.supporting_clusters, sort_keys=True),
                    json.dumps(record.supporting_trends, sort_keys=True),
                    json.dumps(record.supporting_reports, sort_keys=True),
                    record.scientific_explanation,
                    record.canonical_hash,
                ),
            )

    def get_explanation(self, explanation_id: str) -> EdgeExplainabilityRecord | None:
        cursor = self.conn.execute(
            """
            SELECT explanation_id, edge_id, origin, supporting_evidence_json,
                   supporting_hypotheses_json, supporting_experiments_json,
                   supporting_studies_json, supporting_clusters_json,
                   supporting_trends_json, supporting_reports_json,
                   scientific_explanation, canonical_hash
            FROM edge_explainability_records WHERE explanation_id = ?
            """,
            (explanation_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return EdgeExplainabilityRecord(
            explanation_id=row[0],
            edge_id=row[1],
            origin=row[2],
            supporting_evidence=json.loads(row[3]),
            supporting_hypotheses=json.loads(row[4]),
            supporting_experiments=json.loads(row[5]),
            supporting_studies=json.loads(row[6]),
            supporting_clusters=json.loads(row[7]),
            supporting_trends=json.loads(row[8]),
            supporting_reports=json.loads(row[9]),
            scientific_explanation=row[10],
            canonical_hash=row[11],
        )


class EdgeScoreRepository:
    """Repository for storing and retrieving EdgeScore models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_alpha_db(self.conn)

    def save_score(self, score: EdgeScore) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO edge_scores (
                    score_id, edge_id, confidence_score, reproducibility_score,
                    robustness_score, stability_score, evidence_strength,
                    scientific_quality, longevity_score, conflict_penalty,
                    overall_edge_score, timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    score.score_id,
                    score.edge_id,
                    score.confidence_score,
                    score.reproducibility_score,
                    score.robustness_score,
                    score.stability_score,
                    score.evidence_strength,
                    score.scientific_quality,
                    score.longevity_score,
                    score.conflict_penalty,
                    score.overall_edge_score,
                    score.timestamp,
                    score.canonical_hash,
                ),
            )

    def get_score(self, score_id: str) -> EdgeScore | None:
        cursor = self.conn.execute(
            """
            SELECT score_id, edge_id, confidence_score, reproducibility_score,
                   robustness_score, stability_score, evidence_strength,
                   scientific_quality, longevity_score, conflict_penalty,
                   overall_edge_score, timestamp, canonical_hash
            FROM edge_scores WHERE score_id = ?
            """,
            (score_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return EdgeScore(
            score_id=row[0],
            edge_id=row[1],
            confidence_score=row[2],
            reproducibility_score=row[3],
            robustness_score=row[4],
            stability_score=row[5],
            evidence_strength=row[6],
            scientific_quality=row[7],
            longevity_score=row[8],
            conflict_penalty=row[9],
            overall_edge_score=row[10],
            timestamp=row[11],
            canonical_hash=row[12],
        )


class EdgeRankingRepository:
    """Repository for storing and retrieving EdgeRanking models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_alpha_db(self.conn)

    def save_ranking(self, ranking: EdgeRanking) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO edge_rankings (
                    ranking_id, ranked_edges_json, edge_scores_json,
                    ranking_timestamp, ranking_rules_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ranking.ranking_id,
                    json.dumps(ranking.ranked_edges, sort_keys=False),  # Preserve order
                    json.dumps([s.dict() for s in ranking.edge_scores], sort_keys=True),
                    ranking.ranking_timestamp,
                    json.dumps(ranking.ranking_rules, sort_keys=True),
                    json.dumps(ranking.metadata, sort_keys=True),
                    ranking.canonical_hash,
                ),
            )

    def get_ranking(self, ranking_id: str) -> EdgeRanking | None:
        cursor = self.conn.execute(
            """
            SELECT ranking_id, ranked_edges_json, edge_scores_json,
                   ranking_timestamp, ranking_rules_json, metadata_json, canonical_hash
            FROM edge_rankings WHERE ranking_id = ?
            """,
            (ranking_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return EdgeRanking(
            ranking_id=row[0],
            ranked_edges=json.loads(row[1]),
            edge_scores=[EdgeScore(**s) for s in json.loads(row[2])],
            ranking_timestamp=row[3],
            ranking_rules=json.loads(row[4]),
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class EdgeReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_alpha_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO alpha_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM alpha_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
