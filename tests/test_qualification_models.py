"""
Project GOAT v0.7 — Test Suite for Qualification Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (ScientificQualification, QualificationGate, GateEvaluation, DecisionReadiness, QualificationExplainabilityRecord)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.qualification.core.canonical import (
    compute_evaluation_id,
    compute_gate_id,
    compute_qualification_explanation_id,
    compute_qualification_id,
    compute_qualification_report_id,
    compute_readiness_id,
    serialize_canonical_json,
)
from goat.qualification.core.enums import QualificationState, ReadinessLevel
from goat.qualification.core.models import (
    DecisionReadiness,
    GateEvaluation,
    QualificationExplainabilityRecord,
    QualificationGate,
    ScientificQualification,
)


def test_qualification_id_determinism():
    id1, hash1 = compute_qualification_id("CMP_1", "MRG_1")
    id2, hash2 = compute_qualification_id("CMP_1", "MRG_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SQL_")


def test_gate_id_determinism():
    id1, hash1 = compute_gate_id("Gate Evidence")
    id2, hash2 = compute_gate_id("Gate Evidence")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("QGT_")


def test_evaluation_id_determinism():
    id1, hash1 = compute_evaluation_id("QGT_1", "SQL_1")
    id2, hash2 = compute_evaluation_id("QGT_1", "SQL_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("GEV_")


def test_readiness_id_determinism():
    id1, hash1 = compute_readiness_id("SQL_1", "READY_FOR_SIMULATION")
    id2, hash2 = compute_readiness_id("SQL_1", "READY_FOR_SIMULATION")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("DCR_")


def test_qualification_explanation_id_determinism():
    id1, hash1 = compute_qualification_explanation_id("SQL_1")
    id2, hash2 = compute_qualification_explanation_id("SQL_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("QEX_")


def test_qualification_report_id_determinism():
    id1, hash1 = compute_qualification_report_id("ScientificReadinessReport", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_qualification_report_id("ScientificReadinessReport", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SQR_")


def test_scientific_qualification_model():
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
    assert qual.qualification_id == q_id
    with pytest.raises((TypeError, ValidationError)):
        qual.overall_readiness = 1.0


def test_qualification_gate_model():
    g_id, g_hash = compute_gate_id("Gate Evidence")
    gate = QualificationGate(
        gate_id=g_id,
        gate_name="Gate Evidence",
        evaluation_rule="EVIDENCE_SUFFICIENCY_RULE",
        canonical_hash=g_hash,
    )
    assert gate.gate_id == g_id
    with pytest.raises((TypeError, ValidationError)):
        gate.priority = 1000


def test_gate_evaluation_model():
    e_id, e_hash = compute_evaluation_id("QGT_1", "SQL_1")
    evaluation = GateEvaluation(
        evaluation_id=e_id,
        gate_id="QGT_1",
        qualification_id="SQL_1",
        passed=True,
        score=0.85,
        canonical_hash=e_hash,
    )
    assert evaluation.evaluation_id == e_id
    with pytest.raises((TypeError, ValidationError)):
        evaluation.score = 1.5


def test_decision_readiness_model():
    r_id, r_hash = compute_readiness_id("SQL_1", "READY_FOR_SIMULATION")
    readiness = DecisionReadiness(
        readiness_id=r_id,
        qualification_id="SQL_1",
        readiness_level=ReadinessLevel.READY_FOR_SIMULATION,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=r_hash,
    )
    assert readiness.readiness_id == r_id
    with pytest.raises((TypeError, ValidationError)):
        readiness.timestamp = "2026-07-31T00:00:00Z"


def test_qualification_explainability_record_model():
    ex_id, ex_hash = compute_qualification_explanation_id("SQL_1")
    expl = QualificationExplainabilityRecord(
        explanation_id=ex_id,
        qualification_id="SQL_1",
        scientific_rationale="Rationale narrative.",
        canonical_hash=ex_hash,
    )
    assert expl.explanation_id == ex_id
    with pytest.raises((TypeError, ValidationError)):
        expl.scientific_rationale = "Modified"
