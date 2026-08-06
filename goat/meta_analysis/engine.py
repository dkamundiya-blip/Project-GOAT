"""
Project GOAT v0.7 — Scientific Meta-Analysis & Research Intelligence Engine

Main coordinator executing deterministic meta-analysis workflows across accumulated research:
1. Load integrated knowledge & scientific knowledge graph
2. Generate research clusters (ClusterEngine)
3. Discover research patterns (PatternDiscoveryEngine)
4. Analyze research trends (TrendAnalysisEngine)
5. Compute intelligence metrics (ResearchIntelligenceEngine)
6. Generate executive summary (ScientificSummaryEngine)
7. Produce root MetaAnalysisResult
8. Persist state to SQLite repositories
9. Generate reports
10. Replay past meta-analysis executions
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.integration.core.models import IntegratedKnowledge, KnowledgeNode
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.meta_analysis.aggregation.intelligence import ResearchIntelligenceEngine
from goat.meta_analysis.aggregation.summary import ScientificSummaryEngine
from goat.meta_analysis.aggregation.trends import TrendAnalysisEngine
from goat.meta_analysis.clustering.engine import ClusterEngine
from goat.meta_analysis.core.canonical import compute_canonical_sha256, compute_meta_analysis_id
from goat.meta_analysis.core.models import MetaAnalysisResult
from goat.meta_analysis.persistence.sqlite import (
    ClusterRepository,
    MetaAnalysisRepository,
    PatternRepository,
    ReportRepository,
    SummaryRepository,
    TrendRepository,
)

from goat.meta_analysis.patterns.discovery import PatternDiscoveryEngine
from goat.meta_analysis.reporting.reports import (
    MetaAnalysisReport,
    ResearchClusterReport,
    ResearchPatternReport,
    ResearchTrendReport,
    ScientificSummaryReport,
)


class ScientificMetaAnalysisEngine:
    """Deterministic Scientific Meta-Analysis & Research Intelligence Engine."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.cluster_engine = ClusterEngine()
        self.pattern_engine = PatternDiscoveryEngine()
        self.trend_engine = TrendAnalysisEngine()
        self.intelligence_engine = ResearchIntelligenceEngine()
        self.summary_engine = ScientificSummaryEngine()

        # Repositories
        self.cluster_repo = ClusterRepository(self.conn)
        self.pattern_repo = PatternRepository(self.conn)
        self.trend_repo = TrendRepository(self.conn)
        self.summary_repo = SummaryRepository(self.conn)
        self.analysis_repo = MetaAnalysisRepository(self.conn)
        self.report_repo = ReportRepository(self.conn)

    def run_meta_analysis(
        self,
        integrated_knowledge_list: list[IntegratedKnowledge],
        graph: ScientificKnowledgeGraph | None,
        validations: list[dict[str, Any]],
        conflicts: list[dict[str, Any]],
        timestamp: str,
    ) -> tuple[MetaAnalysisResult, MetaAnalysisReport]:
        """Execute a full scientific meta-analysis over accumulated research.

        Args:
            integrated_knowledge_list: List of IntegratedKnowledge objects.
            graph: Optional ScientificKnowledgeGraph object.
            validations: List of validation run summary dicts.
            conflicts: List of conflict records or dicts.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (MetaAnalysisResult, MetaAnalysisReport).
        """
        nodes = graph.get_nodes() if graph else []

        # 1. Cluster Generation
        clusters = self.cluster_engine.generate_all_clusters(
            nodes=nodes,
            validations=validations,
            graph=graph,
            timestamp=timestamp,
        )
        for c in clusters:
            self.cluster_repo.save_cluster(c)

        # 2. Pattern Discovery
        patterns = self.pattern_engine.discover_all_patterns(
            validations=validations,
            clusters=clusters,
            timestamp=timestamp,
        )
        for p in patterns:
            self.pattern_repo.save_pattern(p)

        # 3. Trend Analysis
        trends = self.trend_engine.analyze_trends(
            validations=validations,
            conflicts=conflicts,
            timestamp=timestamp,
        )
        for t in trends:
            self.trend_repo.save_trend(t)

        # 4. Research Intelligence Metrics
        metrics = self.intelligence_engine.compute_metrics(
            graph=graph,
            integrated_knowledge_list=integrated_knowledge_list,
            validations=validations,
            conflicts=conflicts,
            timestamp=timestamp,
        )

        # 5. Scientific Executive Summary
        summary = self.summary_engine.generate_summary(
            integrated_knowledge_list=integrated_knowledge_list,
            clusters=clusters,
            patterns=patterns,
            trends=trends,
            conflicts=conflicts,
            timestamp=timestamp,
        )
        self.summary_repo.save_summary(summary)

        # 6. Build Root MetaAnalysisResult Model
        ik_ids = sorted([ik.knowledge_id for ik in integrated_knowledge_list])
        c_ids = sorted([c.cluster_id for c in clusters])
        p_ids = sorted([p.pattern_id for p in patterns])

        analysis_id, _ = compute_meta_analysis_id(ik_ids, c_ids, p_ids)

        overall_conf = metrics.scientific_confidence
        overall_repr = metrics.validation_stability

        payload = {
            "analysis_id": analysis_id,
            "cluster_ids": c_ids,
            "pattern_ids": p_ids,
            "timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        result = MetaAnalysisResult(
            analysis_id=analysis_id,
            analyzed_knowledge_states=ik_ids,
            clusters=clusters,
            patterns=patterns,
            trends=trends,
            contradictions=conflicts,
            scientific_summary=summary,
            intelligence_metrics=metrics,
            confidence=overall_conf,
            reproducibility=overall_repr,
            timestamp=timestamp,
            canonical_hash=canonical_hash,
        )
        self.analysis_repo.save_result(result)

        # 7. Generate MetaAnalysisReport
        rep_id = f"REP_MAR_{analysis_id[4:12]}"
        report = MetaAnalysisReport(
            report_id=rep_id,
            timestamp=timestamp,
            result=result,
        )
        self.report_repo.save_report(rep_id, "MetaAnalysisReport", timestamp, report)

        return result, report

    def generate_sub_reports(
        self,
        result: MetaAnalysisResult,
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate structured sub-reports (Cluster, Pattern, Trend, Summary) for a meta-analysis result.

        Returns:
            Dict containing sub-reports.
        """
        cluster_report = ResearchClusterReport(
            report_id=f"REP_CLR_{result.analysis_id[4:12]}",
            timestamp=timestamp,
            clusters=result.clusters,
        )
        pattern_report = ResearchPatternReport(
            report_id=f"REP_PTR_{result.analysis_id[4:12]}",
            timestamp=timestamp,
            patterns=result.patterns,
        )
        trend_report = ResearchTrendReport(
            report_id=f"REP_TRD_{result.analysis_id[4:12]}",
            timestamp=timestamp,
            trends=result.trends,
        )
        summary_report = ScientificSummaryReport(
            report_id=f"REP_SCS_{result.analysis_id[4:12]}",
            timestamp=timestamp,
            summary=result.scientific_summary,
        )

        return {
            "cluster_report": cluster_report,
            "pattern_report": pattern_report,
            "trend_report": trend_report,
            "summary_report": summary_report,
        }

    def replay_analysis(self, analysis_id: str) -> MetaAnalysisResult:
        """Replay exact meta-analysis result from SQLite repository."""
        res = self.analysis_repo.get_result(analysis_id)
        if not res:
            raise KeyError(f"Meta-analysis ID '{analysis_id}' not found in persistence repository.")
        return res
