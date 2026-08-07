"""
Project GOAT Phase 6 — Edge Discovery Models Package
"""

from goat.edge_discovery.models.dataset import ResearchDataset, compute_dataset_id
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
    compute_edge_id,
)
from goat.edge_discovery.models.hypothesis import (
    HypothesisCondition,
    HypothesisOperator,
    HypothesisPrediction,
    HypothesisStatus,
    ResearchHypothesis,
    compute_hypothesis_id,
)

__all__ = [
    # Hypotheses
    "HypothesisOperator",
    "HypothesisStatus",
    "HypothesisCondition",
    "HypothesisPrediction",
    "ResearchHypothesis",
    "compute_hypothesis_id",
    # Edges
    "EdgeStatus",
    "EdgePerformanceMetrics",
    "DiscoveredEdge",
    "compute_edge_id",
    # Research Datasets
    "ResearchDataset",
    "compute_dataset_id",
]
