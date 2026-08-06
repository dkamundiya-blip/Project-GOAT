"""
Project GOAT v0.9 — SQLite Persistence Repositories for Controlled Live Scientific Validation Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
    ValidationStatus,
)
from goat.live_validation.core.models import (
    LiveValidationCandidate,
    ValidationAudit,
    ValidationDecision,
    ValidationObservation,
    ValidationSession,
    ValidationSummary,
)


def init_live_validation_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and pragmas for Controlled Live Scientific Validation subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS live_validation_candidates (
                candidate_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                evaluation_id TEXT NOT NULL,
                experiment_id TEXT NOT NULL,
                evidence_ids_json TEXT NOT NULL,
                replay_id TEXT NOT NULL,
                status TEXT NOT NULL,
                eligibility_score REAL NOT NULL,
                created_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_sessions (
                session_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                hypothesis_id TEXT NOT NULL,
                status TEXT NOT NULL,
                monitoring_status TEXT NOT NULL,
                start_timestamp TEXT NOT NULL,
                end_timestamp TEXT,
                total_observations INTEGER NOT NULL,
                operator TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_observations (
                observation_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                live_outcome REAL NOT NULL,
                expected_outcome REAL NOT NULL,
                slippage REAL NOT NULL,
                spread REAL NOT NULL,
                latency_ms REAL NOT NULL,
                fill_ratio REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_decisions (
                decision_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                rationale TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                authorizer TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_audits (
                audit_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                action TEXT NOT NULL,
                previous_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                operator TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                notes TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_summaries (
                summary_id TEXT PRIMARY KEY,
                total_candidates INTEGER NOT NULL,
                total_sessions INTEGER NOT NULL,
                total_observations INTEGER NOT NULL,
                status_counts_json TEXT NOT NULL,
                decision_counts_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class CandidateRepository:
    """Repository for persisting and querying LiveValidationCandidate instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, candidate: LiveValidationCandidate) -> LiveValidationCandidate:
        """Insert or replace a LiveValidationCandidate."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO live_validation_candidates (
                    candidate_id, hypothesis_id, evaluation_id, experiment_id, evidence_ids_json,
                    replay_id, status, eligibility_score, created_timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.candidate_id,
                    candidate.hypothesis_id,
                    candidate.evaluation_id,
                    candidate.experiment_id,
                    json.dumps(candidate.evidence_ids),
                    candidate.replay_id,
                    candidate.status.value,
                    candidate.eligibility_score,
                    candidate.created_timestamp,
                    json.dumps(candidate.metadata),
                    candidate.canonical_hash,
                ),
            )
        return candidate

    def get_by_id(self, candidate_id: str) -> LiveValidationCandidate | None:
        """Fetch candidate by ID."""
        cursor = self._conn.execute("SELECT * FROM live_validation_candidates WHERE candidate_id = ?", (candidate_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[LiveValidationCandidate]:
        """Fetch all candidates."""
        cursor = self._conn.execute("SELECT * FROM live_validation_candidates ORDER BY created_timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> LiveValidationCandidate:
        return LiveValidationCandidate(
            candidate_id=row[0],
            hypothesis_id=row[1],
            evaluation_id=row[2],
            experiment_id=row[3],
            evidence_ids=json.loads(row[4]),
            replay_id=row[5],
            status=ValidationStatus(row[6]),
            eligibility_score=row[7],
            created_timestamp=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class ValidationSessionRepository:
    """Repository for persisting and querying ValidationSession instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, session: ValidationSession) -> ValidationSession:
        """Insert or replace a ValidationSession."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO validation_sessions (
                    session_id, candidate_id, hypothesis_id, status, monitoring_status,
                    start_timestamp, end_timestamp, total_observations, operator, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.candidate_id,
                    session.hypothesis_id,
                    session.status.value,
                    session.monitoring_status.value,
                    session.start_timestamp,
                    session.end_timestamp,
                    session.total_observations,
                    session.operator,
                    json.dumps(session.metadata),
                    session.canonical_hash,
                ),
            )
        return session

    def get_by_id(self, session_id: str) -> ValidationSession | None:
        """Fetch session by ID."""
        cursor = self._conn.execute("SELECT * FROM validation_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ValidationSession]:
        """Fetch all sessions."""
        cursor = self._conn.execute("SELECT * FROM validation_sessions ORDER BY start_timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ValidationSession:
        return ValidationSession(
            session_id=row[0],
            candidate_id=row[1],
            hypothesis_id=row[2],
            status=ValidationStatus(row[3]),
            monitoring_status=MonitoringStatus(row[4]),
            start_timestamp=row[5],
            end_timestamp=row[6],
            total_observations=row[7],
            operator=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class ObservationRepository:
    """Repository for persisting and querying ValidationObservation instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, observation: ValidationObservation) -> ValidationObservation:
        """Insert or replace a ValidationObservation."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO validation_observations (
                    observation_id, session_id, timestamp, live_outcome, expected_outcome,
                    slippage, spread, latency_ms, fill_ratio, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.observation_id,
                    observation.session_id,
                    observation.timestamp,
                    observation.live_outcome,
                    observation.expected_outcome,
                    observation.slippage,
                    observation.spread,
                    observation.latency_ms,
                    observation.fill_ratio,
                    json.dumps(observation.metadata),
                    observation.canonical_hash,
                ),
            )
        return observation

    def get_by_id(self, observation_id: str) -> ValidationObservation | None:
        """Fetch observation by ID."""
        cursor = self._conn.execute("SELECT * FROM validation_observations WHERE observation_id = ?", (observation_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_by_session(self, session_id: str) -> list[ValidationObservation]:
        """Fetch all observations for a target session."""
        cursor = self._conn.execute("SELECT * FROM validation_observations WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ValidationObservation:
        return ValidationObservation(
            observation_id=row[0],
            session_id=row[1],
            timestamp=row[2],
            live_outcome=row[3],
            expected_outcome=row[4],
            slippage=row[5],
            spread=row[6],
            latency_ms=row[7],
            fill_ratio=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class DecisionRepository:
    """Repository for persisting and querying ValidationDecision instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, decision: ValidationDecision) -> ValidationDecision:
        """Insert or replace a ValidationDecision."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO validation_decisions (
                    decision_id, session_id, candidate_id, decision, rationale,
                    timestamp, authorizer, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.session_id,
                    decision.candidate_id,
                    decision.decision.value,
                    decision.rationale,
                    decision.timestamp,
                    decision.authorizer,
                    json.dumps(decision.metadata),
                    decision.canonical_hash,
                ),
            )
        return decision

    def get_by_id(self, decision_id: str) -> ValidationDecision | None:
        """Fetch decision by ID."""
        cursor = self._conn.execute("SELECT * FROM validation_decisions WHERE decision_id = ?", (decision_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def get_by_session_id(self, session_id: str) -> ValidationDecision | None:
        """Fetch decision by target session ID."""
        cursor = self._conn.execute("SELECT * FROM validation_decisions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_all(self) -> list[ValidationDecision]:
        """Fetch all decisions."""
        cursor = self._conn.execute("SELECT * FROM validation_decisions ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ValidationDecision:
        return ValidationDecision(
            decision_id=row[0],
            session_id=row[1],
            candidate_id=row[2],
            decision=ValidationDecisionOutcome(row[3]),
            rationale=row[4],
            timestamp=row[5],
            authorizer=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class AuditRepository:
    """Repository for persisting and querying ValidationAudit instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, audit: ValidationAudit) -> ValidationAudit:
        """Insert or replace a ValidationAudit."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO validation_audits (
                    audit_id, session_id, action, previous_status, new_status,
                    operator, timestamp, notes, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.audit_id,
                    audit.session_id,
                    audit.action,
                    audit.previous_status.value,
                    audit.new_status.value,
                    audit.operator,
                    audit.timestamp,
                    audit.notes,
                    audit.canonical_hash,
                ),
            )
        return audit

    def get_by_id(self, audit_id: str) -> ValidationAudit | None:
        """Fetch audit by ID."""
        cursor = self._conn.execute("SELECT * FROM validation_audits WHERE audit_id = ?", (audit_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def list_by_session(self, session_id: str) -> list[ValidationAudit]:
        """Fetch all audits for a target session."""
        cursor = self._conn.execute("SELECT * FROM validation_audits WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ValidationAudit:
        return ValidationAudit(
            audit_id=row[0],
            session_id=row[1],
            action=row[2],
            previous_status=ValidationStatus(row[3]),
            new_status=ValidationStatus(row[4]),
            operator=row[5],
            timestamp=row[6],
            notes=row[7],
            canonical_hash=row[8],
        )


class SummaryRepository:
    """Repository for persisting and querying ValidationSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: ValidationSummary) -> ValidationSummary:
        """Insert or replace a ValidationSummary."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO validation_summaries (
                    summary_id, total_candidates, total_sessions, total_observations,
                    status_counts_json, decision_counts_json, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.total_candidates,
                    summary.total_sessions,
                    summary.total_observations,
                    json.dumps(summary.status_counts),
                    json.dumps(summary.decision_counts),
                    summary.timestamp,
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> ValidationSummary | None:
        """Fetch summary by ID."""
        cursor = self._conn.execute("SELECT * FROM validation_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ValidationSummary:
        return ValidationSummary(
            summary_id=row[0],
            total_candidates=row[1],
            total_sessions=row[2],
            total_observations=row[3],
            status_counts=json.loads(row[4]),
            decision_counts=json.loads(row[5]),
            timestamp=row[6],
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class LiveValidationPersistenceContext:
    """Unified Persistence Context wrapping SQLite repositories for controlled live validation subsystem."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_live_validation_db(self.conn)
        self.candidates = CandidateRepository(self.conn)
        self.sessions = ValidationSessionRepository(self.conn)
        self.observations = ObservationRepository(self.conn)
        self.decisions = DecisionRepository(self.conn)
        self.audits = AuditRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
