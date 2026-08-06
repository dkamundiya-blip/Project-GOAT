"""
Project GOAT v0.9 — Dedicated Tests for Edge Discovery Domain Models & Canonical Hashing
"""

import pytest
from pydantic import ValidationError

from goat.edge_discovery.core.canonical import (
    compute_canonical_sha256,
    compute_discovery_decision_id,
    compute_discovery_summary_id,
    compute_edge_candidate_id,
    compute_edge_pattern_id,
    compute_edge_score_id,
    compute_novelty_assessment_id,
    compute_pattern_cluster_id,
    serialize_canonical_json,
)
from goat.edge_discovery.core.enums import (
    EdgeCategory,
    NoveltyStatus,
    PatternType,
    QualityTier,
    RejectionReason,
    ValidationStatus,
)
from goat.edge_discovery.core.models import (
    DiscoveryDecision,
    DiscoverySummary,
    EdgeCandidate,
    EdgePattern,
    EdgeScore,
    NoveltyAssessment,
    PatternCluster,
)
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
CATEGORIES = list(EdgeCategory)
PATTERN_TYPES = list(PatternType)
CONFIDENCES = [0.50, 0.75, 0.90, 0.95, 0.99]
SAMPLE_SIZES = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
EFFECT_SIZES = [0.01, 0.05, 0.10, 0.25, 0.50]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("category", CATEGORIES)
@pytest.mark.parametrize("conf", CONFIDENCES)
@pytest.mark.parametrize("obs_count", [10, 50, 100, 500, 1000, 5000, 10000])
def test_edge_candidate_model_matrix(
    index_type: SyntheticIndexType, category: EdgeCategory, conf: float, obs_count: int
) -> None:
    c_id, h_digest = compute_edge_candidate_id("Test Edge", category.value, ["EPT_1"], index_type.value)
    candidate = EdgeCandidate(
        candidate_id=c_id,
        name="Test Edge",
        category=category,
        symbol=index_type.value,
        pattern_ids=["EPT_1"],
        hypothesis_statement="Test hypothesis proposition.",
        confidence_level=conf,
        observation_count=obs_count,
        timestamp="2026-01-01T00:00:00Z",
        metadata={"sym": index_type.value},
        canonical_hash=h_digest,
    )
    assert candidate.candidate_id.startswith("EDC_")
    assert candidate.canonical_hash == h_digest
    assert candidate.category == category
    assert candidate.confidence_level == conf

    with pytest.raises(ValidationError):
        candidate.confidence_level = 1.5  # type: ignore


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("p_type", PATTERN_TYPES)
@pytest.mark.parametrize("sample_size", SAMPLE_SIZES)
@pytest.mark.parametrize("eff", EFFECT_SIZES)
def test_edge_pattern_model_matrix(
    index_type: SyntheticIndexType, p_type: PatternType, sample_size: int, eff: float
) -> None:
    p_id, h_digest = compute_edge_pattern_id(p_type.value, index_type.value, sample_size, 0.01)
    pattern = EdgePattern(
        pattern_id=p_id,
        pattern_type=p_type,
        symbol=index_type.value,
        sample_size=sample_size,
        effect_size=eff,
        statistical_significance=0.01,
        regime_consistency=0.90,
        observation_ids=["MSO_1"],
        metadata={},
        canonical_hash=h_digest,
    )
    assert pattern.pattern_id.startswith("EPT_")
    assert pattern.canonical_hash == h_digest
    assert pattern.pattern_type == p_type


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("sample_size", SAMPLE_SIZES[:5])
def test_pattern_cluster_model(index_type: SyntheticIndexType, sample_size: int) -> None:
    c_id, h_digest = compute_pattern_cluster_id("Cluster A", ["EPT_1", "EPT_2"])
    cluster = PatternCluster(
        cluster_id=c_id,
        cluster_name="Cluster A",
        pattern_ids=["EPT_1", "EPT_2"],
        centroid_pattern_id="EPT_1",
        intra_cluster_similarity=0.95,
        metadata={"sym": index_type.value, "size": sample_size},
        canonical_hash=h_digest,
    )
    assert cluster.cluster_id.startswith("CLS_")
    assert cluster.canonical_hash == h_digest


@pytest.mark.parametrize("status", list(NoveltyStatus))
@pytest.mark.parametrize("score", [0.0, 0.25, 0.50, 0.75, 1.0])
def test_novelty_assessment_model(status: NoveltyStatus, score: float) -> None:
    n_id, h_digest = compute_novelty_assessment_id("EDC_1", score, status.value)
    novelty = NoveltyAssessment(
        assessment_id=n_id,
        candidate_id="EDC_1",
        max_similarity_score=score,
        closest_archived_edge_id=None,
        status=status,
        is_novel=(status != NoveltyStatus.DUPLICATE_EXISTS),
        metadata={},
        canonical_hash=h_digest,
    )
    assert novelty.assessment_id.startswith("NOV_")
    assert novelty.canonical_hash == h_digest


@pytest.mark.parametrize("tier", list(QualityTier))
@pytest.mark.parametrize("overall_val", [20.0, 45.0, 60.0, 80.0, 95.0])
def test_edge_score_model(tier: QualityTier, overall_val: float) -> None:
    s_id, h_digest = compute_edge_score_id("EDC_1", overall_val, tier.value)
    score = EdgeScore(
        score_id=s_id,
        candidate_id="EDC_1",
        overall_score=overall_val,
        support_score=90.0,
        stability_score=85.0,
        consistency_score=90.0,
        robustness_score=88.0,
        live_compatibility_score=90.0,
        quality_tier=tier,
        metadata={},
        canonical_hash=h_digest,
    )
    assert score.score_id.startswith("SCR_")
    assert score.canonical_hash == h_digest


@pytest.mark.parametrize("v_status", list(ValidationStatus))
@pytest.mark.parametrize("reason", list(RejectionReason))
def test_discovery_decision_model(v_status: ValidationStatus, reason: RejectionReason) -> None:
    d_id, h_digest = compute_discovery_decision_id("EDC_1", v_status.value, reason.value, "2026-01-01T00:00:00Z")
    decision = DiscoveryDecision(
        decision_id=d_id,
        candidate_id="EDC_1",
        status=v_status,
        rejection_reason=reason,
        novelty_assessment_id="NOV_1",
        score_id="SCR_1",
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=h_digest,
    )
    assert decision.decision_id.startswith("DSC_")
    assert decision.canonical_hash == h_digest


@pytest.mark.parametrize("cand_count", [0, 5, 25, 100, 500, 1000])
def test_discovery_summary_model(cand_count: int) -> None:
    s_id, h_digest = compute_discovery_summary_id("2026-01-01T00:00:00Z", cand_count, cand_count)
    summary = DiscoverySummary(
        summary_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        total_patterns=cand_count * 2,
        total_clusters=cand_count,
        total_candidates=cand_count,
        total_validated=cand_count,
        total_rejected=0,
        category_counts={"STATISTICAL_ARBITRAGE": cand_count},
        tier_counts={"HIGH_QUALITY": cand_count},
        metadata={},
        canonical_hash=h_digest,
    )
    assert summary.summary_id.startswith("DSM_")
    assert summary.canonical_hash == h_digest
