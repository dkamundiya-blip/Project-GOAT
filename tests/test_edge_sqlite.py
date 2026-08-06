"""
Project GOAT v0.9 — Dedicated Tests for Edge Discovery SQLite Persistence Repositories
"""

import sqlite3
import pytest

from goat.edge_discovery.core.canonical import (
    compute_discovery_decision_id,
    compute_edge_candidate_id,
    compute_edge_pattern_id,
    compute_edge_score_id,
    compute_novelty_assessment_id,
    compute_pattern_cluster_id,
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
    EdgeCandidate,
    EdgePattern,
    EdgeScore,
    NoveltyAssessment,
    PatternCluster,
)
from goat.edge_discovery.persistence.sqlite import EdgeDiscoveryPersistenceContext
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_sqlite_repository_roundtrips(index_type: SyntheticIndexType) -> None:
    db = EdgeDiscoveryPersistenceContext(":memory:")

    # Pragma checks
    cursor = db.conn.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1

    p_id, p_hash = compute_edge_pattern_id("VOLATILITY_EXPANSION_PATTERN", index_type.value, 50, 0.01)
    pattern = EdgePattern(
        pattern_id=p_id,
        pattern_type=PatternType.VOLATILITY_EXPANSION_PATTERN,
        symbol=index_type.value,
        sample_size=50,
        effect_size=0.15,
        statistical_significance=0.01,
        regime_consistency=0.90,
        observation_ids=["MSO_1"],
        metadata={},
        canonical_hash=p_hash,
    )
    db.patterns.save(pattern)

    cls_id, cls_hash = compute_pattern_cluster_id("Cluster A", [p_id])
    cluster = PatternCluster(
        cluster_id=cls_id,
        cluster_name="Cluster A",
        pattern_ids=[p_id],
        centroid_pattern_id=p_id,
        intra_cluster_similarity=1.0,
        metadata={},
        canonical_hash=cls_hash,
    )
    db.clusters.save(cluster)

    c_id, c_hash = compute_edge_candidate_id("Candidate A", "REGIME_TRANSITION", [p_id], index_type.value)
    candidate = EdgeCandidate(
        candidate_id=c_id,
        name="Candidate A",
        category=EdgeCategory.REGIME_TRANSITION,
        symbol=index_type.value,
        pattern_ids=[p_id],
        hypothesis_statement="Statement",
        confidence_level=0.95,
        observation_count=50,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=c_hash,
    )
    db.edges.save(candidate)

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
    db.novelties.save(novelty)

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
    db.scores.save(score)

    d_id, d_hash = compute_discovery_decision_id(c_id, "PASSED", "NONE", "2026-01-01T00:00:00Z")
    decision = DiscoveryDecision(
        decision_id=d_id,
        candidate_id=c_id,
        status=ValidationStatus.PASSED,
        rejection_reason=RejectionReason.NONE,
        novelty_assessment_id=n_id,
        score_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=d_hash,
    )
    db.decisions.save(decision)

    # Retrieval assertions
    fetched_cand = db.edges.get_by_id(c_id)
    assert fetched_cand is not None
    assert fetched_cand.candidate_id == c_id
    assert fetched_cand.canonical_hash == c_hash

    fetched_dec = db.decisions.get_by_id(d_id)
    assert fetched_dec is not None
    assert fetched_dec.decision_id == d_id
    assert fetched_dec.status == ValidationStatus.PASSED

    db.close()


def test_sqlite_foreign_key_enforcement() -> None:
    db = EdgeDiscoveryPersistenceContext(":memory:")
    # Try inserting NoveltyAssessment referencing non-existent candidate -> raises IntegrityError
    novelty = NoveltyAssessment(
        assessment_id="NOV_BOGUS",
        candidate_id="EDC_BOGUS",
        max_similarity_score=0.10,
        closest_archived_edge_id=None,
        status=NoveltyStatus.GENUINELY_NOVEL,
        is_novel=True,
        metadata={},
        canonical_hash="HASH",
    )

    with pytest.raises(sqlite3.IntegrityError):
        db.novelties.save(novelty)

    db.close()
