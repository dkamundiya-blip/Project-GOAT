"""
Project GOAT v0.9 — Dedicated Tests for Edge Discovery Reporting Generator
"""

import json
import pytest

from goat.edge_discovery.core.canonical import (
    compute_discovery_decision_id,
    compute_discovery_summary_id,
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
    DiscoveryDecision,
    DiscoverySummary,
    EdgeCandidate,
    EdgeScore,
    NoveltyAssessment,
)
from goat.edge_discovery.reporting.reports import EdgeDiscoveryReportGenerator
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_edge_discovery_reporting(index_type: SyntheticIndexType) -> None:
    reporter = EdgeDiscoveryReportGenerator()

    c_id, c_hash = compute_edge_candidate_id("Edge C", "STATISTICAL_ARBITRAGE", ["EPT_1"], index_type.value)
    candidate = EdgeCandidate(
        candidate_id=c_id,
        name="Edge C",
        category=EdgeCategory.STATISTICAL_ARBITRAGE,
        symbol=index_type.value,
        pattern_ids=["EPT_1"],
        hypothesis_statement="Statement C",
        confidence_level=0.95,
        observation_count=50,
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

    sum_id, sum_hash = compute_discovery_summary_id("2026-01-01T00:00:00Z", 1, 1)
    summary = DiscoverySummary(
        summary_id=sum_id,
        timestamp="2026-01-01T00:00:00Z",
        total_patterns=2,
        total_clusters=1,
        total_candidates=1,
        total_validated=1,
        total_rejected=0,
        category_counts={"STATISTICAL_ARBITRAGE": 1},
        tier_counts={"HIGH_QUALITY": 1},
        metadata={},
        canonical_hash=sum_hash,
    )

    exec_rep = reporter.generate_executive_report(summary)
    cand_rep = reporter.generate_edge_discovery_report(candidate)
    nov_rep = reporter.generate_novelty_report(novelty)
    score_rep = reporter.generate_scoring_report(score)
    summary_rep = reporter.generate_summary_report(decision)

    assert "# QUANTITATIVE EDGE DISCOVERY EXECUTIVE REPORT" in exec_rep
    assert "# QUANTITATIVE EDGE CANDIDATE REPORT" in cand_rep
    assert "# EDGE CANDIDATE NOVELTY REPORT" in nov_rep
    assert "# EDGE QUALITY SCORING REPORT" in score_rep
    assert "# DISCOVERY PROTOCOL VALIDATION REPORT" in summary_rep

    json_str = reporter.export_canonical_json(candidate)
    data = json.loads(json_str)
    assert data["candidate_id"] == candidate.candidate_id
    assert data["canonical_hash"] == candidate.canonical_hash
