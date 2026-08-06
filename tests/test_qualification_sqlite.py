"""
Project GOAT v0.7 — Test Suite for Scientific Qualification Persistence Repositories

Coverage:
- QualificationRepository (save, get, list round-trip)
- GateRepository (save, get round-trip)
- GateEvaluationRepository (save, get round-trip)
- DecisionReadinessRepository (save readiness & explanation, get round-trip)
- QualificationReportRepository (save, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.qualification.core.canonical import (
    compute_evaluation_id,
    compute_gate_id,
    compute_qualification_explanation_id,
    compute_qualification_id,
    compute_readiness_id,
)
from goat.qualification.core.enums import QualificationState, ReadinessLevel
from goat.qualification.core.models import (
    DecisionReadiness,
    GateEvaluation,
    QualificationExplainabilityRecord,
    QualificationGate,
    ScientificQualification,
)
from goat.qualification.persistence.sqlite import (
    DecisionReadinessRepository,
    GateEvaluationRepository,
    GateRepository,
    QualificationReportRepository,
    QualificationRepository,
    init_qualification_db,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_qualification_db(conn)
    yield conn
    conn.close()


def test_qualification_repository_roundtrip(db_conn):
    repo = QualificationRepository(db_conn)
    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(
        qualification_id=q_id,
        composite_id="CMP_1",
        regime_id="MRG_1",
        evaluation_timestamp="2026-07-30T00:00:00Z",
        qualification_state=QualificationState.QUALIFIED,
        overall_readiness=0.85,
        canonical_hash=q_hash,
    )

    repo.save_qualification(qual)
    fetched = repo.get_qualification(q_id)

    assert fetched == qual
    assert len(repo.list_qualifications()) == 1


def test_gate_repository_roundtrip(db_conn):
    repo = GateRepository(db_conn)
    g_id, g_hash = compute_gate_id("Gate Evidence")
    gate = QualificationGate(
        gate_id=g_id,
        gate_name="Gate Evidence",
        evaluation_rule="EVIDENCE_SUFFICIENCY_RULE",
        canonical_hash=g_hash,
    )

    repo.save_gate(gate)
    fetched = repo.get_gate(g_id)

    assert fetched == gate


def test_gate_evaluation_repository_roundtrip(db_conn):
    q_repo = QualificationRepository(db_conn)
    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(
        qualification_id=q_id,
        composite_id="CMP_1",
        regime_id="MRG_1",
        evaluation_timestamp="2026-07-30T00:00:00Z",
        qualification_state=QualificationState.QUALIFIED,
        overall_readiness=0.85,
        canonical_hash=q_hash,
    )
    q_repo.save_qualification(qual)

    g_repo = GateRepository(db_conn)
    g_id, g_hash = compute_gate_id("Gate Evidence")
    gate = QualificationGate(
        gate_id=g_id,
        gate_name="Gate Evidence",
        evaluation_rule="EVIDENCE_SUFFICIENCY_RULE",
        canonical_hash=g_hash,
    )
    g_repo.save_gate(gate)

    ev_repo = GateEvaluationRepository(db_conn)
    e_id, e_hash = compute_evaluation_id(g_id, q_id)
    evaluation = GateEvaluation(
        evaluation_id=e_id,
        gate_id=g_id,
        qualification_id=q_id,
        passed=True,
        score=0.85,
        canonical_hash=e_hash,
    )

    ev_repo.save_evaluation(evaluation)
    fetched = ev_repo.get_evaluation(e_id)

    assert fetched == evaluation


def test_readiness_repository_roundtrip(db_conn):
    q_repo = QualificationRepository(db_conn)
    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(
        qualification_id=q_id,
        composite_id="CMP_1",
        regime_id="MRG_1",
        evaluation_timestamp="2026-07-30T00:00:00Z",
        qualification_state=QualificationState.QUALIFIED,
        overall_readiness=0.85,
        canonical_hash=q_hash,
    )
    q_repo.save_qualification(qual)

    rdn_repo = DecisionReadinessRepository(db_conn)
    r_id, r_hash = compute_readiness_id(q_id, "READY_FOR_SIMULATION")
    readiness = DecisionReadiness(
        readiness_id=r_id,
        qualification_id=q_id,
        readiness_level=ReadinessLevel.READY_FOR_SIMULATION,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=r_hash,
    )

    rdn_repo.save_readiness(readiness)
    fetched_rdn = rdn_repo.get_readiness(r_id)
    assert fetched_rdn == readiness

    ex_id, ex_hash = compute_qualification_explanation_id(q_id)
    explanation = QualificationExplainabilityRecord(
        explanation_id=ex_id,
        qualification_id=q_id,
        scientific_rationale="Rationale text.",
        canonical_hash=ex_hash,
    )
    rdn_repo.save_explanation(explanation)
    fetched_ex = rdn_repo.get_explanation(ex_id)
    assert fetched_ex == explanation
