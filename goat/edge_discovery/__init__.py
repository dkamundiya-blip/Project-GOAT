"""
Project GOAT Phase 6 — Edge Discovery Engine Package (`goat.edge_discovery`)

Quantitative research package providing hypothesis creation, candidate feature combination search,
16-metric historical evaluation, statistical significance testing (Bootstrap/Monte Carlo),
market regime validation, walk-forward OOS verification, edge persistence, composite ranking,
decay monitoring, and experiment dataset exports.
"""

from goat.edge_discovery.dataset import ResearchDatasetBuilder
from goat.edge_discovery.decay import EdgeDecayEngine
from goat.edge_discovery.engine import (
    EdgeDiscoveryEngine,
    MasterEdgeDiscoveryEngine,
)
from goat.edge_discovery.evaluator import HistoricalEvaluationEngine
from goat.edge_discovery.generator import FeatureCombinationGenerator
from goat.edge_discovery.hypothesis import HypothesisEngine
from goat.edge_discovery.models import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
    HypothesisCondition,
    HypothesisOperator,
    HypothesisPrediction,
    HypothesisStatus,
    ResearchDataset,
    ResearchHypothesis,
    compute_dataset_id,
    compute_edge_id,
    compute_hypothesis_id,
)
from goat.edge_discovery.persistence import (
    IEdgeRepository,
    InMemoryEdgeRepository,
    SQLiteEdgeRepository,
    init_edge_discovery_db,
)
from goat.edge_discovery.ranking import EdgeRankingEngine
from goat.edge_discovery.regime import MarketRegimeValidator
from goat.edge_discovery.significance import StatisticalSignificanceEngine
from goat.edge_discovery.walk_forward import WalkForwardValidator

__all__ = [
    # Master Engine
    "MasterEdgeDiscoveryEngine",
    "EdgeDiscoveryEngine",
    # Research Modules
    "HypothesisEngine",
    "FeatureCombinationGenerator",
    "HistoricalEvaluationEngine",
    "StatisticalSignificanceEngine",
    "MarketRegimeValidator",
    "WalkForwardValidator",
    "EdgeRankingEngine",
    "EdgeDecayEngine",
    "ResearchDatasetBuilder",
    # Domain Models
    "HypothesisOperator",
    "HypothesisStatus",
    "HypothesisCondition",
    "HypothesisPrediction",
    "ResearchHypothesis",
    "compute_hypothesis_id",
    "EdgeStatus",
    "EdgePerformanceMetrics",
    "DiscoveredEdge",
    "compute_edge_id",
    "ResearchDataset",
    "compute_dataset_id",
    # Persistence
    "IEdgeRepository",
    "InMemoryEdgeRepository",
    "init_edge_discovery_db",
    "SQLiteEdgeRepository",
]
