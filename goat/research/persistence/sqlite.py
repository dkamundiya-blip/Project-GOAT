"""
Project GOAT v0.9 — SQLite Persistence Repositories for Research Hypothesis Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.research.core.enums import (
    EvidenceLevel,
    HypothesisPriority,
    HypothesisStatus,
)
from goat.research.core.models import (
    HypothesisApproval,
    HypothesisRegistrySummary,
    HypothesisRevision,
    HypothesisValidation,
    ScientificHypothesis,
)


def init_research_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and pragmas for Research Hypothesis subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scientific_hypotheses (
                hypothesis_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                research_question TEXT NOT NULL,
                null_hypothesis TEXT NOT NULL,
                alternative_hypothesis TEXT NOT NULL,
                expected_behaviour TEXT NOT NULL,
                independent_variables_json TEXT NOT NULL,
                dependent_variables_json TEXT NOT NULL,
                assumptions_json TEXT NOT NULL,
                risk_statement TEXT NOT NULL,
                success_criteria_json TEXT NOT NULL,
                failure_criteria_json TEXT NOT NULL,
                author TEXT NOT NULL,
                created_timestamp TEXT NOT NULL,
                updated_timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                evidence_level TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hypothesis_revisions (
                revision_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                previous_hash TEXT NOT NULL,
                change_summary TEXT NOT NULL,
                author TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (hypothesis_id) REFERENCES scientific_hypotheses(hypothesis_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hypothesis_validations (
                validation_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                is_valid INTEGER NOT NULL,
                rule_results_json TEXT NOT NULL,
                errors_json TEXT NOT NULL,
                warnings_json TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (hypothesis_id) REFERENCES scientific_hypotheses(hypothesis_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hypothesis_approvals (
                approval_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                approver TEXT NOT NULL,
                status TEXT NOT NULL,
                approval_notes TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (hypothesis_id) REFERENCES scientific_hypotheses(hypothesis_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hypothesis_registry_summaries (
                summary_id TEXT PRIMARY KEY,
                total_hypotheses INTEGER NOT NULL,
                status_counts_json TEXT NOT NULL,
                priority_counts_json TEXT NOT NULL,
                evidence_level_counts_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class HypothesisRepository:
    """Repository for persisting and querying ScientificHypothesis instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, hypothesis: ScientificHypothesis) -> ScientificHypothesis:
        """Insert or replace a ScientificHypothesis record."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO scientific_hypotheses (
                    hypothesis_id, title, research_question, null_hypothesis, alternative_hypothesis,
                    expected_behaviour, independent_variables_json, dependent_variables_json, assumptions_json,
                    risk_statement, success_criteria_json, failure_criteria_json, author, created_timestamp,
                    updated_timestamp, status, priority, evidence_level, revision_number, tags_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    hypothesis.hypothesis_id,
                    hypothesis.title,
                    hypothesis.research_question,
                    hypothesis.null_hypothesis,
                    hypothesis.alternative_hypothesis,
                    hypothesis.expected_behaviour,
                    json.dumps(hypothesis.independent_variables),
                    json.dumps(hypothesis.dependent_variables),
                    json.dumps(hypothesis.assumptions),
                    hypothesis.risk_statement,
                    json.dumps(hypothesis.success_criteria),
                    json.dumps(hypothesis.failure_criteria),
                    hypothesis.author,
                    hypothesis.created_timestamp,
                    hypothesis.updated_timestamp,
                    hypothesis.status.value,
                    hypothesis.priority.value,
                    hypothesis.evidence_level.value,
                    hypothesis.revision_number,
                    json.dumps(hypothesis.tags),
                    json.dumps(hypothesis.metadata),
                    hypothesis.canonical_hash,
                ),
            )
        return hypothesis

    def get_by_id(self, hypothesis_id: str) -> ScientificHypothesis | None:
        """Fetch a ScientificHypothesis by hypothesis_id."""
        cursor = self._conn.execute(
            "SELECT * FROM scientific_hypotheses WHERE hypothesis_id = ?",
            (hypothesis_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ScientificHypothesis]:
        """Fetch all ScientificHypothesis records sorted by created_timestamp."""
        cursor = self._conn.execute("SELECT * FROM scientific_hypotheses ORDER BY created_timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def delete_by_id(self, hypothesis_id: str) -> bool:
        """Delete a hypothesis record by ID."""
        with self._conn:
            cursor = self._conn.execute("DELETE FROM scientific_hypotheses WHERE hypothesis_id = ?", (hypothesis_id,))
            return cursor.rowcount > 0

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ScientificHypothesis:
        return ScientificHypothesis(
            hypothesis_id=row[0],
            title=row[1],
            research_question=row[2],
            null_hypothesis=row[3],
            alternative_hypothesis=row[4],
            expected_behaviour=row[5],
            independent_variables=json.loads(row[6]),
            dependent_variables=json.loads(row[7]),
            assumptions=json.loads(row[8]),
            risk_statement=row[9],
            success_criteria=json.loads(row[10]),
            failure_criteria=json.loads(row[11]),
            author=row[12],
            created_timestamp=row[13],
            updated_timestamp=row[14],
            status=HypothesisStatus(row[15]),
            priority=HypothesisPriority(row[16]),
            evidence_level=EvidenceLevel(row[17]),
            revision_number=row[18],
            tags=json.loads(row[19]),
            metadata=json.loads(row[20]),
            canonical_hash=row[21],
        )


class RevisionRepository:
    """Repository for persisting and querying HypothesisRevision instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, revision: HypothesisRevision) -> HypothesisRevision:
        """Insert or replace a HypothesisRevision record."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO hypothesis_revisions (
                    revision_id, hypothesis_id, revision_number, previous_hash, change_summary,
                    author, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    revision.revision_id,
                    revision.hypothesis_id,
                    revision.revision_number,
                    revision.previous_hash,
                    revision.change_summary,
                    revision.author,
                    revision.timestamp,
                    json.dumps(revision.metadata),
                    revision.canonical_hash,
                ),
            )
        return revision

    def get_by_hypothesis_id(self, hypothesis_id: str) -> list[HypothesisRevision]:
        """Fetch all revisions for a hypothesis sorted by revision_number."""
        cursor = self._conn.execute(
            "SELECT * FROM hypothesis_revisions WHERE hypothesis_id = ? ORDER BY revision_number ASC",
            (hypothesis_id,),
        )
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> HypothesisRevision:
        return HypothesisRevision(
            revision_id=row[0],
            hypothesis_id=row[1],
            revision_number=row[2],
            previous_hash=row[3],
            change_summary=row[4],
            author=row[5],
            timestamp=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class ValidationRepository:
    """Repository for persisting and querying HypothesisValidation instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, validation: HypothesisValidation) -> HypothesisValidation:
        """Insert or replace a HypothesisValidation record."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO hypothesis_validations (
                    validation_id, hypothesis_id, is_valid, rule_results_json, errors_json,
                    warnings_json, reviewer, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    validation.validation_id,
                    validation.hypothesis_id,
                    1 if validation.is_valid else 0,
                    json.dumps(validation.validation_rule_results),
                    json.dumps(validation.validation_errors),
                    json.dumps(validation.validation_warnings),
                    validation.reviewer,
                    validation.timestamp,
                    json.dumps(validation.metadata),
                    validation.canonical_hash,
                ),
            )
        return validation

    def get_by_hypothesis_id(self, hypothesis_id: str) -> list[HypothesisValidation]:
        """Fetch all validations for a hypothesis sorted by timestamp."""
        cursor = self._conn.execute(
            "SELECT * FROM hypothesis_validations WHERE hypothesis_id = ? ORDER BY timestamp ASC",
            (hypothesis_id,),
        )
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> HypothesisValidation:
        return HypothesisValidation(
            validation_id=row[0],
            hypothesis_id=row[1],
            is_valid=bool(row[2]),
            validation_rule_results=json.loads(row[3]),
            validation_errors=json.loads(row[4]),
            validation_warnings=json.loads(row[5]),
            reviewer=row[6],
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class ApprovalRepository:
    """Repository for persisting and querying HypothesisApproval instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, approval: HypothesisApproval) -> HypothesisApproval:
        """Insert or replace a HypothesisApproval record."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO hypothesis_approvals (
                    approval_id, hypothesis_id, approver, status, approval_notes,
                    timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval.approval_id,
                    approval.hypothesis_id,
                    approval.approver,
                    approval.status.value,
                    approval.approval_notes,
                    approval.timestamp,
                    json.dumps(approval.metadata),
                    approval.canonical_hash,
                ),
            )
        return approval

    def get_by_hypothesis_id(self, hypothesis_id: str) -> list[HypothesisApproval]:
        """Fetch all approval decisions for a hypothesis sorted by timestamp."""
        cursor = self._conn.execute(
            "SELECT * FROM hypothesis_approvals WHERE hypothesis_id = ? ORDER BY timestamp ASC",
            (hypothesis_id,),
        )
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> HypothesisApproval:
        return HypothesisApproval(
            approval_id=row[0],
            hypothesis_id=row[1],
            approver=row[2],
            status=HypothesisStatus(row[3]),
            approval_notes=row[4],
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class SummaryRepository:
    """Repository for persisting and querying HypothesisRegistrySummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: HypothesisRegistrySummary) -> HypothesisRegistrySummary:
        """Insert or replace a HypothesisRegistrySummary record."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO hypothesis_registry_summaries (
                    summary_id, total_hypotheses, status_counts_json, priority_counts_json,
                    evidence_level_counts_json, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.total_hypotheses,
                    json.dumps(summary.status_counts),
                    json.dumps(summary.priority_counts),
                    json.dumps(summary.evidence_level_counts),
                    summary.timestamp,
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> HypothesisRegistrySummary | None:
        """Fetch a summary by summary_id."""
        cursor = self._conn.execute(
            "SELECT * FROM hypothesis_registry_summaries WHERE summary_id = ?",
            (summary_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> HypothesisRegistrySummary:
        return HypothesisRegistrySummary(
            summary_id=row[0],
            total_hypotheses=row[1],
            status_counts=json.loads(row[2]),
            priority_counts=json.loads(row[3]),
            evidence_level_counts=json.loads(row[4]),
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ResearchPersistenceContext:
    """Unified Persistence Context wrapping SQLite repositories for research hypotheses."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_research_db(self.conn)
        self.hypotheses = HypothesisRepository(self.conn)
        self.revisions = RevisionRepository(self.conn)
        self.validations = ValidationRepository(self.conn)
        self.approvals = ApprovalRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
