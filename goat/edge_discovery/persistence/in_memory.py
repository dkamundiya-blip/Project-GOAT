"""
Project GOAT Phase 6 — In-Memory Edge Repository Implementation

Provides a thread-safe in-memory store for validated market edges.
"""

from __future__ import annotations

import threading
from typing import Sequence

from goat.edge_discovery.models.edge import DiscoveredEdge, EdgeStatus
from goat.edge_discovery.persistence.interfaces import IEdgeRepository


class InMemoryEdgeRepository(IEdgeRepository):
    """Thread-safe in-memory store for DiscoveredEdge instances."""

    def __init__(self):
        self._edges: dict[str, DiscoveredEdge] = {}
        self._lock = threading.RLock()

    def save_edge(self, edge: DiscoveredEdge) -> None:
        with self._lock:
            self._edges[edge.edge_id] = edge

    def save_edges(self, edges: Sequence[DiscoveredEdge]) -> None:
        with self._lock:
            for e in edges:
                self._edges[e.edge_id] = e

    def get_edge(self, edge_id: str) -> DiscoveredEdge | None:
        with self._lock:
            return self._edges.get(edge_id)

    def get_recent_edges(
        self,
        symbol: str | None = None,
        status: EdgeStatus | None = None,
        limit: int = 100,
    ) -> list[DiscoveredEdge]:
        with self._lock:
            res = list(self._edges.values())
            if symbol:
                res = [e for e in res if symbol.upper() in [s.upper() for s in e.supported_symbols]]
            if status:
                res = [e for e in res if e.status == status]
            res.sort(key=lambda x: x.discovery_date, reverse=True)
            return res[:limit]

    def get_top_edges(self, limit: int = 50) -> list[DiscoveredEdge]:
        with self._lock:
            res = list(self._edges.values())
            res.sort(key=lambda x: x.composite_score, reverse=True)
            return res[:limit]

    def update_edge_status(self, edge_id: str, status: EdgeStatus) -> None:
        with self._lock:
            if edge_id in self._edges:
                existing = self._edges[edge_id]
                updated = DiscoveredEdge(
                    edge_id=existing.edge_id,
                    version=existing.version,
                    hypothesis_id=existing.hypothesis_id,
                    feature_combination=existing.feature_combination,
                    supported_symbols=existing.supported_symbols,
                    supported_timeframes=existing.supported_timeframes,
                    metrics=existing.metrics,
                    p_value=existing.p_value,
                    confidence_interval_low=existing.confidence_interval_low,
                    confidence_interval_high=existing.confidence_interval_high,
                    effect_size=existing.effect_size,
                    composite_score=existing.composite_score,
                    discovery_date=existing.discovery_date,
                    last_validation_date=existing.last_validation_date,
                    status=status,
                    regime_performance=existing.regime_performance,
                    walk_forward_metrics=existing.walk_forward_metrics,
                    checksum=existing.checksum,
                    metadata=existing.metadata,
                    canonical_hash=existing.canonical_hash,
                )
                self._edges[edge_id] = updated

    def count(self, status: EdgeStatus | None = None) -> int:
        with self._lock:
            if status:
                return sum(1 for e in self._edges.values() if e.status == status)
            return len(self._edges)
