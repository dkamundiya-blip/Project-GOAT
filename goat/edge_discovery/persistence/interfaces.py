"""
Project GOAT Phase 6 — Edge Repository Interface

Defines the IEdgeRepository abstract interface for Edge Repository persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from goat.edge_discovery.models.edge import DiscoveredEdge, EdgeStatus


class IEdgeRepository(ABC):
    """Repository interface for Edge Store persistence."""

    @abstractmethod
    def save_edge(self, edge: DiscoveredEdge) -> None:
        """Persist a single validated edge."""
        pass

    @abstractmethod
    def save_edges(self, edges: Sequence[DiscoveredEdge]) -> None:
        """Persist a batch of validated edges."""
        pass

    @abstractmethod
    def get_edge(self, edge_id: str) -> DiscoveredEdge | None:
        """Fetch a specific edge by ID."""
        pass

    @abstractmethod
    def get_recent_edges(
        self,
        symbol: str | None = None,
        status: EdgeStatus | None = None,
        limit: int = 100,
    ) -> list[DiscoveredEdge]:
        """Query recent edges filtered by optional symbol and status."""
        pass

    @abstractmethod
    def get_top_edges(self, limit: int = 50) -> list[DiscoveredEdge]:
        """Query top edges ordered descending by composite score."""
        pass

    @abstractmethod
    def update_edge_status(self, edge_id: str, status: EdgeStatus) -> None:
        """Update the status of an existing edge."""
        pass

    @abstractmethod
    def count(self, status: EdgeStatus | None = None) -> int:
        """Count persisted edges."""
        pass
