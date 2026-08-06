"""
Project GOAT v0.9 — SQLite Persistence Repositories for Edge Promotion & Retirement Governance Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.governance.core.enums import (
    EdgeStatus,
    GovernanceDecisionOutcome,
    GovernanceReason,
)
from goat.governance.core.models import (
    EdgeCandidate,
    GovernanceAudit,
    GovernanceDecision,
    GovernanceSummary,
    PromotionAssessment,
    RetirementAssessment,
)


def init_governance_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and pragmas for Governance subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edge_candidates (
                edge_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                evaluation_id TEXT NOT NULL,
                experiment_id TEXT NOT NULL,
                validation_session_id TEXT NOT NULL,
                evidence_ids_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS promotion_assessments (
                assessment_id TEXT PRIMARY KEY,
                edge_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                is_hypothesis_passed INTEGER NOT NULL,
                is_evidence_complete INTEGER NOT NULL,
                is_experiment_complete INTEGER NOT NULL,
                is_statistics_complete INTEGER NOT NULL,
                is_live_validation_complete INTEGER NOT NULL,
                is_constitution_satisfied INTEGER NOT NULL,
                is_research_protocol_satisfied INTEGER NOT NULL,
                is_promotable INTEGER NOT NULL,
                assessment_notes TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS retirement_assessments (
                assessment_id TEXT PRIMARY KEY,
                edge_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                expectancy_degradation REAL NOT NULL,
                confidence_decline REAL NOT NULL,
                structural_shift_detected INTEGER NOT NULL,
                amendment_001_violation INTEGER NOT NULL,
                is_retirement_recommended INTEGER NOT NULL,
                assessment_notes TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS governance_decisions (
                decision_id TEXT PRIMARY KEY,
                edge_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                rationale TEXT NOT NULL,
                authorizer TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS governance_audits (
                audit_id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                edge_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                evidence_ids_json TEXT NOT NULL,
                experiment_id TEXT NOT NULL,
                evaluation_id TEXT NOT NULL,
                validation_session_id TEXT NOT NULL,
                is_explainable INTEGER NOT NULL,
                is_replayable INTEGER NOT NULL,
                operator TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS governance_summaries (
                summary_id TEXT PRIMARY KEY,
                total_edges INTEGER NOT NULL,
                total_decisions INTEGER NOT NULL,
                status_counts_json TEXT NOT NULL,
                decision_counts_json TEXT NOT NULL,
                reason_counts_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class EdgeRepository:
    """Repository for persisting and querying EdgeCandidate instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, candidate: EdgeCandidate) -> EdgeCandidate:
        """Insert or replace an EdgeCandidate."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO edge_candidates (
                    edge_id, title, hypothesis_id, evaluation_id, experiment_id, validation_session_id,
                    evidence_ids_json, status, created_timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.edge_id,
                    candidate.title,
                    candidate.hypothesis_id,
                    candidate.evaluation_id,
                    candidate.experiment_id,
                    candidate.validation_session_id,
                    json.dumps(candidate.evidence_ids),
                    candidate.status.value,
                    candidate.created_timestamp,
                    json.dumps(candidate.metadata),
                    candidate.canonical_hash,
                ),
            )
        return candidate

    def get_by_id(self, edge_id: str) -> EdgeCandidate | None:
        """Fetch candidate by ID."""
        cursor = self._conn.execute("SELECT * FROM edge_candidates WHERE edge_id = ?", (edge_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[EdgeCandidate]:
        """Fetch all candidates."""
        cursor = self._conn.execute("SELECT * FROM edge_candidates ORDER BY created_timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> EdgeCandidate:
        return EdgeCandidate(
            edge_id=row[0],
            title=row[1],
            hypothesis_id=row[2],
            evaluation_id=row[3],
            experiment_id=row[4],
            validation_session_id=row[5],
            evidence_ids=json.loads(row[6]),
            status=EdgeStatus(row[7]),
            created_timestamp=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class PromotionRepository:
    """Repository for persisting and querying PromotionAssessment instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, assessment: PromotionAssessment) -> PromotionAssessment:
        """Insert or replace a PromotionAssessment."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO promotion_assessments (
                    assessment_id, edge_id, hypothesis_id, is_hypothesis_passed, is_evidence_complete,
                    is_experiment_complete, is_statistics_complete, is_live_validation_complete,
                    is_constitution_satisfied, is_research_protocol_satisfied, is_promotable,
                    assessment_notes, timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment.assessment_id,
                    assessment.edge_id,
                    assessment.hypothesis_id,
                    1 if assessment.is_hypothesis_passed else 0,
                    1 if assessment.is_evidence_complete else 0,
                    1 if assessment.is_experiment_complete else 0,
                    1 if assessment.is_statistics_complete else 0,
                    1 if assessment.is_live_validation_complete else 0,
                    1 if assessment.is_constitution_satisfied else 0,
                    1 if assessment.is_research_protocol_satisfied else 0,
                    1 if assessment.is_promotable else 0,
                    assessment.assessment_notes,
                    assessment.timestamp,
                    assessment.canonical_hash,
                ),
            )
        return assessment

    def get_by_id(self, assessment_id: str) -> PromotionAssessment | None:
        """Fetch assessment by ID."""
        cursor = self._conn.execute("SELECT * FROM promotion_assessments WHERE assessment_id = ?", (assessment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_edge_id(self, edge_id: str) -> PromotionAssessment | None:
        """Fetch assessment by target edge ID."""
        cursor = self._conn.execute("SELECT * FROM promotion_assessments WHERE edge_id = ?", (edge_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[PromotionAssessment]:
        """Fetch all promotion assessments."""
        cursor = self._conn.execute("SELECT * FROM promotion_assessments ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> PromotionAssessment:
        return PromotionAssessment(
            assessment_id=row[0],
            edge_id=row[1],
            hypothesis_id=row[2],
            is_hypothesis_passed=bool(row[3]),
            is_evidence_complete=bool(row[4]),
            is_experiment_complete=bool(row[5]),
            is_statistics_complete=bool(row[6]),
            is_live_validation_complete=bool(row[7]),
            is_constitution_satisfied=bool(row[8]),
            is_research_protocol_satisfied=bool(row[9]),
            is_promotable=bool(row[10]),
            assessment_notes=row[11],
            timestamp=row[12],
            canonical_hash=row[13],
        )


class RetirementRepository:
    """Repository for persisting and querying RetirementAssessment instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, assessment: RetirementAssessment) -> RetirementAssessment:
        """Insert or replace a RetirementAssessment."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO retirement_assessments (
                    assessment_id, edge_id, hypothesis_id, expectancy_degradation, confidence_decline,
                    structural_shift_detected, amendment_001_violation, is_retirement_recommended,
                    assessment_notes, timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment.assessment_id,
                    assessment.edge_id,
                    assessment.hypothesis_id,
                    assessment.expectancy_degradation,
                    assessment.confidence_decline,
                    1 if assessment.structural_shift_detected else 0,
                    1 if assessment.amendment_001_violation else 0,
                    1 if assessment.is_retirement_recommended else 0,
                    assessment.assessment_notes,
                    assessment.timestamp,
                    assessment.canonical_hash,
                ),
            )
        return assessment

    def get_by_id(self, assessment_id: str) -> RetirementAssessment | None:
        """Fetch assessment by ID."""
        cursor = self._conn.execute("SELECT * FROM retirement_assessments WHERE assessment_id = ?", (assessment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_edge_id(self, edge_id: str) -> RetirementAssessment | None:
        """Fetch assessment by target edge ID."""
        cursor = self._conn.execute("SELECT * FROM retirement_assessments WHERE edge_id = ?", (edge_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[RetirementAssessment]:
        """Fetch all retirement assessments."""
        cursor = self._conn.execute("SELECT * FROM retirement_assessments ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> RetirementAssessment:
        return RetirementAssessment(
            assessment_id=row[0],
            edge_id=row[1],
            hypothesis_id=row[2],
            expectancy_degradation=row[3],
            confidence_decline=row[4],
            structural_shift_detected=bool(row[5]),
            amendment_001_violation=bool(row[6]),
            is_retirement_recommended=bool(row[7]),
            assessment_notes=row[8],
            timestamp=row[9],
            canonical_hash=row[10],
        )


class GovernanceRepository:
    """Repository for persisting and querying GovernanceDecision instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, decision: GovernanceDecision) -> GovernanceDecision:
        """Insert or replace a GovernanceDecision."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO governance_decisions (
                    decision_id, edge_id, hypothesis_id, decision, reason,
                    rationale, authorizer, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.edge_id,
                    decision.hypothesis_id,
                    decision.decision.value,
                    decision.reason.value,
                    decision.rationale,
                    decision.authorizer,
                    decision.timestamp,
                    json.dumps(decision.metadata),
                    decision.canonical_hash,
                ),
            )
        return decision

    def get_by_id(self, decision_id: str) -> GovernanceDecision | None:
        """Fetch decision by ID."""
        cursor = self._conn.execute("SELECT * FROM governance_decisions WHERE decision_id = ?", (decision_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_edge_id(self, edge_id: str) -> GovernanceDecision | None:
        """Fetch decision by target edge ID."""
        cursor = self._conn.execute("SELECT * FROM governance_decisions WHERE edge_id = ?", (edge_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[GovernanceDecision]:
        """Fetch all decisions."""
        cursor = self._conn.execute("SELECT * FROM governance_decisions ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> GovernanceDecision:
        return GovernanceDecision(
            decision_id=row[0],
            edge_id=row[1],
            hypothesis_id=row[2],
            decision=GovernanceDecisionOutcome(row[3]),
            reason=GovernanceReason(row[4]),
            rationale=row[5],
            authorizer=row[6],
            timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class AuditRepository:
    """Repository for persisting and querying GovernanceAudit instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, audit: GovernanceAudit) -> GovernanceAudit:
        """Insert or replace a GovernanceAudit."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO governance_audits (
                    audit_id, decision_id, edge_id, hypothesis_id, evidence_ids_json,
                    experiment_id, evaluation_id, validation_session_id, is_explainable, is_replayable,
                    operator, timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.audit_id,
                    audit.decision_id,
                    audit.edge_id,
                    audit.hypothesis_id,
                    json.dumps(audit.evidence_ids),
                    audit.experiment_id,
                    audit.evaluation_id,
                    audit.validation_session_id,
                    1 if audit.is_explainable else 0,
                    1 if audit.is_replayable else 0,
                    audit.operator,
                    audit.timestamp,
                    audit.canonical_hash,
                ),
            )
        return audit

    def get_by_id(self, audit_id: str) -> GovernanceAudit | None:
        """Fetch audit by ID."""
        cursor = self._conn.execute("SELECT * FROM governance_audits WHERE audit_id = ?", (audit_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_decision_id(self, decision_id: str) -> GovernanceAudit | None:
        """Fetch audit by target decision ID."""
        cursor = self._conn.execute("SELECT * FROM governance_audits WHERE decision_id = ?", (decision_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[GovernanceAudit]:
        """Fetch all audits."""
        cursor = self._conn.execute("SELECT * FROM governance_audits ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> GovernanceAudit:
        return GovernanceAudit(
            audit_id=row[0],
            decision_id=row[1],
            edge_id=row[2],
            hypothesis_id=row[3],
            evidence_ids=json.loads(row[4]),
            experiment_id=row[5],
            evaluation_id=row[6],
            validation_session_id=row[7],
            is_explainable=bool(row[8]),
            is_replayable=bool(row[9]),
            operator=row[10],
            timestamp=row[11],
            canonical_hash=row[12],
        )


class SummaryRepository:
    """Repository for persisting and querying GovernanceSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: GovernanceSummary) -> GovernanceSummary:
        """Insert or replace a GovernanceSummary."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO governance_summaries (
                    summary_id, total_edges, total_decisions, status_counts_json,
                    decision_counts_json, reason_counts_json, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.total_edges,
                    summary.total_decisions,
                    json.dumps(summary.status_counts),
                    json.dumps(summary.decision_counts),
                    json.dumps(summary.reason_counts),
                    summary.timestamp,
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> GovernanceSummary | None:
        """Fetch summary by ID."""
        cursor = self._conn.execute("SELECT * FROM governance_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> GovernanceSummary:
        return GovernanceSummary(
            summary_id=row[0],
            total_edges=row[1],
            total_decisions=row[2],
            status_counts=json.loads(row[3]),
            decision_counts=json.loads(row[4]),
            reason_counts=json.loads(row[5]),
            timestamp=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class GovernancePersistenceContext:
    """Unified Persistence Context wrapping SQLite repositories for governance subsystem."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_governance_db(self.conn)
        self.edges = EdgeRepository(self.conn)
        self.promotions = PromotionRepository(self.conn)
        self.retirements = RetirementRepository(self.conn)
        self.decisions = GovernanceRepository(self.conn)
        self.audits = AuditRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
