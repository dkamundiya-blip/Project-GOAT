"""
Project GOAT Phase 5 — In-Memory Feature Repository Implementation

Provides a thread-safe in-memory sliding-window implementation of IFeatureRepository.
"""

from __future__ import annotations

from collections import defaultdict
import threading
from typing import Sequence

from goat.feature_engineering.models.feature_vector import FeatureVector
from goat.feature_engineering.persistence.interfaces import IFeatureRepository


class InMemoryFeatureRepository(IFeatureRepository):
    """Thread-safe in-memory feature vector store."""

    def __init__(self, max_vectors_per_key: int = 5000):
        self.max_vectors_per_key = max_vectors_per_key
        self._vectors: dict[tuple[str, str], list[FeatureVector]] = defaultdict(list)
        self._lock = threading.RLock()

    def save_vector(self, vector: FeatureVector) -> None:
        key = (vector.symbol.upper(), vector.timeframe.lower())
        with self._lock:
            v_list = self._vectors[key]
            # Replace if vector_id exists
            for idx, existing in enumerate(v_list[-20:]):
                if existing.vector_id == vector.vector_id:
                    v_list[len(v_list) - 20 + idx] = vector
                    return
            v_list.append(vector)
            if len(v_list) > self.max_vectors_per_key:
                v_list.pop(0)

    def save_vectors(self, vectors: Sequence[FeatureVector]) -> None:
        for v in vectors:
            self.save_vector(v)

    def get_recent_vectors(self, symbol: str, timeframe: str, limit: int = 100) -> list[FeatureVector]:
        key = (symbol.upper(), timeframe.lower())
        with self._lock:
            return list(self._vectors[key][-limit:])

    def get_latest_vector(self, symbol: str, timeframe: str) -> FeatureVector | None:
        key = (symbol.upper(), timeframe.lower())
        with self._lock:
            v_list = self._vectors[key]
            return v_list[-1] if v_list else None

    def get_vectors_range(self, symbol: str, timeframe: str, start_iso: str, end_iso: str) -> list[FeatureVector]:
        key = (symbol.upper(), timeframe.lower())
        with self._lock:
            return [
                v for v in self._vectors[key]
                if start_iso <= v.timestamp <= end_iso
            ]

    def count(self, symbol: str | None = None, timeframe: str | None = None) -> int:
        with self._lock:
            if symbol and timeframe:
                return len(self._vectors[(symbol.upper(), timeframe.lower())])
            if symbol:
                return sum(len(v) for k, v in self._vectors.items() if k[0] == symbol.upper())
            return sum(len(v) for v in self._vectors.values())
