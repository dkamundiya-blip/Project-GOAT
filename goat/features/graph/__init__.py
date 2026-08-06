"""
Project GOAT v0.7 — Feature Dependency Graph Package

Exposes GraphNode, GraphEdge, FeatureDependencyGraph, CircularDependencyError, and GraphValidationError.
"""

from goat.features.graph.dag import (
    CircularDependencyError,
    FeatureDependencyGraph,
    GraphValidationError,
)
from goat.features.graph.edge import GraphEdge, compute_edge_id
from goat.features.graph.node import GraphNode, compute_node_id

__all__ = [
    "GraphNode",
    "GraphEdge",
    "compute_node_id",
    "compute_edge_id",
    "FeatureDependencyGraph",
    "CircularDependencyError",
    "GraphValidationError",
]
