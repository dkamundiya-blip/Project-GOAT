"""
Project GOAT v0.9 — Dedicated Tests for Novelty Assessment Engine
"""

import pytest

from goat.edge_discovery.core.canonical import compute_edge_candidate_id
from goat.edge_discovery.core.enums import EdgeCategory, NoveltyStatus
from goat.edge_discovery.core.models import EdgeCandidate
from goat.edge_discovery.novelty.engine import NoveltyAssessmentEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
CATEGORIES = list(EdgeCategory)
SIM_THRESHOLDS = [0.50, 0.70, 0.85, 0.95]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("category", CATEGORIES)
@pytest.mark.parametrize("thresh", SIM_THRESHOLDS)
def test_novelty_assessment_engine_matrix(
    index_type: SyntheticIndexType, category: EdgeCategory, thresh: float
) -> None:
    evaluator = NoveltyAssessmentEngine()

    c1_id, c1_hash = compute_edge_candidate_id("Edge 1", category.value, ["EPT_1"], index_type.value)
    c1 = EdgeCandidate(
        candidate_id=c1_id,
        name="Edge 1",
        category=category,
        symbol=index_type.value,
        pattern_ids=["EPT_1"],
        hypothesis_statement="Statement 1",
        confidence_level=0.95,
        observation_count=50,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=c1_hash,
    )

    nov1 = evaluator.evaluate_novelty(c1, [], max_similarity_threshold=thresh)
    assert nov1.assessment_id.startswith("NOV_")
    assert nov1.status == NoveltyStatus.GENUINELY_NOVEL
    assert nov1.is_novel is True

    c2_id, c2_hash = compute_edge_candidate_id("Edge 2", category.value, ["EPT_1"], index_type.value)
    c2 = EdgeCandidate(
        candidate_id=c2_id,
        name="Edge 2",
        category=category,
        symbol=index_type.value,
        pattern_ids=["EPT_1"],
        hypothesis_statement="Statement 2",
        confidence_level=0.95,
        observation_count=50,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=c2_hash,
    )

    nov2 = evaluator.evaluate_novelty(c2, [c1], max_similarity_threshold=thresh)
    assert nov2.status == NoveltyStatus.DUPLICATE_EXISTS
    assert nov2.is_novel is False
