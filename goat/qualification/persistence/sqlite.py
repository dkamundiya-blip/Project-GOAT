"""
Project GOAT v0.7 — SQLite Persistence for Scientific Qualification Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- QualificationRepository
- GateRepository
- GateEvaluationRepository
- DecisionReadinessRepository
- QualificationReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.qualification.core.models import (
    DecisionReadiness,
    GateEvaluation,
    QualificationExplainabilityRecord,
    QualificationGate,
    ScientificQualification,
)


def init_qualification_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for Scientific Qualification Engine."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scientific_qualifications (
                qualification_id TEXT PRIMARY KEY,
                composite_id TEXT NOT NULL,
                regime_id TEXT NOT NULL,
                evaluation_timestamp TEXT NOT NULL,
                qualification_state TEXT NOT NULL,
                overall_readiness REAL NOT NULL,
                scientific_confidence REAL NOT NULL,
                evidence_strength REAL NOT NULL,
                reproducibility REAL NOT NULL,
                explainability REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS qualification_gates (
                gate_id TEXT PRIMARY KEY,
                gate_name TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL,
                evaluation_rule TEXT NOT NULL,
                pass_threshold REAL NOT NULL,
                mandatory INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gate_evaluations (
                evaluation_id TEXT PRIMARY KEY,
                gate_id TEXT NOT NULL,
                qualification_id TEXT NOT NULL,
                passed INTEGER NOT NULL,
                score REAL NOT NULL,
                explanation TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (qualification_id) REFERENCES scientific_qualifications(qualification_id) ON DELETE CASCADE,
                FOREIGN KEY (gate_id) REFERENCES qualification_gates(gate_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decision_readiness_records (
                readiness_id TEXT PRIMARY KEY,
                qualification_id TEXT NOT NULL,
                readiness_level TEXT NOT NULL,
                blocking_conditions_json TEXT NOT NULL,
                satisfied_conditions_json TEXT NOT NULL,
                scientific_summary TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (qualification_id) REFERENCES scientific_qualifications(qualification_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS qualification_explainability_records (
                explanation_id TEXT PRIMARY KEY,
                qualification_id TEXT NOT NULL,
                participating_composites_json TEXT NOT NULL,
                applicable_regimes_json TEXT NOT NULL,
                passed_gates_json TEXT NOT NULL,
                failed_gates_json TEXT NOT NULL,
                blocking_conditions_json TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                supporting_hypotheses_json TEXT NOT NULL,
                supporting_validations_json TEXT NOT NULL,
                supporting_knowledge_json TEXT NOT NULL,
                scientific_rationale TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (qualification_id) REFERENCES scientific_qualifications(qualification_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS qualification_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class QualificationRepository:
    """Repository for storing and retrieving ScientificQualification models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_qualification_db(self.conn)

    def save_qualification(self, qualification: ScientificQualification) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO scientific_qualifications (
                    qualification_id, composite_id, regime_id, evaluation_timestamp,
                    qualification_state, overall_readiness, scientific_confidence,
                    evidence_strength, reproducibility, explainability,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    qualification.qualification_id,
                    qualification.composite_id,
                    qualification.regime_id,
                    qualification.evaluation_timestamp,
                    qualification.qualification_state.value if hasattr(qualification.qualification_state, "value") else str(qualification.qualification_state),
                    qualification.overall_readiness,
                    qualification.scientific_confidence,
                    qualification.evidence_strength,
                    qualification.reproducibility,
                    qualification.explainability,
                    json.dumps(qualification.metadata, sort_keys=True),
                    qualification.canonical_hash,
                ),
            )

    def get_qualification(self, qualification_id: str) -> ScientificQualification | None:
        cursor = self.conn.execute(
            """
            SELECT qualification_id, composite_id, regime_id, evaluation_timestamp,
                   qualification_state, overall_readiness, scientific_confidence,
                   evidence_strength, reproducibility, explainability,
                   metadata_json, canonical_hash
            FROM scientific_qualifications WHERE qualification_id = ?
            """,
            (qualification_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ScientificQualification(
            qualification_id=row[0],
            composite_id=row[1],
            regime_id=row[2],
            evaluation_timestamp=row[3],
            qualification_state=row[4],
            overall_readiness=row[5],
            scientific_confidence=row[6],
            evidence_strength=row[7],
            reproducibility=row[8],
            explainability=row[9],
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )

    def list_qualifications(self) -> list[ScientificQualification]:
        cursor = self.conn.execute("SELECT qualification_id FROM scientific_qualifications ORDER BY qualification_id ASC")
        quals = []
        for row in cursor.fetchall():
            q = self.get_qualification(row[0])
            if q:
                quals.append(q)
        return quals


class GateRepository:
    """Repository for storing and retrieving QualificationGate models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_qualification_db(self.conn)

    def save_gate(self, gate: QualificationGate) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO qualification_gates (
                    gate_id, gate_name, description, priority,
                    evaluation_rule, pass_threshold, mandatory,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    gate.gate_id,
                    gate.gate_name,
                    gate.description,
                    gate.priority,
                    gate.evaluation_rule,
                    gate.pass_threshold,
                    1 if gate.mandatory else 0,
                    json.dumps(gate.metadata, sort_keys=True),
                    gate.canonical_hash,
                ),
            )

    def get_gate(self, gate_id: str) -> QualificationGate | None:
        cursor = self.conn.execute(
            """
            SELECT gate_id, gate_name, description, priority,
                   evaluation_rule, pass_threshold, mandatory,
                   metadata_json, canonical_hash
            FROM qualification_gates WHERE gate_id = ?
            """,
            (gate_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return QualificationGate(
            gate_id=row[0],
            gate_name=row[1],
            description=row[2],
            priority=row[3],
            evaluation_rule=row[4],
            pass_threshold=row[5],
            mandatory=bool(row[6]),
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class GateEvaluationRepository:
    """Repository for storing and retrieving GateEvaluation models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_qualification_db(self.conn)

    def save_evaluation(self, evaluation: GateEvaluation) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO gate_evaluations (
                    evaluation_id, gate_id, qualification_id, passed,
                    score, explanation, supporting_evidence_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evaluation.evaluation_id,
                    evaluation.gate_id,
                    evaluation.qualification_id,
                    1 if evaluation.passed else 0,
                    evaluation.score,
                    evaluation.explanation,
                    json.dumps(evaluation.supporting_evidence, sort_keys=True),
                    evaluation.canonical_hash,
                ),
            )

    def get_evaluation(self, evaluation_id: str) -> GateEvaluation | None:
        cursor = self.conn.execute(
            """
            SELECT evaluation_id, gate_id, qualification_id, passed,
                   score, explanation, supporting_evidence_json, canonical_hash
            FROM gate_evaluations WHERE evaluation_id = ?
            """,
            (evaluation_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return GateEvaluation(
            evaluation_id=row[0],
            gate_id=row[1],
            qualification_id=row[2],
            passed=bool(row[3]),
            score=row[4],
            explanation=row[5],
            supporting_evidence=json.loads(row[6]),
            canonical_hash=row[7],
        )


class DecisionReadinessRepository:
    """Repository for storing and retrieving DecisionReadiness and QualificationExplainabilityRecord models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_qualification_db(self.conn)

    def save_readiness(self, readiness: DecisionReadiness) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO decision_readiness_records (
                    readiness_id, qualification_id, readiness_level,
                    blocking_conditions_json, satisfied_conditions_json,
                    scientific_summary, timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    readiness.readiness_id,
                    readiness.qualification_id,
                    readiness.readiness_level.value if hasattr(readiness.readiness_level, "value") else str(readiness.readiness_level),
                    json.dumps(readiness.blocking_conditions, sort_keys=True),
                    json.dumps(readiness.satisfied_conditions, sort_keys=True),
                    readiness.scientific_summary,
                    readiness.timestamp,
                    readiness.canonical_hash,
                ),
            )

    def get_readiness(self, readiness_id: str) -> DecisionReadiness | None:
        cursor = self.conn.execute(
            """
            SELECT readiness_id, qualification_id, readiness_level,
                   blocking_conditions_json, satisfied_conditions_json,
                   scientific_summary, timestamp, canonical_hash
            FROM decision_readiness_records WHERE readiness_id = ?
            """,
            (readiness_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return DecisionReadiness(
            readiness_id=row[0],
            qualification_id=row[1],
            readiness_level=row[2],
            blocking_conditions=json.loads(row[3]),
            satisfied_conditions=json.loads(row[4]),
            scientific_summary=row[5],
            timestamp=row[6],
            canonical_hash=row[7],
        )

    def save_explanation(self, record: QualificationExplainabilityRecord) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO qualification_explainability_records (
                    explanation_id, qualification_id, participating_composites_json,
                    applicable_regimes_json, passed_gates_json, failed_gates_json,
                    blocking_conditions_json, supporting_evidence_json,
                    supporting_hypotheses_json, supporting_validations_json,
                    supporting_knowledge_json, scientific_rationale, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.explanation_id,
                    record.qualification_id,
                    json.dumps(record.participating_composites, sort_keys=True),
                    json.dumps(record.applicable_regimes, sort_keys=True),
                    json.dumps(record.passed_gates, sort_keys=True),
                    json.dumps(record.failed_gates, sort_keys=True),
                    json.dumps(record.blocking_conditions, sort_keys=True),
                    json.dumps(record.supporting_evidence, sort_keys=True),
                    json.dumps(record.supporting_hypotheses, sort_keys=True),
                    json.dumps(record.supporting_validations, sort_keys=True),
                    json.dumps(record.supporting_knowledge, sort_keys=True),
                    record.scientific_rationale,
                    record.canonical_hash,
                ),
            )

    def get_explanation(self, explanation_id: str) -> QualificationExplainabilityRecord | None:
        cursor = self.conn.execute(
            """
            SELECT explanation_id, qualification_id, participating_composites_json,
                   applicable_regimes_json, passed_gates_json, failed_gates_json,
                   blocking_conditions_json, supporting_evidence_json,
                   supporting_hypotheses_json, supporting_validations_json,
                   supporting_knowledge_json, scientific_rationale, canonical_hash
            FROM qualification_explainability_records WHERE explanation_id = ?
            """,
            (explanation_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return QualificationExplainabilityRecord(
            explanation_id=row[0],
            qualification_id=row[1],
            participating_composites=json.loads(row[2]),
            applicable_regimes=json.loads(row[3]),
            passed_gates=json.loads(row[4]),
            failed_gates=json.loads(row[5]),
            blocking_conditions=json.loads(row[6]),
            supporting_evidence=json.loads(row[7]),
            supporting_hypotheses=json.loads(row[8]),
            supporting_validations=json.loads(row[9]),
            supporting_knowledge=json.loads(row[10]),
            scientific_rationale=row[11],
            canonical_hash=row[12],
        )


class QualificationReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_qualification_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO qualification_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM qualification_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
