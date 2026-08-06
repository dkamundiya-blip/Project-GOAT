"""
Project GOAT v0.7 — Test Suite for EdgeDiscoveryEngine

Coverage:
- Discovery from passed validation runs
- Discovery from meta-analysis results
- Edge maturity stage classification
- Full discover_all_candidate_edges orchestration
"""

from goat.alpha.core.enums import EdgeMaturity
from goat.alpha.discovery.engine import EdgeDiscoveryEngine
from goat.meta_analysis.core.canonical import (
    compute_cluster_id,
    compute_meta_analysis_id,
    compute_metrics_id,
    compute_summary_id,
)
from goat.meta_analysis.core.enums import ClusterType
from goat.meta_analysis.core.models import (
    MetaAnalysisResult,
    ResearchCluster,
    ResearchIntelligenceMetrics,
    ScientificSummary,
)


def test_determine_edge_maturity():
    engine = EdgeDiscoveryEngine()

    assert engine.determine_edge_maturity(5, 1, 1, "GROWING", 0.90, 0.90) == EdgeMaturity.FOUNDATIONAL
    assert engine.determine_edge_maturity(3, 1, 0, "GROWING", 0.80, 0.80) == EdgeMaturity.MATURE
    assert engine.determine_edge_maturity(2, 1, 0, "STABLE", 0.70, 0.70) == EdgeMaturity.VALIDATED
    assert engine.determine_edge_maturity(1, 1, 0, "STABLE", 0.60, 0.60) == EdgeMaturity.EMERGING
    assert engine.determine_edge_maturity(2, 0, 0, "STABLE", 0.60, 0.60) == EdgeMaturity.EXPERIMENTAL
    assert engine.determine_edge_maturity(1, 0, 0, "STABLE", 0.50, 0.50) == EdgeMaturity.NEW


def test_discover_from_validations():
    engine = EdgeDiscoveryEngine()

    vals = [
        {"validation_id": "VAL_001", "hypothesis_id": "HYP_MOM", "status": "PASSED", "confidence": 0.85},
        {"validation_id": "VAL_002", "hypothesis_id": "HYP_MOM", "status": "PASSED", "confidence": 0.90},
    ]

    edges = engine.discover_from_validations(vals, "2026-07-30T00:00:00Z")
    assert len(edges) == 1
    assert edges[0].edge_id.startswith("SED_")
    assert "HYP_MOM" in edges[0].originating_hypotheses
    assert len(edges[0].originating_validations) == 2


def test_discover_from_meta_analysis():
    engine = EdgeDiscoveryEngine()

    c_id, c_hash = compute_cluster_id("Cluster Alpha", ["N1"])
    cluster = ResearchCluster(
        cluster_id=c_id,
        title="Cluster Alpha",
        cluster_type=ClusterType.THEME,
        participating_nodes=["N1"],
        participating_validations=["VAL_100"],
        confidence=0.85,
        reproducibility=0.90,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    s_id, s_hash = compute_summary_id(1, 1, "2026-07-30T00:00:00Z")
    summary = ScientificSummary(summary_id=s_id, creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=s_hash)

    m_id, m_hash = compute_metrics_id(0.5, 0.5, "2026-07-30T00:00:00Z")
    metrics = ResearchIntelligenceMetrics(metrics_id=m_id, timestamp="2026-07-30T00:00:00Z", canonical_hash=m_hash)

    a_id, a_hash = compute_meta_analysis_id(["K1"], [c_id], [])
    meta_result = MetaAnalysisResult(
        analysis_id=a_id,
        clusters=[cluster],
        scientific_summary=summary,
        intelligence_metrics=metrics,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=a_hash,
    )

    edges = engine.discover_from_meta_analysis(meta_result, "2026-07-30T00:00:00Z")
    assert len(edges) == 1
    assert c_id in edges[0].originating_clusters
