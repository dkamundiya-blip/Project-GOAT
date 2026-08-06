"""
Project GOAT v0.7 — Composite Edge Engine Package

Public API Exports for Step 6.2 (Phase VI).
"""

from goat.composite.conflicts import CompositeConflictEngine
from goat.composite.core import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
    ConflictSeverity,
    RankingStrategy,
    SynthesisMode,
    compute_composite_evidence_id,
    compute_composite_explanation_id,
    compute_composite_id,
    compute_composite_ranking_id,
    compute_composite_report_id,
    compute_composite_score_id,
    serialize_canonical_json,
)
from goat.composite.engine import CompositeEdgeEngineCoordinator
from goat.composite.persistence import (
    CompositeEvidenceRepository,
    CompositeRankingRepository,
    CompositeReportRepository,
    CompositeRepository,
    CompositeScoreRepository,
    init_composite_db,
)
from goat.composite.ranking import CompositeRankingEngine
from goat.composite.reporting import (
    CompositeAnalysisReport,
    CompositeEdgeReport,
    CompositeEvidenceReport,
    CompositeRankingReport,
    CompositeScoreReport,
)
from goat.composite.scoring import CompositeScoringEngine
from goat.composite.synthesis import CompositeEdgeSynthesisEngine

__all__ = [
    # Core Models & Enums
    "SynthesisMode",
    "ConflictSeverity",
    "RankingStrategy",
    "CompositeEdge",
    "CompositeEvidence",
    "CompositeScore",
    "CompositeRanking",
    "CompositeExplainabilityRecord",
    # Identifiers & Canonical Hashing
    "compute_composite_id",
    "compute_composite_evidence_id",
    "compute_composite_score_id",
    "compute_composite_ranking_id",
    "compute_composite_explanation_id",
    "compute_composite_report_id",
    "serialize_canonical_json",
    # Engines & Coordinators
    "CompositeEdgeEngineCoordinator",
    "CompositeEdgeSynthesisEngine",
    "CompositeConflictEngine",
    "CompositeScoringEngine",
    "CompositeRankingEngine",
    # Reports
    "CompositeEdgeReport",
    "CompositeEvidenceReport",
    "CompositeScoreReport",
    "CompositeRankingReport",
    "CompositeAnalysisReport",
    # Repositories & Database Initialization
    "init_composite_db",
    "CompositeRepository",
    "CompositeEvidenceRepository",
    "CompositeScoreRepository",
    "CompositeRankingRepository",
    "CompositeReportRepository",
]
