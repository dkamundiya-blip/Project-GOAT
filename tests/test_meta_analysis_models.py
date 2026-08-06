"""
Project GOAT v0.7 — Test Suite for Meta-Analysis Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (ResearchCluster, ResearchPattern, ResearchTrend, ScientificSummary, ResearchIntelligenceMetrics, MetaAnalysisResult)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.meta_analysis.core.canonical import (
    compute_cluster_id,
    compute_meta_analysis_id,
    compute_metrics_id,
    compute_pattern_id,
    compute_summary_id,
    compute_trend_id,
    serialize_canonical_json,
)
from goat.meta_analysis.core.enums import ClusterType, PatternCategory, TrendDirection
from goat.meta_analysis.core.models import (
    MetaAnalysisResult,
    ResearchCluster,
    ResearchIntelligenceMetrics,
    ResearchPattern,
    ResearchTrend,
    ScientificSummary,
)


def test_cluster_id_determinism():
    id1, hash1 = compute_cluster_id("Cluster A", ["N1", "N2"])
    id2, hash2 = compute_cluster_id("Cluster A", ["N2", "N1"])
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RCL_")


def test_pattern_id_determinism():
    id1, hash1 = compute_pattern_id("Pattern A", ["E1", "E2"])
    id2, hash2 = compute_pattern_id("Pattern A", ["E2", "E1"])
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RPT_")


def test_trend_id_determinism():
    id1, hash1 = compute_trend_id("Momentum", "GROWING")
    id2, hash2 = compute_trend_id("Momentum", "GROWING")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RTD_")


def test_summary_id_determinism():
    id1, hash1 = compute_summary_id(10, 5, "2026-07-30T00:00:00Z")
    id2, hash2 = compute_summary_id(10, 5, "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SCS_")


def test_metrics_id_determinism():
    id1, hash1 = compute_metrics_id(0.8, 0.9, "2026-07-30T00:00:00Z")
    id2, hash2 = compute_metrics_id(0.8, 0.9, "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RIM_")


def test_meta_analysis_id_determinism():
    id1, hash1 = compute_meta_analysis_id(["K1"], ["C1"], ["P1"])
    id2, hash2 = compute_meta_analysis_id(["K1"], ["C1"], ["P1"])
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("MAR_")


def test_research_cluster_model():
    c_id, c_hash = compute_cluster_id("Title", ["N1"])
    cluster = ResearchCluster(
        cluster_id=c_id,
        title="Title",
        cluster_type=ClusterType.THEME,
        participating_nodes=["N1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )
    assert cluster.cluster_id == c_id
    with pytest.raises((TypeError, ValidationError)):
        cluster.title = "New Title"


def test_research_pattern_model():
    p_id, p_hash = compute_pattern_id("Pattern Name", ["E1"])
    pattern = ResearchPattern(
        pattern_id=p_id,
        pattern_name="Pattern Name",
        category=PatternCategory.RECURRING_EVIDENCE,
        evidence=["E1"],
        canonical_hash=p_hash,
    )
    assert pattern.pattern_id == p_id
    with pytest.raises((TypeError, ValidationError)):
        pattern.frequency = 10


def test_research_trend_model():
    t_id, t_hash = compute_trend_id("Topic", "GROWING")
    trend = ResearchTrend(
        trend_id=t_id,
        topic="Topic",
        direction=TrendDirection.GROWING,
        canonical_hash=t_hash,
    )
    assert trend.trend_id == t_id
    with pytest.raises((TypeError, ValidationError)):
        trend.strength = 1.0


def test_scientific_summary_model():
    s_id, s_hash = compute_summary_id(1, 1, "2026-07-30T00:00:00Z")
    summary = ScientificSummary(
        summary_id=s_id,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=s_hash,
    )
    assert summary.summary_id == s_id
    with pytest.raises((TypeError, ValidationError)):
        summary.validated_knowledge_count = 5


def test_research_intelligence_metrics_model():
    m_id, m_hash = compute_metrics_id(0.5, 0.5, "2026-07-30T00:00:00Z")
    metrics = ResearchIntelligenceMetrics(
        metrics_id=m_id,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=m_hash,
    )
    assert metrics.metrics_id == m_id
    with pytest.raises((TypeError, ValidationError)):
        metrics.knowledge_density = 0.9
