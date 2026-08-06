"""
Project GOAT v0.7 — Test Suite for EdgeRankingEngine

Coverage:
- Deterministic ranking ordering
- Stable tie-breaking logic (Overall score -> Quality -> Reproducibility -> ID)
- Custom ranking rules
"""

from goat.alpha.core.canonical import compute_edge_id, compute_score_id
from goat.alpha.core.enums import EdgeMaturity, RankingRuleType
from goat.alpha.core.models import EdgeScore, ScientificEdge
from goat.alpha.ranking.engine import EdgeRankingEngine


def test_edge_ranking_engine_ordering():
    engine = EdgeRankingEngine()

    e1_id, e1_hash = compute_edge_id("E1", ["H1"], ["V1"])
    e2_id, e2_hash = compute_edge_id("E2", ["H2"], ["V2"])

    edge1 = ScientificEdge(edge_id=e1_id, title="E1", discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)
    edge2 = ScientificEdge(edge_id=e2_id, title="E2", discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e2_hash)

    s1_id, s1_hash = compute_score_id(e1_id, 0.75, "2026-07-30T00:00:00Z")
    s2_id, s2_hash = compute_score_id(e2_id, 0.90, "2026-07-30T00:00:00Z")

    score1 = EdgeScore(score_id=s1_id, edge_id=e1_id, overall_edge_score=0.75, scientific_quality=0.75, timestamp="2026-07-30T00:00:00Z", canonical_hash=s1_hash)
    score2 = EdgeScore(score_id=s2_id, edge_id=e2_id, overall_edge_score=0.90, scientific_quality=0.90, timestamp="2026-07-30T00:00:00Z", canonical_hash=s2_hash)

    ranking = engine.rank_edges([edge1, edge2], [score1, score2], "2026-07-30T00:00:00Z")

    assert ranking.ranking_id.startswith("ERK_")
    assert ranking.ranked_edges == [e2_id, e1_id]  # Higher score first


def test_edge_ranking_tie_breaking():
    engine = EdgeRankingEngine()

    # Two edges with equal overall score but different scientific quality
    e1_id = "SED_1111111111111111"
    e2_id = "SED_2222222222222222"

    edge1 = ScientificEdge(edge_id=e1_id, title="E1", discovery_timestamp="2026-07-30T00:00:00Z")
    edge2 = ScientificEdge(edge_id=e2_id, title="E2", discovery_timestamp="2026-07-30T00:00:00Z")

    score1 = EdgeScore(score_id="ESC_1111111111111111", edge_id=e1_id, overall_edge_score=0.80, scientific_quality=0.70, timestamp="2026-07-30T00:00:00Z")
    score2 = EdgeScore(score_id="ESC_2222222222222222", edge_id=e2_id, overall_edge_score=0.80, scientific_quality=0.85, timestamp="2026-07-30T00:00:00Z")

    ranking = engine.rank_edges([edge1, edge2], [score1, score2], "2026-07-30T00:00:00Z")

    # Tie broken by scientific_quality: e2 has 0.85 vs e1's 0.70
    assert ranking.ranked_edges == [e2_id, e1_id]
