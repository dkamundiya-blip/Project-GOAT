"""
Project GOAT v0.7 — Test Suite for EdgeScoringEngine

Coverage:
- Scientific edge multi-dimensional scoring (confidence, reproducibility, robustness, stability, evidence strength, quality, longevity)
- Conflict penalty deduction
- Overall edge quality score bounds [0.0, 1.0]
"""

from goat.alpha.core.canonical import compute_edge_id
from goat.alpha.core.enums import EdgeMaturity
from goat.alpha.core.models import ScientificEdge
from goat.alpha.scoring.engine import EdgeScoringEngine


def test_compute_edge_score_clean():
    engine = EdgeScoringEngine()

    e_id, e_hash = compute_edge_id("Edge Clean", ["HYP_1"], ["VAL_1", "VAL_2"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge Clean",
        maturity=EdgeMaturity.VALIDATED,
        originating_hypotheses=["HYP_1"],
        originating_validations=["VAL_1", "VAL_2"],
        supporting_evidence=["VAL_1", "VAL_2"],
        confidence=0.90,
        reproducibility=0.88,
        robustness=0.85,
        stability=0.85,
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    score = engine.compute_edge_score(edge, [], "2026-07-30T00:00:00Z")

    assert score.score_id.startswith("ESC_")
    assert score.conflict_penalty == 0.0
    assert 0.0 <= score.overall_edge_score <= 1.0
    assert score.scientific_quality > 0.80


def test_compute_edge_score_with_conflicts():
    engine = EdgeScoringEngine()

    e_id, e_hash = compute_edge_id("Edge Conflicted", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge Conflicted",
        maturity=EdgeMaturity.NEW,
        originating_hypotheses=["HYP_1"],
        originating_validations=["VAL_1"],
        supporting_evidence=["VAL_1"],
        confidence=0.70,
        reproducibility=0.60,
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    conflicts = [
        {"validation_a": "VAL_1", "validation_b": "VAL_OTHER", "conflict_type": "CONTRADICTED"},
    ]

    score = engine.compute_edge_score(edge, conflicts, "2026-07-30T00:00:00Z")

    assert score.conflict_penalty > 0.0
    assert score.overall_edge_score < 0.70
