"""
Project GOAT v0.7 — Test Suite for Composite Reports

Coverage:
- CompositeEdgeReport (Markdown & JSON)
- CompositeEvidenceReport (Markdown & JSON)
- CompositeScoreReport (Markdown & JSON)
- CompositeRankingReport (Markdown & JSON)
- CompositeAnalysisReport (Markdown & JSON)
"""

from goat.composite.core.canonical import (
    compute_composite_evidence_id,
    compute_composite_explanation_id,
    compute_composite_id,
    compute_composite_ranking_id,
    compute_composite_score_id,
)
from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
)
from goat.composite.reporting.reports import (
    CompositeAnalysisReport,
    CompositeEdgeReport,
    CompositeEvidenceReport,
    CompositeRankingReport,
    CompositeScoreReport,
)


def test_composite_edge_report_rendering():
    c_id, c_hash = compute_composite_id(["SED_1"], "Composite Alpha")
    composite = CompositeEdge(
        composite_id=c_id,
        title="Composite Alpha",
        participating_edges=["SED_1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    report = CompositeEdgeReport(
        report_id="CAR_CMP_001",
        timestamp="2026-07-30T00:00:00Z",
        composites=[composite],
    )

    md = report.to_markdown()
    assert "# Composite Candidate Edge Report" in md
    assert c_id in md

    json_str = report.to_json()
    assert '"report_id":"CAR_CMP_001"' in json_str


def test_composite_ranking_report_rendering():
    rk_id, rk_hash = compute_composite_ranking_id(["CMP_1"], "2026-07-30T00:00:00Z")
    sc_id, sc_hash = compute_composite_score_id("CMP_1", 0.90, "2026-07-30T00:00:00Z")
    score = CompositeScore(score_id=sc_id, composite_id="CMP_1", overall_score=0.90, timestamp="2026-07-30T00:00:00Z", canonical_hash=sc_hash)

    ranking = CompositeRanking(
        ranking_id=rk_id,
        ranked_composites=["CMP_1"],
        composite_scores=[score],
        ranking_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=rk_hash,
    )

    report = CompositeRankingReport(
        report_id="CAR_RNK_001",
        timestamp="2026-07-30T00:00:00Z",
        ranking=ranking,
    )

    md = report.to_markdown()
    assert "# Composite Ranking Report" in md
    assert rk_id in md


def test_composite_analysis_report_rendering():
    report = CompositeAnalysisReport(
        report_id="CAR_001",
        timestamp="2026-07-30T00:00:00Z",
        total_active_edges_input=4,
        total_composites_synthesized=3,
        top_ranked_composite_id="CMP_1",
        top_composite_score=0.92,
    )

    md = report.to_markdown()
    assert "# Composite Edge Synthesis Executive Report" in md
    assert "CMP_1" in md
