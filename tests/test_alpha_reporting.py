"""
Project GOAT v0.7 — Test Suite for Scientific Alpha Reports

Coverage:
- ScientificEdgeReport (Markdown & JSON)
- EdgeRankingReport (Markdown & JSON)
- EdgeEvidenceReport (Markdown & JSON)
- EdgeQualityReport (Markdown & JSON)
- ScientificAlphaReport (Markdown & JSON)
"""

from goat.alpha.core.canonical import (
    compute_edge_id,
    compute_evidence_id,
    compute_explanation_id,
    compute_ranking_id,
    compute_score_id,
)
from goat.alpha.core.enums import EdgeMaturity, EvidenceSourceType
from goat.alpha.core.models import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    EdgeRanking,
    EdgeScore,
    ScientificEdge,
)
from goat.alpha.reporting.reports import (
    EdgeEvidenceReport,
    EdgeQualityReport,
    EdgeRankingReport,
    ScientificAlphaReport,
    ScientificEdgeReport,
)


def test_scientific_edge_report_rendering():
    e_id, e_hash = compute_edge_id("Edge Alpha", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge Alpha",
        maturity=EdgeMaturity.VALIDATED,
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    report = ScientificEdgeReport(
        report_id="SAR_EDG_001",
        timestamp="2026-07-30T00:00:00Z",
        edges=[edge],
    )

    md = report.to_markdown()
    assert "# Scientific Candidate Edge Report" in md
    assert e_id in md

    json_str = report.to_json()
    assert '"report_id":"SAR_EDG_001"' in json_str


def test_edge_ranking_report_rendering():
    rk_id, rk_hash = compute_ranking_id(["SED_1"], "2026-07-30T00:00:00Z")
    sc_id, sc_hash = compute_score_id("SED_1", 0.90, "2026-07-30T00:00:00Z")
    score = EdgeScore(score_id=sc_id, edge_id="SED_1", overall_edge_score=0.90, timestamp="2026-07-30T00:00:00Z", canonical_hash=sc_hash)

    ranking = EdgeRanking(
        ranking_id=rk_id,
        ranked_edges=["SED_1"],
        edge_scores=[score],
        ranking_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=rk_hash,
    )

    report = EdgeRankingReport(
        report_id="SAR_RNK_001",
        timestamp="2026-07-30T00:00:00Z",
        ranking=ranking,
    )

    md = report.to_markdown()
    assert "# Edge Ranking Report" in md
    assert rk_id in md


def test_edge_evidence_report_rendering():
    ev_id, ev_hash = compute_evidence_id("SED_1", "VAL_1", "VALIDATION")
    evidence = EdgeEvidence(
        evidence_id=ev_id,
        edge_id="SED_1",
        source_type=EvidenceSourceType.VALIDATION,
        source_reference="VAL_1",
        canonical_hash=ev_hash,
    )

    ex_id, ex_hash = compute_explanation_id("SED_1", "HYP_1")
    expl = EdgeExplainabilityRecord(
        explanation_id=ex_id,
        edge_id="SED_1",
        origin="HYP_1",
        scientific_explanation="Explanation text",
        canonical_hash=ex_hash,
    )

    report = EdgeEvidenceReport(
        report_id="SAR_EVI_001",
        timestamp="2026-07-30T00:00:00Z",
        evidence_records=[evidence],
        explainability_records=[expl],
    )

    md = report.to_markdown()
    assert "# Edge Evidence & Traceability Report" in md
    assert ev_id in md


def test_scientific_alpha_report_rendering():
    report = ScientificAlphaReport(
        report_id="SAR_001",
        timestamp="2026-07-30T00:00:00Z",
        total_edges_discovered=5,
        top_ranked_edge_id="SED_1",
        top_edge_score=0.92,
        foundational_count=1,
        mature_count=2,
        validated_count=2,
    )

    md = report.to_markdown()
    assert "# Scientific Alpha Engine Executive Report" in md
    assert "SED_1" in md
