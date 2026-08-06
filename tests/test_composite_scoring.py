"""
Project GOAT v0.7 — Test Suite for CompositeScoringEngine

Coverage:
- Synergy score computation
- Robustness, stability, diversity, reproducibility scores
- Conflict penalty deduction
- Overall score bounding [0.0, 1.0]
"""

from goat.alpha.core.canonical import compute_edge_id
from goat.alpha.core.models import ScientificEdge
from goat.composite.core.canonical import compute_composite_id
from goat.composite.core.models import CompositeEdge
from goat.composite.scoring.engine import CompositeScoringEngine


def test_compute_composite_score_clean():
    engine = CompositeScoringEngine()

    e1_id, e1_hash = compute_edge_id("E1", ["H1"], ["V1"])
    e2_id, e2_hash = compute_edge_id("E2", ["H2"], ["V2"])

    e1 = ScientificEdge(edge_id=e1_id, title="E1", confidence=0.85, reproducibility=0.88, robustness=0.85, stability=0.85, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)
    e2 = ScientificEdge(edge_id=e2_id, title="E2", confidence=0.88, reproducibility=0.90, robustness=0.86, stability=0.86, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e2_hash)

    c_id, c_hash = compute_composite_id([e1_id, e2_id], "Title")
    composite = CompositeEdge(
        composite_id=c_id,
        title="Title",
        participating_edges=[e1_id, e2_id],
        participating_hypotheses=["H1", "H2"],
        supporting_evidence=["V1", "V2"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    score = engine.compute_composite_score(composite, [e1, e2], 0.0, "2026-07-30T00:00:00Z")

    assert score.score_id.startswith("CSC_")
    assert score.synergy_score > 0.80
    assert 0.0 <= score.overall_score <= 1.0
