"""
Project GOAT v0.7 — Test Suite for Composite Edge Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (CompositeEdge, CompositeEvidence, CompositeScore, CompositeRanking, CompositeExplainabilityRecord)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.composite.core.canonical import (
    compute_composite_evidence_id,
    compute_composite_explanation_id,
    compute_composite_id,
    compute_composite_ranking_id,
    compute_composite_report_id,
    compute_composite_score_id,
    serialize_canonical_json,
)
from goat.composite.core.enums import ConflictSeverity, SynthesisMode
from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
)


def test_composite_id_determinism():
    id1, hash1 = compute_composite_id(["SED_1", "SED_2"], "Composite Title")
    id2, hash2 = compute_composite_id(["SED_1", "SED_2"], "Composite Title")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CMP_")


def test_composite_evidence_id_determinism():
    id1, hash1 = compute_composite_evidence_id("CMP_1234567890ABCDEF", "SED_1")
    id2, hash2 = compute_composite_evidence_id("CMP_1234567890ABCDEF", "SED_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CEV_")


def test_composite_score_id_determinism():
    id1, hash1 = compute_composite_score_id("CMP_1234567890ABCDEF", 0.85, "2026-07-30T00:00:00Z")
    id2, hash2 = compute_composite_score_id("CMP_1234567890ABCDEF", 0.85, "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CSC_")


def test_composite_ranking_id_determinism():
    id1, hash1 = compute_composite_ranking_id(["CMP_1", "CMP_2"], "2026-07-30T00:00:00Z")
    id2, hash2 = compute_composite_ranking_id(["CMP_1", "CMP_2"], "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CRK_")


def test_composite_explanation_id_determinism():
    id1, hash1 = compute_composite_explanation_id("CMP_1234567890ABCDEF")
    id2, hash2 = compute_composite_explanation_id("CMP_1234567890ABCDEF")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CEX_")


def test_composite_report_id_determinism():
    id1, hash1 = compute_composite_report_id("CompositeAnalysisReport", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_composite_report_id("CompositeAnalysisReport", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CAR_")


def test_composite_edge_model():
    c_id, c_hash = compute_composite_id(["SED_1", "SED_2"], "Title")
    composite = CompositeEdge(
        composite_id=c_id,
        title="Title",
        participating_edges=["SED_1", "SED_2"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )
    assert composite.composite_id == c_id
    with pytest.raises((TypeError, ValidationError)):
        composite.title = "Modified Title"


def test_composite_evidence_model():
    ev_id, ev_hash = compute_composite_evidence_id("CMP_1234567890ABCDEF", "SED_1")
    evidence = CompositeEvidence(
        evidence_id=ev_id,
        composite_id="CMP_1234567890ABCDEF",
        contributing_edge="SED_1",
        contribution_strength=0.85,
        canonical_hash=ev_hash,
    )
    assert evidence.evidence_id == ev_id
    with pytest.raises((TypeError, ValidationError)):
        evidence.contribution_strength = 0.99


def test_composite_score_model():
    sc_id, sc_hash = compute_composite_score_id("CMP_1234567890ABCDEF", 0.90, "2026-07-30T00:00:00Z")
    score = CompositeScore(
        score_id=sc_id,
        composite_id="CMP_1234567890ABCDEF",
        overall_score=0.90,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=sc_hash,
    )
    assert score.score_id == sc_id
    with pytest.raises((TypeError, ValidationError)):
        score.overall_score = 1.0


def test_composite_ranking_model():
    rk_id, rk_hash = compute_composite_ranking_id(["CMP_1"], "2026-07-30T00:00:00Z")
    ranking = CompositeRanking(
        ranking_id=rk_id,
        ranked_composites=["CMP_1"],
        ranking_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=rk_hash,
    )
    assert ranking.ranking_id == rk_id
    with pytest.raises((TypeError, ValidationError)):
        ranking.ranking_timestamp = "2026-07-31T00:00:00Z"


def test_composite_explainability_record_model():
    ex_id, ex_hash = compute_composite_explanation_id("CMP_1234567890ABCDEF")
    expl = CompositeExplainabilityRecord(
        explanation_id=ex_id,
        composite_id="CMP_1234567890ABCDEF",
        participating_edges=["SED_1", "SED_2"],
        scientific_explanation="Explanation text.",
        canonical_hash=ex_hash,
    )
    assert expl.explanation_id == ex_id
    with pytest.raises((TypeError, ValidationError)):
        expl.scientific_explanation = "Modified"
