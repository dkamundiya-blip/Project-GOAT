"""
Project GOAT v0.9 — Dedicated Tests for Discovery Protocol Validation Engine
"""

import pytest

from goat.edge_discovery.core.canonical import (
    compute_edge_candidate_id,
    compute_edge_score_id,
    compute_novelty_assessment_id,
)
from goat.edge_discovery.core.enums import (
    EdgeCategory,
    NoveltyStatus,
    QualityTier,
    RejectionReason,
    ValidationStatus,
)
from goat.edge_discovery.core.models import (
    EdgeCandidate,
    EdgeScore,
    NoveltyAssessment,
)
from goat.edge_discovery.validation.engine import DiscoveryValidationEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
CATEGORIES = list(EdgeCategory)
OBS_COUNTS = [10, 25, 50, 100, 250, 500, 1000]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("category", CATEGORIES[:3])
@pytest.mark.parametrize("obs_cnt", OBS_COUNTS[:3])
def test_validation_engine_pass_matrix(
    index_type: SyntheticIndexType, category: EdgeCategory, obs_cnt: int
) -> None:
    validator = DiscoveryValidationEngine()

    c_id, c_hash = compute_edge_candidate_id("Edge A", category.value, ["EPT_1"], index_type.value)
    candidate = EdgeCandidate(
        candidate_id=c_id,
        name="Edge A",
        category=category,
        symbol=index_type.value,
        pattern_ids=["EPT_1"],
        hypothesis_statement="Statement",
        confidence_level=0.95,
        observation_count=obs_cnt,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=c_hash,
    )

    n_id, n_hash = compute_novelty_assessment_id(c_id, 0.10, "GENUINELY_NOVEL")
    novelty = NoveltyAssessment(
        assessment_id=n_id,
        candidate_id=c_id,
        max_similarity_score=0.10,
        closest_archived_edge_id=None,
        status=NoveltyStatus.GENUINELY_NOVEL,
        is_novel=True,
        metadata={},
        canonical_hash=n_hash,
    )

    s_id, s_hash = compute_edge_score_id(c_id, 85.0, "HIGH_QUALITY")
    score = EdgeScore(
        score_id=s_id,
        candidate_id=c_id,
        overall_score=85.0,
        support_score=90.0,
        stability_score=85.0,
        consistency_score=80.0,
        robustness_score=85.0,
        live_compatibility_score=85.0,
        quality_tier=QualityTier.HIGH_QUALITY,
        metadata={},
        canonical_hash=s_hash,
    )

    decision = validator.validate_candidate(candidate, novelty, score, min_observations=5)
    assert decision.decision_id.startswith("DSC_")
    assert decision.status == ValidationStatus.PASSED
    assert decision.rejection_reason == RejectionReason.NONE


@pytest.mark.parametrize("index_type", INDICES[:5])
@pytest.mark.parametrize(
    "obs_count, is_novel, conf, cons_score, overall_score, expected_reason",
    [
        (2, True, 0.95, 80.0, 80.0, RejectionReason.INSUFFICIENT_OBSERVATIONS),
        (50, False, 0.95, 80.0, 80.0, RejectionReason.DUPLICATE_EDGE),
        (50, True, 0.30, 80.0, 80.0, RejectionReason.POOR_CONFIDENCE),
        (50, True, 0.95, 10.0, 80.0, RejectionReason.SINGLE_REGIME_BEHAVIOR),
        (50, True, 0.95, 80.0, 20.0, RejectionReason.OVERFIT_EVIDENCE),
    ],
)
def test_validation_engine_rejections(
    index_type: SyntheticIndexType,
    obs_count: int,
    is_novel: bool,
    conf: float,
    cons_score: float,
    overall_score: float,
    expected_reason: RejectionReason,
) -> None:
    validator = DiscoveryValidationEngine()

    c_id, c_hash = compute_edge_candidate_id("Edge B", "REGIME_TRANSITION", ["EPT_1"], index_type.value)
    candidate = EdgeCandidate(
        candidate_id=c_id,
        name="Edge B",
        category=EdgeCategory.REGIME_TRANSITION,
        symbol=index_type.value,
        pattern_ids=["EPT_1"],
        hypothesis_statement="Statement",
        confidence_level=conf,
        observation_count=obs_count,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=c_hash,
    )

    n_id, n_hash = compute_novelty_assessment_id(c_id, 0.10 if is_novel else 0.95, "GENUINELY_NOVEL")
    novelty = NoveltyAssessment(
        assessment_id=n_id,
        candidate_id=c_id,
        max_similarity_score=0.10 if is_novel else 0.95,
        closest_archived_edge_id=None,
        status=NoveltyStatus.GENUINELY_NOVEL if is_novel else NoveltyStatus.DUPLICATE_EXISTS,
        is_novel=is_novel,
        metadata={},
        canonical_hash=n_hash,
    )

    s_id, s_hash = compute_edge_score_id(c_id, overall_score, "MARGINAL")
    score = EdgeScore(
        score_id=s_id,
        candidate_id=c_id,
        overall_score=overall_score,
        support_score=50.0,
        stability_score=50.0,
        consistency_score=cons_score,
        robustness_score=50.0,
        live_compatibility_score=50.0,
        quality_tier=QualityTier.MARGINAL,
        metadata={},
        canonical_hash=s_hash,
    )

    decision = validator.validate_candidate(candidate, novelty, score)
    assert decision.status == ValidationStatus.REJECTED
    assert decision.rejection_reason == expected_reason
