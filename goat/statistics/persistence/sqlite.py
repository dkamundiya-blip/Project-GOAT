"""
Project GOAT v0.9 — SQLite Persistence Repositories for Statistical Evaluation Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.statistics.core.enums import (
    EvaluationConfidence,
    EvaluationStatus,
    ScientificDecision,
)
from goat.statistics.core.models import (
    ConfidenceAssessment,
    EvaluationDecision,
    EvaluationSummary,
    ExpectancyAssessment,
    SignificanceAssessment,
    StatisticalEvaluation,
)


def init_statistics_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and pragmas for Statistical Evaluation subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS statistical_evaluations (
                evaluation_id TEXT PRIMARY KEY,
                experiment_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                status TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                confidence_rating TEXT NOT NULL,
                p_value REAL NOT NULL,
                effect_size REAL NOT NULL,
                expected_value REAL NOT NULL,
                sample_size INTEGER NOT NULL,
                evaluator TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS confidence_assessments (
                confidence_id TEXT PRIMARY KEY,
                evaluation_id TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                lower_bound REAL NOT NULL,
                upper_bound REAL NOT NULL,
                margin_of_error REAL NOT NULL,
                sample_size INTEGER NOT NULL,
                confidence_rating TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS significance_assessments (
                significance_id TEXT PRIMARY KEY,
                evaluation_id TEXT NOT NULL,
                p_value REAL NOT NULL,
                test_statistic REAL NOT NULL,
                alpha_threshold REAL NOT NULL,
                is_significant INTEGER NOT NULL,
                multiple_comparison_correction TEXT NOT NULL,
                adjusted_p_value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expectancy_assessments (
                expectancy_id TEXT PRIMARY KEY,
                evaluation_id TEXT NOT NULL,
                expected_value REAL NOT NULL,
                win_rate REAL NOT NULL,
                loss_rate REAL NOT NULL,
                average_gain REAL NOT NULL,
                average_loss REAL NOT NULL,
                profit_factor REAL NOT NULL,
                sample_size INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_decisions (
                decision_id TEXT PRIMARY KEY,
                evaluation_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence_rating TEXT NOT NULL,
                decision_rationale TEXT NOT NULL,
                authorizer TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_summaries (
                summary_id TEXT PRIMARY KEY,
                total_evaluations INTEGER NOT NULL,
                total_decisions INTEGER NOT NULL,
                decision_counts_json TEXT NOT NULL,
                confidence_counts_json TEXT NOT NULL,
                status_counts_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class StatisticalRepository:
    """Repository for persisting and querying StatisticalEvaluation instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, evaluation: StatisticalEvaluation) -> StatisticalEvaluation:
        """Insert or replace a StatisticalEvaluation."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO statistical_evaluations (
                    evaluation_id, experiment_id, hypothesis_id, status, decision,
                    confidence_level, confidence_rating, p_value, effect_size, expected_value,
                    sample_size, evaluator, timestamp, tags_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evaluation.evaluation_id,
                    evaluation.experiment_id,
                    evaluation.hypothesis_id,
                    evaluation.status.value,
                    evaluation.decision.value,
                    evaluation.confidence_level,
                    evaluation.confidence_rating.value,
                    evaluation.p_value,
                    evaluation.effect_size,
                    evaluation.expected_value,
                    evaluation.sample_size,
                    evaluation.evaluator,
                    evaluation.timestamp,
                    json.dumps(evaluation.tags),
                    json.dumps(evaluation.metadata),
                    evaluation.canonical_hash,
                ),
            )
        return evaluation

    def get_by_id(self, evaluation_id: str) -> StatisticalEvaluation | None:
        """Fetch evaluation by ID."""
        cursor = self._conn.execute("SELECT * FROM statistical_evaluations WHERE evaluation_id = ?", (evaluation_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[StatisticalEvaluation]:
        """Fetch all evaluations."""
        cursor = self._conn.execute("SELECT * FROM statistical_evaluations ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> StatisticalEvaluation:
        return StatisticalEvaluation(
            evaluation_id=row[0],
            experiment_id=row[1],
            hypothesis_id=row[2],
            status=EvaluationStatus(row[3]),
            decision=ScientificDecision(row[4]),
            confidence_level=row[5],
            confidence_rating=EvaluationConfidence(row[6]),
            p_value=row[7],
            effect_size=row[8],
            expected_value=row[9],
            sample_size=row[10],
            evaluator=row[11],
            timestamp=row[12],
            tags=json.loads(row[13]),
            metadata=json.loads(row[14]),
            canonical_hash=row[15],
        )


class ConfidenceRepository:
    """Repository for persisting and querying ConfidenceAssessment instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, confidence: ConfidenceAssessment) -> ConfidenceAssessment:
        """Insert or replace a ConfidenceAssessment."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO confidence_assessments (
                    confidence_id, evaluation_id, confidence_level, lower_bound, upper_bound,
                    margin_of_error, sample_size, confidence_rating, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    confidence.confidence_id,
                    confidence.evaluation_id,
                    confidence.confidence_level,
                    confidence.lower_bound,
                    confidence.upper_bound,
                    confidence.margin_of_error,
                    confidence.sample_size,
                    confidence.confidence_rating.value,
                    confidence.timestamp,
                    json.dumps(confidence.metadata),
                    confidence.canonical_hash,
                ),
            )
        return confidence

    def get_by_id(self, confidence_id: str) -> ConfidenceAssessment | None:
        """Fetch confidence assessment by ID."""
        cursor = self._conn.execute("SELECT * FROM confidence_assessments WHERE confidence_id = ?", (confidence_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_evaluation_id(self, evaluation_id: str) -> ConfidenceAssessment | None:
        """Fetch confidence assessment by target evaluation ID."""
        cursor = self._conn.execute("SELECT * FROM confidence_assessments WHERE evaluation_id = ?", (evaluation_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ConfidenceAssessment:
        return ConfidenceAssessment(
            confidence_id=row[0],
            evaluation_id=row[1],
            confidence_level=row[2],
            lower_bound=row[3],
            upper_bound=row[4],
            margin_of_error=row[5],
            sample_size=row[6],
            confidence_rating=EvaluationConfidence(row[7]),
            timestamp=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class SignificanceRepository:
    """Repository for persisting and querying SignificanceAssessment instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, significance: SignificanceAssessment) -> SignificanceAssessment:
        """Insert or replace a SignificanceAssessment."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO significance_assessments (
                    significance_id, evaluation_id, p_value, test_statistic, alpha_threshold,
                    is_significant, multiple_comparison_correction, adjusted_p_value, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    significance.significance_id,
                    significance.evaluation_id,
                    significance.p_value,
                    significance.test_statistic,
                    significance.alpha_threshold,
                    1 if significance.is_significant else 0,
                    significance.multiple_comparison_correction,
                    significance.adjusted_p_value,
                    significance.timestamp,
                    json.dumps(significance.metadata),
                    significance.canonical_hash,
                ),
            )
        return significance

    def get_by_id(self, significance_id: str) -> SignificanceAssessment | None:
        """Fetch significance assessment by ID."""
        cursor = self._conn.execute("SELECT * FROM significance_assessments WHERE significance_id = ?", (significance_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_evaluation_id(self, evaluation_id: str) -> SignificanceAssessment | None:
        """Fetch significance assessment by target evaluation ID."""
        cursor = self._conn.execute("SELECT * FROM significance_assessments WHERE evaluation_id = ?", (evaluation_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> SignificanceAssessment:
        return SignificanceAssessment(
            significance_id=row[0],
            evaluation_id=row[1],
            p_value=row[2],
            test_statistic=row[3],
            alpha_threshold=row[4],
            is_significant=bool(row[5]),
            multiple_comparison_correction=row[6],
            adjusted_p_value=row[7],
            timestamp=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class ExpectancyRepository:
    """Repository for persisting and querying ExpectancyAssessment instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, expectancy: ExpectancyAssessment) -> ExpectancyAssessment:
        """Insert or replace an ExpectancyAssessment."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO expectancy_assessments (
                    expectancy_id, evaluation_id, expected_value, win_rate, loss_rate,
                    average_gain, average_loss, profit_factor, sample_size, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    expectancy.expectancy_id,
                    expectancy.evaluation_id,
                    expectancy.expected_value,
                    expectancy.win_rate,
                    expectancy.loss_rate,
                    expectancy.average_gain,
                    expectancy.average_loss,
                    expectancy.profit_factor,
                    expectancy.sample_size,
                    expectancy.timestamp,
                    json.dumps(expectancy.metadata),
                    expectancy.canonical_hash,
                ),
            )
        return expectancy

    def get_by_id(self, expectancy_id: str) -> ExpectancyAssessment | None:
        """Fetch expectancy assessment by ID."""
        cursor = self._conn.execute("SELECT * FROM expectancy_assessments WHERE expectancy_id = ?", (expectancy_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_evaluation_id(self, evaluation_id: str) -> ExpectancyAssessment | None:
        """Fetch expectancy assessment by target evaluation ID."""
        cursor = self._conn.execute("SELECT * FROM expectancy_assessments WHERE evaluation_id = ?", (evaluation_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ExpectancyAssessment:
        return ExpectancyAssessment(
            expectancy_id=row[0],
            evaluation_id=row[1],
            expected_value=row[2],
            win_rate=row[3],
            loss_rate=row[4],
            average_gain=row[5],
            average_loss=row[6],
            profit_factor=row[7],
            sample_size=row[8],
            timestamp=row[9],
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )


class DecisionRepository:
    """Repository for persisting and querying EvaluationDecision instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, decision: EvaluationDecision) -> EvaluationDecision:
        """Insert or replace an EvaluationDecision."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO evaluation_decisions (
                    decision_id, evaluation_id, hypothesis_id, decision, confidence_rating,
                    decision_rationale, authorizer, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.evaluation_id,
                    decision.hypothesis_id,
                    decision.decision.value,
                    decision.confidence_rating.value,
                    decision.decision_rationale,
                    decision.authorizer,
                    decision.timestamp,
                    json.dumps(decision.metadata),
                    decision.canonical_hash,
                ),
            )
        return decision

    def get_by_id(self, decision_id: str) -> EvaluationDecision | None:
        """Fetch decision by ID."""
        cursor = self._conn.execute("SELECT * FROM evaluation_decisions WHERE decision_id = ?", (decision_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[EvaluationDecision]:
        """Fetch all decisions."""
        cursor = self._conn.execute("SELECT * FROM evaluation_decisions ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EvaluationDecision:
        return EvaluationDecision(
            decision_id=row[0],
            evaluation_id=row[1],
            hypothesis_id=row[2],
            decision=ScientificDecision(row[3]),
            confidence_rating=EvaluationConfidence(row[4]),
            decision_rationale=row[5],
            authorizer=row[6],
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class SummaryRepository:
    """Repository for persisting and querying EvaluationSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: EvaluationSummary) -> EvaluationSummary:
        """Insert or replace an EvaluationSummary."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO evaluation_summaries (
                    summary_id, total_evaluations, total_decisions, decision_counts_json,
                    confidence_counts_json, status_counts_json, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.total_evaluations,
                    summary.total_decisions,
                    json.dumps(summary.decision_counts),
                    json.dumps(summary.confidence_counts),
                    json.dumps(summary.status_counts),
                    summary.timestamp,
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> EvaluationSummary | None:
        """Fetch summary by ID."""
        cursor = self._conn.execute("SELECT * FROM evaluation_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EvaluationSummary:
        return EvaluationSummary(
            summary_id=row[0],
            total_evaluations=row[1],
            total_decisions=row[2],
            decision_counts=json.loads(row[3]),
            confidence_counts=json.loads(row[4]),
            status_counts=json.loads(row[5]),
            timestamp=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class StatisticalPersistenceContext:
    """Unified Persistence Context wrapping SQLite repositories for statistical evaluation subsystem."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_statistics_db(self.conn)
        self.evaluations = StatisticalRepository(self.conn)
        self.confidence = ConfidenceRepository(self.conn)
        self.significance = SignificanceRepository(self.conn)
        self.expectancy = ExpectancyRepository(self.conn)
        self.decisions = DecisionRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
