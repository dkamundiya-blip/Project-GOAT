"""
Project GOAT v0.7 — Scientific Alpha Discovery Engine

Main coordinator executing the discovery, scoring, explainability, and ranking of candidate quantitative market edges:
1. Load validated knowledge, integrated knowledge, and meta-analysis results
2. Discover candidate ScientificEdges (EdgeDiscoveryEngine)
3. Calculate multi-dimensional quality scores (EdgeScoringEngine)
4. Extract supporting evidence & build explainability records (EdgeEvidenceAggregator)
5. Rank candidate edges deterministically (EdgeRankingEngine)
6. Persist models to SQLite repositories
7. Generate reports
8. Replay past edge discovery & ranking results
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.alpha.core.canonical import compute_alpha_report_id, compute_canonical_sha256
from goat.alpha.core.models import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    EdgeRanking,
    EdgeScore,
    ScientificEdge,
)

from goat.alpha.discovery.engine import EdgeDiscoveryEngine
from goat.alpha.evidence.aggregator import EdgeEvidenceAggregator
from goat.alpha.persistence.sqlite import (
    EdgeEvidenceRepository,
    EdgeRankingRepository,
    EdgeReportRepository,
    EdgeScoreRepository,
    ScientificEdgeRepository,
)
from goat.alpha.ranking.engine import EdgeRankingEngine
from goat.alpha.reporting.reports import (
    EdgeEvidenceReport,
    EdgeQualityReport,
    EdgeRankingReport,
    ScientificAlphaReport,
    ScientificEdgeReport,
)
from goat.alpha.scoring.engine import EdgeScoringEngine
from goat.integration.core.models import IntegratedKnowledge
from goat.meta_analysis.core.models import MetaAnalysisResult


class ScientificAlphaDiscoveryEngine:
    """Deterministic Scientific Alpha & Quantitative Edge Discovery Engine."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.discovery_engine = EdgeDiscoveryEngine()
        self.scoring_engine = EdgeScoringEngine()
        self.evidence_aggregator = EdgeEvidenceAggregator()
        self.ranking_engine = EdgeRankingEngine()

        # Repositories
        self.edge_repo = ScientificEdgeRepository(self.conn)
        self.evidence_repo = EdgeEvidenceRepository(self.conn)
        self.score_repo = EdgeScoreRepository(self.conn)
        self.ranking_repo = EdgeRankingRepository(self.conn)
        self.report_repo = EdgeReportRepository(self.conn)

    def execute_alpha_discovery(
        self,
        validations: list[dict[str, Any]],
        integrated_knowledge_list: list[IntegratedKnowledge],
        meta_result: MetaAnalysisResult | None,
        conflicts: list[dict[str, Any]],
        timestamp: str,
    ) -> tuple[EdgeRanking, ScientificAlphaReport]:
        """Execute complete quantitative edge discovery, scoring, and ranking workflow deterministically.

        Args:
            validations: List of validation run summary dicts.
            integrated_knowledge_list: List of IntegratedKnowledge models.
            meta_result: Optional MetaAnalysisResult model.
            conflicts: List of conflict records or dicts.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (EdgeRanking, ScientificAlphaReport).
        """
        # 1. Discover Candidate ScientificEdges
        edges = self.discovery_engine.discover_all_candidate_edges(
            validations=validations,
            integrated_knowledge_list=integrated_knowledge_list,
            meta_result=meta_result,
            timestamp=timestamp,
        )
        for e in edges:
            self.edge_repo.save_edge(e)

        # 2. Score Candidate Edges
        scores = self.scoring_engine.score_all_edges(
            edges=edges,
            conflicts=conflicts,
            timestamp=timestamp,
        )
        for s in scores:
            self.score_repo.save_score(s)

        # 3. Extract Evidence & Build Explainability Records
        all_evidence: list[EdgeEvidence] = []
        all_explanations: list[EdgeExplainabilityRecord] = []

        for e in edges:
            ev_list = self.evidence_aggregator.aggregate_evidence(e, validations)
            all_evidence.extend(ev_list)
            for ev in ev_list:
                self.evidence_repo.save_evidence(ev)

            expl_rec = self.evidence_aggregator.build_explainability_record(e, ev_list)
            all_explanations.append(expl_rec)
            self.evidence_repo.save_explanation(expl_rec)

        # 4. Rank Candidate Edges
        ranking = self.ranking_engine.rank_edges(
            edges=edges,
            scores=scores,
            timestamp=timestamp,
        )
        self.ranking_repo.save_ranking(ranking)

        # 5. Generate Executive ScientificAlphaReport
        top_edge_id = ranking.ranked_edges[0] if ranking.ranked_edges else ""
        score_map = {s.edge_id: s.overall_edge_score for s in scores}
        top_score = score_map.get(top_edge_id, 0.0)

        foundational_count = sum(1 for e in edges if e.maturity.value == "FOUNDATIONAL" or e.maturity == "FOUNDATIONAL")
        mature_count = sum(1 for e in edges if e.maturity.value == "MATURE" or e.maturity == "MATURE")
        validated_count = sum(1 for e in edges if e.maturity.value == "VALIDATED" or e.maturity == "VALIDATED")

        rep_id, _ = compute_alpha_report_id("ScientificAlphaReport", timestamp)
        report = ScientificAlphaReport(
            report_id=rep_id,
            timestamp=timestamp,
            total_edges_discovered=len(edges),
            top_ranked_edge_id=top_edge_id,
            top_edge_score=top_score,
            foundational_count=foundational_count,
            mature_count=mature_count,
            validated_count=validated_count,
            summary_notes=f"Discovered and ranked {len(edges)} quantitative market edges deterministically.",
        )
        self.report_repo.save_report(rep_id, "ScientificAlphaReport", timestamp, report)

        return ranking, report

    def generate_sub_reports(
        self,
        edges: list[ScientificEdge],
        ranking: EdgeRanking,
        evidence_records: list[EdgeEvidence],
        explainability_records: list[EdgeExplainabilityRecord],
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate sub-reports (EdgeReport, RankingReport, EvidenceReport, QualityReport)."""
        edge_report = ScientificEdgeReport(
            report_id=f"SAR_EDG_{timestamp[:10]}",
            timestamp=timestamp,
            edges=edges,
        )
        ranking_report = EdgeRankingReport(
            report_id=f"SAR_RNK_{timestamp[:10]}",
            timestamp=timestamp,
            ranking=ranking,
        )
        evidence_report = EdgeEvidenceReport(
            report_id=f"SAR_EVI_{timestamp[:10]}",
            timestamp=timestamp,
            evidence_records=evidence_records,
            explainability_records=explainability_records,
        )
        quality_report = EdgeQualityReport(
            report_id=f"SAR_QLT_{timestamp[:10]}",
            timestamp=timestamp,
            scores=ranking.edge_scores,
        )

        return {
            "edge_report": edge_report,
            "ranking_report": ranking_report,
            "evidence_report": evidence_report,
            "quality_report": quality_report,
        }

    def replay_ranking(self, ranking_id: str) -> EdgeRanking:
        """Replay exact EdgeRanking model from persistence repository."""
        rk = self.ranking_repo.get_ranking(ranking_id)
        if not rk:
            raise KeyError(f"Ranking ID '{ranking_id}' not found in persistence repository.")
        return rk
