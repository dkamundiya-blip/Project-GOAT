"""
Project GOAT v0.7 — Test Suite for CompositeRankingEngine

Coverage:
- Deterministic ranking ordering
- Stable tie-breaking logic (Overall score -> Synergy -> Robustness -> ID)
"""

from goat.composite.core.canonical import compute_composite_id, compute_composite_score_id
from goat.composite.core.models import CompositeEdge, CompositeScore
from goat.composite.ranking.engine import CompositeRankingEngine


def test_composite_ranking_engine_ordering():
    engine = CompositeRankingEngine()

    c1_id, c1_hash = compute_composite_id(["SED_1"], "C1")
    c2_id, c2_hash = compute_composite_id(["SED_2"], "C2")

    comp1 = CompositeEdge(composite_id=c1_id, title="C1", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=c1_hash)
    comp2 = CompositeEdge(composite_id=c2_id, title="C2", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=c2_hash)

    s1_id, s1_hash = compute_composite_score_id(c1_id, 0.75, "2026-07-30T00:00:00Z")
    s2_id, s2_hash = compute_composite_score_id(c2_id, 0.90, "2026-07-30T00:00:00Z")

    score1 = CompositeScore(score_id=s1_id, composite_id=c1_id, overall_score=0.75, synergy_score=0.75, timestamp="2026-07-30T00:00:00Z", canonical_hash=s1_hash)
    score2 = CompositeScore(score_id=s2_id, composite_id=c2_id, overall_score=0.90, synergy_score=0.90, timestamp="2026-07-30T00:00:00Z", canonical_hash=s2_hash)

    ranking = engine.rank_composites([comp1, comp2], [score1, score2], "2026-07-30T00:00:00Z")

    assert ranking.ranking_id.startswith("CRK_")
    assert ranking.ranked_composites == [c2_id, c1_id]  # Higher score first


def test_composite_ranking_tie_breaking():
    engine = CompositeRankingEngine()

    c1_id = "CMP_1111111111111111"
    c2_id = "CMP_2222222222222222"

    comp1 = CompositeEdge(composite_id=c1_id, title="C1", creation_timestamp="2026-07-30T00:00:00Z")
    comp2 = CompositeEdge(composite_id=c2_id, title="C2", creation_timestamp="2026-07-30T00:00:00Z")

    score1 = CompositeScore(score_id="CSC_1111111111111111", composite_id=c1_id, overall_score=0.80, synergy_score=0.70, timestamp="2026-07-30T00:00:00Z")
    score2 = CompositeScore(score_id="CSC_2222222222222222", composite_id=c2_id, overall_score=0.80, synergy_score=0.85, timestamp="2026-07-30T00:00:00Z")

    ranking = engine.rank_composites([comp1, comp2], [score1, score2], "2026-07-30T00:00:00Z")

    # Tie broken by synergy_score: c2 has 0.85 vs c1's 0.70
    assert ranking.ranked_composites == [c2_id, c1_id]
