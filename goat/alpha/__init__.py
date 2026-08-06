"""
Project GOAT v0.7 — Scientific Alpha Engine Package

Public API Exports for Step 6.0 (Phase VI).
"""

from goat.alpha.core import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    EdgeMaturity,
    EdgeRanking,
    EdgeScore,
    EvidenceSourceType,
    RankingRuleType,
    ScientificEdge,
    compute_alpha_report_id,
    compute_edge_id,
    compute_evidence_id,
    compute_explanation_id,
    compute_ranking_id,
    compute_score_id,
    serialize_canonical_json,
)
from goat.alpha.discovery import EdgeDiscoveryEngine
from goat.alpha.engine import ScientificAlphaDiscoveryEngine
from goat.alpha.evidence import EdgeEvidenceAggregator
from goat.alpha.persistence import (
    EdgeEvidenceRepository,
    EdgeRankingRepository,
    EdgeReportRepository,
    EdgeScoreRepository,
    ScientificEdgeRepository,
    init_alpha_db,
)
from goat.alpha.ranking import EdgeRankingEngine
from goat.alpha.reporting import (
    EdgeEvidenceReport,
    EdgeQualityReport,
    EdgeRankingReport,
    ScientificAlphaReport,
    ScientificEdgeReport,
)
from goat.alpha.scoring import EdgeScoringEngine

__all__ = [
    # Core Models & Enums
    "EdgeMaturity",
    "EvidenceSourceType",
    "RankingRuleType",
    "ScientificEdge",
    "EdgeEvidence",
    "EdgeScore",
    "EdgeRanking",
    "EdgeExplainabilityRecord",
    # Identifiers & Canonical Hashing
    "compute_edge_id",
    "compute_evidence_id",
    "compute_score_id",
    "compute_ranking_id",
    "compute_explanation_id",
    "compute_alpha_report_id",
    "serialize_canonical_json",
    # Alpha Engines & Coordinators
    "ScientificAlphaDiscoveryEngine",
    "EdgeDiscoveryEngine",
    "EdgeScoringEngine",
    "EdgeEvidenceAggregator",
    "EdgeRankingEngine",
    # Reports
    "ScientificEdgeReport",
    "EdgeRankingReport",
    "EdgeEvidenceReport",
    "EdgeQualityReport",
    "ScientificAlphaReport",
    # Repositories & Database Initialization
    "init_alpha_db",
    "ScientificEdgeRepository",
    "EdgeEvidenceRepository",
    "EdgeScoreRepository",
    "EdgeRankingRepository",
    "EdgeReportRepository",
]
