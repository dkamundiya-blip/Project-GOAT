"""
Project GOAT v0.9 — Quantitative Edge Discovery Engine Package
"""

from goat.edge_discovery.clustering.engine import PatternClusteringEngine
from goat.edge_discovery.core.canonical import (
    compute_canonical_sha256,
    compute_discovery_decision_id,
    compute_discovery_summary_id,
    compute_edge_candidate_id,
    compute_edge_pattern_id,
    compute_edge_score_id,
    compute_novelty_assessment_id,
    compute_pattern_cluster_id,
    serialize_canonical_json,
)
from goat.edge_discovery.core.enums import (
    EdgeCategory,
    NoveltyStatus,
    PatternType,
    QualityTier,
    RejectionReason,
    ValidationStatus,
)
from goat.edge_discovery.core.models import (
    DiscoveryDecision,
    DiscoverySummary,
    EdgeCandidate,
    EdgePattern,
    EdgeScore,
    NoveltyAssessment,
    PatternCluster,
)
from goat.edge_discovery.engine import MasterEdgeDiscoveryEngine
from goat.edge_discovery.mining.engine import PatternMiningEngine
from goat.edge_discovery.novelty.engine import NoveltyAssessmentEngine
from goat.edge_discovery.persistence.sqlite import (
    ClusterRepository,
    DecisionRepository,
    EdgeDiscoveryPersistenceContext,
    EdgeRepository,
    NoveltyRepository,
    PatternRepository,
    ScoreRepository,
    SummaryRepository,
    init_edge_discovery_db,
)
from goat.edge_discovery.reporting.reports import EdgeDiscoveryReportGenerator
from goat.edge_discovery.scoring.engine import EdgeScoringEngine
from goat.edge_discovery.validation.engine import DiscoveryValidationEngine

__all__ = [
    "ClusterRepository",
    "DecisionRepository",
    "DiscoveryDecision",
    "DiscoverySummary",
    "DiscoveryValidationEngine",
    "EdgeCandidate",
    "EdgeCategory",
    "EdgeDiscoveryPersistenceContext",
    "EdgeDiscoveryReportGenerator",
    "EdgePattern",
    "EdgeRepository",
    "EdgeScore",
    "EdgeScoringEngine",
    "MasterEdgeDiscoveryEngine",
    "NoveltyAssessment",
    "NoveltyAssessmentEngine",
    "NoveltyRepository",
    "NoveltyStatus",
    "PatternCluster",
    "PatternClusteringEngine",
    "PatternMiningEngine",
    "PatternRepository",
    "PatternType",
    "QualityTier",
    "RejectionReason",
    "ScoreRepository",
    "SummaryRepository",
    "ValidationStatus",
    "compute_canonical_sha256",
    "compute_discovery_decision_id",
    "compute_discovery_summary_id",
    "compute_edge_candidate_id",
    "compute_edge_pattern_id",
    "compute_edge_score_id",
    "compute_novelty_assessment_id",
    "compute_pattern_cluster_id",
    "init_edge_discovery_db",
    "serialize_canonical_json",
]
