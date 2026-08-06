"""
Project GOAT v0.7 — Test Suite for Meta-Analysis Reports

Coverage:
- MetaAnalysisReport (Markdown & JSON)
- ResearchClusterReport (Markdown & JSON)
- ResearchPatternReport (Markdown & JSON)
- ResearchTrendReport (Markdown & JSON)
- ScientificSummaryReport (Markdown & JSON)
"""

from goat.meta_analysis.core.canonical import (
    compute_cluster_id,
    compute_meta_analysis_id,
    compute_metrics_id,
    compute_pattern_id,
    compute_summary_id,
    compute_trend_id,
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
from goat.meta_analysis.reporting.reports import (
    MetaAnalysisReport,
    ResearchClusterReport,
    ResearchPatternReport,
    ResearchTrendReport,
    ScientificSummaryReport,
)


def test_meta_analysis_report_rendering():
    s_id, s_hash = compute_summary_id(1, 1, "2026-07-30T00:00:00Z")
    summary = ScientificSummary(summary_id=s_id, creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=s_hash)

    m_id, m_hash = compute_metrics_id(0.5, 0.5, "2026-07-30T00:00:00Z")
    metrics = ResearchIntelligenceMetrics(metrics_id=m_id, timestamp="2026-07-30T00:00:00Z", canonical_hash=m_hash)

    a_id, a_hash = compute_meta_analysis_id(["K1"], ["C1"], ["P1"])
    result = MetaAnalysisResult(
        analysis_id=a_id,
        analyzed_knowledge_states=["K1"],
        scientific_summary=summary,
        intelligence_metrics=metrics,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=a_hash,
    )

    report = MetaAnalysisReport(
        report_id="REP_MAR_001",
        timestamp="2026-07-30T00:00:00Z",
        result=result,
    )

    md = report.to_markdown()
    assert "# Scientific Meta-Analysis Report" in md
    assert a_id in md

    json_str = report.to_json()
    assert '"report_id":"REP_MAR_001"' in json_str


def test_cluster_report_rendering():
    c_id, c_hash = compute_cluster_id("Title", ["N1"])
    cluster = ResearchCluster(
        cluster_id=c_id,
        title="Title",
        cluster_type=ClusterType.THEME,
        participating_nodes=["N1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    report = ResearchClusterReport(
        report_id="REP_CLR_001",
        timestamp="2026-07-30T00:00:00Z",
        clusters=[cluster],
    )

    md = report.to_markdown()
    assert "# Research Clusters Report" in md
    assert c_id in md


def test_pattern_report_rendering():
    p_id, p_hash = compute_pattern_id("Pattern Name", ["E1"])
    pattern = ResearchPattern(
        pattern_id=p_id,
        pattern_name="Pattern Name",
        category=PatternCategory.RECURRING_EVIDENCE,
        evidence=["E1"],
        canonical_hash=p_hash,
    )

    report = ResearchPatternReport(
        report_id="REP_PTR_001",
        timestamp="2026-07-30T00:00:00Z",
        patterns=[pattern],
    )

    md = report.to_markdown()
    assert "# Research Patterns Report" in md
    assert p_id in md


def test_trend_report_rendering():
    t_id, t_hash = compute_trend_id("Topic", "GROWING")
    trend = ResearchTrend(
        trend_id=t_id,
        topic="Topic",
        direction=TrendDirection.GROWING,
        canonical_hash=t_hash,
    )

    report = ResearchTrendReport(
        report_id="REP_TRD_001",
        timestamp="2026-07-30T00:00:00Z",
        trends=[trend],
    )

    md = report.to_markdown()
    assert "# Research Trends Report" in md
    assert t_id in md


def test_summary_report_rendering():
    s_id, s_hash = compute_summary_id(1, 1, "2026-07-30T00:00:00Z")
    summary = ScientificSummary(
        summary_id=s_id,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=s_hash,
    )

    report = ScientificSummaryReport(
        report_id="REP_SCS_001",
        timestamp="2026-07-30T00:00:00Z",
        summary=summary,
    )

    md = report.to_markdown()
    assert "# Executive Scientific Summary" in md
    assert s_id in md
