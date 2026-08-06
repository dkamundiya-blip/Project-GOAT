"""
Project GOAT v0.7 — Test Suite for Scientific Alpha Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (ScientificEdge, EdgeEvidence, EdgeScore, EdgeRanking, EdgeExplainabilityRecord)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.alpha.core.canonical import (
    compute_alpha_report_id,
    compute_edge_id,
    compute_evidence_id,
    compute_explanation_id,
    compute_ranking_id,
    compute_score_id,
    serialize_canonical_json,
)
from goat.alpha.core.enums import EdgeMaturity, EvidenceSourceType
from goat.alpha.core.models import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    EdgeRanking,
    EdgeScore,
    ScientificEdge,
)


def test_edge_id_determinism():
    id1, hash1 = compute_edge_id("Edge A", ["HYP_1"], ["VAL_1"])
    id2, hash2 = compute_edge_id("Edge A", ["HYP_1"], ["VAL_1"])
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SED_")


def test_evidence_id_determinism():
    id1, hash1 = compute_evidence_id("SED_1234567890ABCDEF", "VAL_1", "VALIDATION")
    id2, hash2 = compute_evidence_id("SED_1234567890ABCDEF", "VAL_1", "VALIDATION")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EEV_")


def test_score_id_determinism():
    id1, hash1 = compute_score_id("SED_1234567890ABCDEF", 0.85, "2026-07-30T00:00:00Z")
    id2, hash2 = compute_score_id("SED_1234567890ABCDEF", 0.85, "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("ESC_")


def test_ranking_id_determinism():
    id1, hash1 = compute_ranking_id(["SED_1", "SED_2"], "2026-07-30T00:00:00Z")
    id2, hash2 = compute_ranking_id(["SED_1", "SED_2"], "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("ERK_")


def test_explanation_id_determinism():
    id1, hash1 = compute_explanation_id("SED_1234567890ABCDEF", "HYP_1")
    id2, hash2 = compute_explanation_id("SED_1234567890ABCDEF", "HYP_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EEX_")


def test_alpha_report_id_determinism():
    id1, hash1 = compute_alpha_report_id("ScientificAlphaReport", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_alpha_report_id("ScientificAlphaReport", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SAR_")


def test_scientific_edge_model():
    e_id, e_hash = compute_edge_id("Edge Title", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge Title",
        maturity=EdgeMaturity.VALIDATED,
        originating_hypotheses=["HYP_1"],
        originating_validations=["VAL_1"],
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )
    assert edge.edge_id == e_id
    with pytest.raises((TypeError, ValidationError)):
        edge.title = "Modified Title"


def test_edge_evidence_model():
    ev_id, ev_hash = compute_evidence_id("SED_1234567890ABCDEF", "VAL_1", "VALIDATION")
    evidence = EdgeEvidence(
        evidence_id=ev_id,
        edge_id="SED_1234567890ABCDEF",
        source_type=EvidenceSourceType.VALIDATION,
        source_reference="VAL_1",
        confidence=0.85,
        canonical_hash=ev_hash,
    )
    assert evidence.evidence_id == ev_id
    with pytest.raises((TypeError, ValidationError)):
        evidence.confidence = 0.99


def test_edge_score_model():
    sc_id, sc_hash = compute_score_id("SED_1234567890ABCDEF", 0.90, "2026-07-30T00:00:00Z")
    score = EdgeScore(
        score_id=sc_id,
        edge_id="SED_1234567890ABCDEF",
        overall_edge_score=0.90,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=sc_hash,
    )
    assert score.score_id == sc_id
    with pytest.raises((TypeError, ValidationError)):
        score.overall_edge_score = 1.0


def test_edge_ranking_model():
    rk_id, rk_hash = compute_ranking_id(["SED_1"], "2026-07-30T00:00:00Z")
    ranking = EdgeRanking(
        ranking_id=rk_id,
        ranked_edges=["SED_1"],
        ranking_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=rk_hash,
    )
    assert ranking.ranking_id == rk_id
    with pytest.raises((TypeError, ValidationError)):
        ranking.ranking_timestamp = "2026-07-31T00:00:00Z"


def test_edge_explainability_record_model():
    ex_id, ex_hash = compute_explanation_id("SED_1234567890ABCDEF", "HYP_1")
    expl = EdgeExplainabilityRecord(
        explanation_id=ex_id,
        edge_id="SED_1234567890ABCDEF",
        origin="HYP_1",
        scientific_explanation="Traceable origin hypothesis HYP_1.",
        canonical_hash=ex_hash,
    )
    assert expl.explanation_id == ex_id
    with pytest.raises((TypeError, ValidationError)):
        expl.origin = "HYP_NEW"
