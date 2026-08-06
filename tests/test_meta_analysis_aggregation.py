"""
Project GOAT v0.7 — Test Suite for Aggregation Engines (Trends, Intelligence Metrics, Summary)

Coverage:
- TrendAnalysisEngine (GROWING, DECLINING, STABLE, CONFLICTING, UNRESOLVED, DORMANT trends)
- ResearchIntelligenceEngine (Metrics calculation & score bounds)
- ScientificSummaryEngine (Summary generation & recommendations)
"""

from goat.integration.core.canonical import compute_integrated_knowledge_id
from goat.integration.core.models import IntegratedKnowledge
from goat.meta_analysis.aggregation.intelligence import ResearchIntelligenceEngine
from goat.meta_analysis.aggregation.summary import ScientificSummaryEngine
from goat.meta_analysis.aggregation.trends import TrendAnalysisEngine
from goat.meta_analysis.core.enums import TrendDirection


def test_trend_analysis_engine():
    engine = TrendAnalysisEngine()

    vals = [
        {"validation_id": "VAL_1", "hypothesis_id": "HYP_MOM", "status": "PASSED", "confidence": 0.85},
        {"validation_id": "VAL_2", "hypothesis_id": "HYP_MOM", "status": "PASSED", "confidence": 0.90},
        {"validation_id": "VAL_3", "hypothesis_id": "HYP_MOM", "status": "PASSED", "confidence": 0.95},
    ]

    trends = engine.analyze_trends(vals, [], "2026-07-30T00:00:00Z")
    assert len(trends) == 1
    assert trends[0].direction == TrendDirection.GROWING
    assert trends[0].topic == "HYP_MOM"


def test_research_intelligence_engine():
    engine = ResearchIntelligenceEngine()

    ik_id, ik_hash = compute_integrated_knowledge_id(["V1"], ["H1"], ["E1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["V1"],
        participating_hypotheses=["H1"],
        participating_experiments=["E1"],
        overall_confidence=0.88,
        consensus_strength=0.90,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )

    vals = [{"validation_id": "V1", "status": "PASSED", "hypothesis_id": "H1"}]
    metrics = engine.compute_metrics(None, [ik], vals, [], "2026-07-30T00:00:00Z")

    assert metrics.metrics_id.startswith("RIM_")
    assert 0.0 <= metrics.knowledge_maturity <= 1.0
    assert 0.0 <= metrics.scientific_confidence <= 1.0


def test_scientific_summary_engine():
    engine = ScientificSummaryEngine()

    ik_id, ik_hash = compute_integrated_knowledge_id(["V1"], ["H1"], ["E1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["V1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )

    summary = engine.generate_summary([ik], [], [], [], [], "2026-07-30T00:00:00Z")

    assert summary.summary_id.startswith("SCS_")
    assert summary.validated_knowledge_count == 1
    assert len(summary.future_investigation_recommendations) >= 1
