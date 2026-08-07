"""
Project GOAT Phase 6 — Edge Persistence Package (`goat.edge_discovery.persistence`)
"""

from goat.edge_discovery.persistence.in_memory import InMemoryEdgeRepository
from goat.edge_discovery.persistence.interfaces import IEdgeRepository
from goat.edge_discovery.persistence.sqlite import (
    SQLiteEdgeRepository,
    init_edge_discovery_db,
)

__all__ = [
    "IEdgeRepository",
    "InMemoryEdgeRepository",
    "init_edge_discovery_db",
    "SQLiteEdgeRepository",
]
