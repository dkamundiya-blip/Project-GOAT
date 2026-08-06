"""
Project GOAT v0.9 — Dedicated Tests for Edge Scoring Engine
"""

import pytest

from goat.edge_discovery.core.canonical import compute_edge_candidate_id
from goat.edge_discovery.core.enums import EdgeCategory, QualityTier
from goat.edge_discovery.core.models import EdgeCandidate
from goat.edge_discovery.scoring.engine import EdgeScoringEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
OBS_COUNTS = [1, 5, 10, 25, 50, 75, 100, 250, 500, 1000]
CONFIDENCES = [0.10, 0.30, 0.50, 0.70, 0.85, 0.90, 0.95, 0.99]
CATEGORIES = list(EdgeCategory)


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("n_obs", OBS_COUNTS)
@pytest.mark.parametrize("conf", CONFIDENCES[:4])
@pytest.mark.parametrize("cat", CATEGORIES[:3])
def test_edge_scoring_engine_matrix(
    index_type: SyntheticIndexType, n_obs: int, conf: float, cat: EdgeCategory
) -> None:
    scorer = EdgeScoringEngine()
    c_id, c_hash = compute_edge_candidate_id("Edge A", cat.value, ["EPT_1"], index_type.value)
    candidate = EdgeCandidate(
        candidate_id=c_id,
        name="Edge A",
        category=cat,
        symbol=index_type.value,
        pattern_ids=["EPT_1"],
        hypothesis_statement="Test hypothesis statement.",
        confidence_level=conf,
        observation_count=n_obs,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=c_hash,
    )

    score = scorer.score_candidate(candidate)
    assert score.score_id.startswith("SCR_")
    assert score.candidate_id == c_id
    assert 0.0 <= score.overall_score <= 100.0
    assert isinstance(score.quality_tier, QualityTier)
