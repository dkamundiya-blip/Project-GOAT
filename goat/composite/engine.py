"""
Project GOAT v0.7 — Composite Edge Engine Coordinator

Main coordinator executing the composite edge synthesis, conflict analysis, scoring, and ranking workflow:
1. Synthesize candidate CompositeEdges from active ScientificEdges (CompositeEdgeSynthesisEngine)
2. Evaluate conflicts between participating edges (CompositeConflictEngine)
3. Calculate multi-dimensional quality & synergy scores (CompositeScoringEngine)
4. Rank CompositeEdges deterministically (CompositeRankingEngine)
5. Persist models to SQLite repositories
6. Generate reports
7. Replay past composite synthesis and ranking decisions
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.alpha.core.models import ScientificEdge
from goat.composite.conflicts.engine import CompositeConflictEngine
from goat.composite.core.canonical import compute_composite_report_id
from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
)
from goat.composite.persistence.sqlite import (
    CompositeEvidenceRepository,
    CompositeRankingRepository,
    CompositeReportRepository,
    CompositeRepository,
    CompositeScoreRepository,
)
from goat.composite.ranking.engine import CompositeRankingEngine
from goat.composite.reporting.reports import (
    CompositeAnalysisReport,
    CompositeEdgeReport,
    CompositeEvidenceReport,
    CompositeRankingReport,
    CompositeScoreReport,
)
from goat.composite.scoring.engine import CompositeScoringEngine
from goat.composite.synthesis.engine import CompositeEdgeSynthesisEngine


class CompositeEdgeEngineCoordinator:
    """Main coordinator executing deterministic composite edge synthesis & portfolio intelligence workflow."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.conflict_engine = CompositeConflictEngine()
        self.synthesis_engine = CompositeEdgeSynthesisEngine(conflict_engine=self.conflict_engine)
        self.scoring_engine = CompositeScoringEngine()
        self.ranking_engine = CompositeRankingEngine()

        # Repositories
        self.composite_repo = CompositeRepository(self.conn)
        self.evidence_repo = CompositeEvidenceRepository(self.conn)
        self.score_repo = CompositeScoreRepository(self.conn)
        self.ranking_repo = CompositeRankingRepository(self.conn)
        self.report_repo = CompositeReportRepository(self.conn)

    def execute_composite_synthesis_workflow(
        self,
        active_edges: list[ScientificEdge],
        timestamp: str,
    ) -> tuple[CompositeRanking, CompositeAnalysisReport]:
        """Execute complete synthesis, scoring, and ranking workflow deterministically.

        Args:
            active_edges: List of active ScientificEdge models.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (CompositeRanking, CompositeAnalysisReport).
        """
        edge_map = {e.edge_id: e for e in active_edges}

        # 1. Synthesize CompositeEdges
        composites, evidence_records, explainability_records, conflict_map = self.synthesis_engine.synthesize_composites(
            active_edges=active_edges,
            timestamp=timestamp,
        )

        for c in composites:
            self.composite_repo.save_composite(c)

        for ev in evidence_records:
            self.evidence_repo.save_evidence(ev)

        for exp in explainability_records:
            self.evidence_repo.save_explanation(exp)

        # 2. Score CompositeEdges
        scores = self.scoring_engine.score_all_composites(
            composites=composites,
            edge_map=edge_map,
            conflict_map=conflict_map,
            timestamp=timestamp,
        )

        for s in scores:
            self.score_repo.save_score(s)

        # 3. Rank CompositeEdges
        ranking = self.ranking_engine.rank_composites(
            composites=composites,
            scores=scores,
            timestamp=timestamp,
        )
        self.ranking_repo.save_ranking(ranking)

        # 4. Generate Executive CompositeAnalysisReport
        top_composite_id = ranking.ranked_composites[0] if ranking.ranked_composites else ""
        score_map = {s.composite_id: s.overall_score for s in scores}
        top_score = score_map.get(top_composite_id, 0.0)

        rep_id, _ = compute_composite_report_id("CompositeAnalysisReport", timestamp)

        report = CompositeAnalysisReport(
            report_id=rep_id,
            timestamp=timestamp,
            total_active_edges_input=len(active_edges),
            total_composites_synthesized=len(composites),
            top_ranked_composite_id=top_composite_id,
            top_composite_score=top_score,
            summary_notes=f"Synthesized {len(composites)} composite edges from {len(active_edges)} active input edges deterministically.",
        )
        self.report_repo.save_report(rep_id, "CompositeAnalysisReport", timestamp, report)

        return ranking, report

    def generate_sub_reports(
        self,
        composites: list[CompositeEdge],
        ranking: CompositeRanking,
        evidence_records: list[CompositeEvidence],
        explainability_records: list[CompositeExplainabilityRecord],
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate sub-reports (EdgeReport, EvidenceReport, ScoreReport, RankingReport)."""
        edge_report = CompositeEdgeReport(
            report_id=f"CAR_CMP_{timestamp[:10]}",
            timestamp=timestamp,
            composites=composites,
        )
        evidence_report = CompositeEvidenceReport(
            report_id=f"CAR_EVI_{timestamp[:10]}",
            timestamp=timestamp,
            evidence_records=evidence_records,
            explainability_records=explainability_records,
        )
        score_report = CompositeScoreReport(
            report_id=f"CAR_SCR_{timestamp[:10]}",
            timestamp=timestamp,
            scores=ranking.composite_scores,
        )
        ranking_report = CompositeRankingReport(
            report_id=f"CAR_RNK_{timestamp[:10]}",
            timestamp=timestamp,
            ranking=ranking,
        )

        return {
            "edge_report": edge_report,
            "evidence_report": evidence_report,
            "score_report": score_report,
            "ranking_report": ranking_report,
        }

    def replay_ranking(self, ranking_id: str) -> CompositeRanking:
        """Replay exact CompositeRanking model from persistence repository."""
        rk = self.ranking_repo.get_ranking(ranking_id)
        if not rk:
            raise KeyError(f"Ranking ID '{ranking_id}' not found in persistence repository.")
        return rk

    def replay_composite(self, composite_id: str) -> CompositeEdge:
        """Replay exact CompositeEdge model from persistence repository."""
        cmp = self.composite_repo.get_composite(composite_id)
        if not cmp:
            raise KeyError(f"Composite ID '{composite_id}' not found in persistence repository.")
        return cmp
