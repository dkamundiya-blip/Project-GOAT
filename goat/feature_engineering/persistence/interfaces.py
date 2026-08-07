"""
Project GOAT Phase 5 — Feature Repository Interface

Defines the IFeatureRepository abstract interface for the Feature Store.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from goat.feature_engineering.models.feature_vector import FeatureVector


class IFeatureRepository(ABC):
    """Repository interface for Feature Store persistence."""

    @abstractmethod
    def save_vector(self, vector: FeatureVector) -> None:
        """Persist a single engineered feature vector."""
        pass

    @abstractmethod
    def save_vectors(self, vectors: Sequence[FeatureVector]) -> None:
        """Persist a batch of feature vectors."""
        pass

    @abstractmethod
    def get_recent_vectors(self, symbol: str, timeframe: str, limit: int = 100) -> list[FeatureVector]:
        """Query recent feature vectors for a symbol and timeframe ordered ascending."""
        pass

    @abstractmethod
    def get_latest_vector(self, symbol: str, timeframe: str) -> FeatureVector | None:
        """Query the latest feature vector for a symbol and timeframe."""
        pass

    @abstractmethod
    def get_vectors_range(self, symbol: str, timeframe: str, start_iso: str, end_iso: str) -> list[FeatureVector]:
        """Query feature vectors within a timestamp interval."""
        pass

    @abstractmethod
    def count(self, symbol: str | None = None, timeframe: str | None = None) -> int:
        """Count persisted feature vectors."""
        pass
