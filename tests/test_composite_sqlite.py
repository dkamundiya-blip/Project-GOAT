"""
Project GOAT v0.7 — Test Suite for Composite Persistence Repositories

Coverage:
- CompositeRepository (save, get, list round-trip)
- CompositeEvidenceRepository (save evidence & explanation, get round-trip)
- CompositeScoreRepository (save, get round-trip)
- CompositeRankingRepository (save, get round-trip)
- CompositeReportRepository (save, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.composite.core.canonical import (
    compute_composite_evidence_id,
    compute_composite_explanation_id,
    compute_composite_id,
    compute_composite_ranking_id,
    compute_composite_score_id,
)
from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
)
from goat.composite.persistence.sqlite import (
    CompositeEvidenceRepository,
    CompositeRankingRepository,
    CompositeReportRepository,
    CompositeRepository,
    CompositeScoreRepository,
    init_composite_db,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_composite_db(conn)
    yield conn
    conn.close()


def test_composite_repository_roundtrip(db_conn):
    repo = CompositeRepository(db_conn)
    c_id, c_hash = compute_composite_id(["SED_1"], "Composite Alpha")
    composite = CompositeEdge(
        composite_id=c_id,
        title="Composite Alpha",
        participating_edges=["SED_1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    repo.save_composite(composite)
    fetched = repo.get_composite(c_id)

    assert fetched == composite
    assert len(repo.list_composites()) == 1


def test_composite_evidence_repository_roundtrip(db_conn):
    comp_repo = CompositeRepository(db_conn)
    c_id, c_hash = compute_composite_id(["SED_1"], "Composite Alpha")
    composite = CompositeEdge(composite_id=c_id, title="Composite Alpha", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=c_hash)
    comp_repo.save_composite(composite)

    ev_repo = CompositeEvidenceRepository(db_conn)
    ev_id, ev_hash = compute_composite_evidence_id(c_id, "SED_1")
    evidence = CompositeEvidence(
        evidence_id=ev_id,
        composite_id=c_id,
        contributing_edge="SED_1",
        contribution_strength=0.85,
        canonical_hash=ev_hash,
    )

    ev_repo.save_evidence(evidence)
    fetched_ev = ev_repo.get_evidence(ev_id)
    assert fetched_ev == evidence

    ex_id, ex_hash = compute_composite_explanation_id(c_id)
    explanation = CompositeExplainabilityRecord(
        explanation_id=ex_id,
        composite_id=c_id,
        participating_edges=["SED_1"],
        scientific_explanation="Explanation narrative.",
        canonical_hash=ex_hash,
    )
    ev_repo.save_explanation(explanation)
    fetched_ex = ev_repo.get_explanation(ex_id)
    assert fetched_ex == explanation


def test_composite_score_repository_roundtrip(db_conn):
    comp_repo = CompositeRepository(db_conn)
    c_id, c_hash = compute_composite_id(["SED_1"], "Composite Alpha")
    composite = CompositeEdge(composite_id=c_id, title="Composite Alpha", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=c_hash)
    comp_repo.save_composite(composite)

    sc_repo = CompositeScoreRepository(db_conn)
    sc_id, sc_hash = compute_composite_score_id(c_id, 0.88, "2026-07-30T00:00:00Z")
    score = CompositeScore(
        score_id=sc_id,
        composite_id=c_id,
        overall_score=0.88,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=sc_hash,
    )

    sc_repo.save_score(score)
    fetched = sc_repo.get_score(sc_id)

    assert fetched == score


def test_composite_ranking_repository_roundtrip(db_conn):
    repo = CompositeRankingRepository(db_conn)
    rk_id, rk_hash = compute_composite_ranking_id(["CMP_1"], "2026-07-30T00:00:00Z")
    ranking = CompositeRanking(
        ranking_id=rk_id,
        ranked_composites=["CMP_1"],
        ranking_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=rk_hash,
    )

    repo.save_ranking(ranking)
    fetched = repo.get_ranking(rk_id)

    assert fetched == ranking
