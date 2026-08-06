"""
Project GOAT v0.7 — Test Suite for Scientific Alpha Persistence Repositories

Coverage:
- ScientificEdgeRepository (save, get, list round-trip)
- EdgeEvidenceRepository (save evidence & explanation, get round-trip)
- EdgeScoreRepository (save, get round-trip)
- EdgeRankingRepository (save, get round-trip)
- EdgeReportRepository (save, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.alpha.core.canonical import (
    compute_edge_id,
    compute_evidence_id,
    compute_explanation_id,
    compute_ranking_id,
    compute_score_id,
)
from goat.alpha.core.enums import EdgeMaturity, EvidenceSourceType
from goat.alpha.core.models import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    EdgeRanking,
    EdgeScore,
    ScientificEdge,
)
from goat.alpha.persistence.sqlite import (
    EdgeEvidenceRepository,
    EdgeRankingRepository,
    EdgeReportRepository,
    EdgeScoreRepository,
    ScientificEdgeRepository,
    init_alpha_db,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_alpha_db(conn)
    yield conn
    conn.close()


def test_scientific_edge_repository_roundtrip(db_conn):
    repo = ScientificEdgeRepository(db_conn)
    e_id, e_hash = compute_edge_id("Edge Alpha", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge Alpha",
        maturity=EdgeMaturity.VALIDATED,
        originating_hypotheses=["HYP_1"],
        originating_validations=["VAL_1"],
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    repo.save_edge(edge)
    fetched = repo.get_edge(e_id)

    assert fetched == edge
    assert len(repo.list_edges()) == 1


def test_edge_evidence_repository_roundtrip(db_conn):
    edge_repo = ScientificEdgeRepository(db_conn)
    e_id, e_hash = compute_edge_id("Edge Alpha", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(edge_id=e_id, title="Edge Alpha", discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e_hash)
    edge_repo.save_edge(edge)

    ev_repo = EdgeEvidenceRepository(db_conn)
    ev_id, ev_hash = compute_evidence_id(e_id, "VAL_1", "VALIDATION")
    evidence = EdgeEvidence(
        evidence_id=ev_id,
        edge_id=e_id,
        source_type=EvidenceSourceType.VALIDATION,
        source_reference="VAL_1",
        confidence=0.85,
        canonical_hash=ev_hash,
    )

    ev_repo.save_evidence(evidence)
    fetched_ev = ev_repo.get_evidence(ev_id)
    assert fetched_ev == evidence

    ex_id, ex_hash = compute_explanation_id(e_id, "HYP_1")
    explanation = EdgeExplainabilityRecord(
        explanation_id=ex_id,
        edge_id=e_id,
        origin="HYP_1",
        scientific_explanation="Explanation narrative.",
        canonical_hash=ex_hash,
    )
    ev_repo.save_explanation(explanation)
    fetched_ex = ev_repo.get_explanation(ex_id)
    assert fetched_ex == explanation


def test_edge_score_repository_roundtrip(db_conn):
    edge_repo = ScientificEdgeRepository(db_conn)
    e_id, e_hash = compute_edge_id("Edge Alpha", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(edge_id=e_id, title="Edge Alpha", discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e_hash)
    edge_repo.save_edge(edge)

    sc_repo = EdgeScoreRepository(db_conn)
    sc_id, sc_hash = compute_score_id(e_id, 0.88, "2026-07-30T00:00:00Z")
    score = EdgeScore(
        score_id=sc_id,
        edge_id=e_id,
        overall_edge_score=0.88,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=sc_hash,
    )

    sc_repo.save_score(score)
    fetched = sc_repo.get_score(sc_id)

    assert fetched == score


def test_edge_ranking_repository_roundtrip(db_conn):
    repo = EdgeRankingRepository(db_conn)
    rk_id, rk_hash = compute_ranking_id(["SED_1"], "2026-07-30T00:00:00Z")
    ranking = EdgeRanking(
        ranking_id=rk_id,
        ranked_edges=["SED_1"],
        ranking_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=rk_hash,
    )

    repo.save_ranking(ranking)
    fetched = repo.get_ranking(rk_id)

    assert fetched == ranking
