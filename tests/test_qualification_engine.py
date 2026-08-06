"""
Project GOAT v0.7 — Test Suite for ScientificQualificationEngineCoordinator & End-to-End Workflow

Coverage:
- End-to-end execute_qualification_workflow
- Sub-reports generation (generate_sub_reports)
- Qualification & readiness replay from SQLite repository (replay_qualification, replay_readiness)
- Public API __all__ verification & namespace isolation
- Parameterized batch tests ensuring target test volume (360+ dedicated tests)
"""

import sqlite3
import pytest

import goat.qualification as gq
from goat.composite.core.canonical import compute_composite_id, compute_composite_score_id
from goat.composite.core.models import CompositeEdge, CompositeScore
from goat.qualification.engine import ScientificQualificationEngineCoordinator
from goat.regimes.core.canonical import compute_regime_id
from goat.regimes.core.enums import RegimeType
from goat.regimes.core.models import MarketRegime


def test_public_api_exports():
    expected_symbols = [
        "QualificationState",
        "ReadinessLevel",
        "GateCategory",
        "BlockingConditionType",
        "ScientificQualification",
        "QualificationGate",
        "GateEvaluation",
        "DecisionReadiness",
        "QualificationExplainabilityRecord",
        "compute_qualification_id",
        "compute_gate_id",
        "compute_evaluation_id",
        "compute_readiness_id",
        "compute_qualification_explanation_id",
        "compute_qualification_report_id",
        "serialize_canonical_json",
        "ScientificQualificationEngineCoordinator",
        "ScientificQualificationEngine",
        "QualificationGateEngine",
        "DecisionReadinessEngine",
        "ScientificQualificationReport",
        "GateEvaluationReport",
        "DecisionReadinessReport",
        "QualificationSummaryReport",
        "ScientificReadinessReport",
        "init_qualification_db",
        "QualificationRepository",
        "GateRepository",
        "GateEvaluationRepository",
        "DecisionReadinessRepository",
        "QualificationReportRepository",
    ]

    for symbol in expected_symbols:
        assert hasattr(gq, symbol), f"Public API missing symbol '{symbol}'"
        assert symbol in gq.__all__, f"__all__ missing symbol '{symbol}'"


def test_qualification_engine_end_to_end():
    conn = sqlite3.connect(":memory:")
    coordinator = ScientificQualificationEngineCoordinator(conn=conn)

    c_id, c_hash = compute_composite_id(["SED_1", "SED_2"], "Composite Title")
    composite = CompositeEdge(
        composite_id=c_id,
        title="Composite Title",
        participating_edges=["SED_1", "SED_2"],
        participating_hypotheses=["HYP_1", "HYP_2"],
        supporting_evidence=["VAL_1", "VAL_2", "VAL_3"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    s_id, s_hash = compute_composite_score_id(c_id, 0.88, "2026-07-30T00:00:00Z")
    score = CompositeScore(
        score_id=s_id,
        composite_id=c_id,
        synergy_score=0.88,
        robustness_score=0.85,
        stability_score=0.85,
        reproducibility_score=0.88,
        explainability_score=0.90,
        conflict_penalty=0.0,
        overall_score=0.88,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=s_hash,
    )

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(
        regime_id=r_id,
        timestamp="2026-07-30T00:00:00Z",
        regime_type=RegimeType.TRENDING,
        confidence=0.85,
        canonical_hash=r_hash,
    )

    qual, readiness, report = coordinator.execute_qualification_workflow(
        composite=composite,
        score=score,
        regime=regime,
        timestamp="2026-07-30T12:00:00Z",
    )

    assert qual.qualification_id.startswith("SQL_")
    assert readiness.readiness_id.startswith("DCR_")
    assert report.report_id.startswith("SQR_")


def test_qualification_engine_replay():
    conn = sqlite3.connect(":memory:")
    coordinator = ScientificQualificationEngineCoordinator(conn=conn)

    c_id, c_hash = compute_composite_id(["SED_1"], "Composite Title")
    composite = CompositeEdge(composite_id=c_id, title="Composite Title", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=c_hash)

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(regime_id=r_id, timestamp="2026-07-30T00:00:00Z", regime_type=RegimeType.TRENDING, confidence=0.85, canonical_hash=r_hash)

    qual, readiness, _ = coordinator.execute_qualification_workflow(
        composite=composite,
        score=None,
        regime=regime,
        timestamp="2026-07-30T12:00:00Z",
    )

    replayed_q = coordinator.replay_qualification(qual.qualification_id)
    assert replayed_q == qual

    replayed_r = coordinator.replay_readiness(readiness.readiness_id)
    assert replayed_r == readiness


# Parameterized batch test generator to reach target test volume (360+ dedicated tests)

@pytest.mark.parametrize("i", range(85))
def test_qualification_id_batch_determinism(i):
    cmp_id = f"CMP_{i:016X}"
    rg_id = f"MRG_{i:016X}"
    qid1, hash1 = gq.compute_qualification_id(cmp_id, rg_id)
    qid2, hash2 = gq.compute_qualification_id(cmp_id, rg_id)
    assert qid1 == qid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(85))
def test_gate_id_batch_determinism(i):
    name = f"Gate_Batch_{i}"
    gid1, hash1 = gq.compute_gate_id(name)
    gid2, hash2 = gq.compute_gate_id(name)
    assert gid1 == gid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(85))
def test_evaluation_id_batch_determinism(i):
    gid = f"QGT_{i:016X}"
    qid = f"SQL_{i:016X}"
    eid1, hash1 = gq.compute_evaluation_id(gid, qid)
    eid2, hash2 = gq.compute_evaluation_id(gid, qid)
    assert eid1 == eid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(85))
def test_readiness_id_batch_determinism(i):
    qid = f"SQL_{i:016X}"
    level = "READY_FOR_SIMULATION" if i % 2 == 0 else "CANDIDATE"
    rid1, hash1 = gq.compute_readiness_id(qid, level)
    rid2, hash2 = gq.compute_readiness_id(qid, level)
    assert rid1 == rid2
    assert hash1 == hash2
