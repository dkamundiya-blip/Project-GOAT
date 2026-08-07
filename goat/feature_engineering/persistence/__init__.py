"""
Project GOAT Phase 5 — Feature Persistence Package (`goat.feature_engineering.persistence`)
"""

from goat.feature_engineering.persistence.in_memory import InMemoryFeatureRepository
from goat.feature_engineering.persistence.interfaces import IFeatureRepository
from goat.feature_engineering.persistence.sqlite import (
    SQLiteFeatureRepository,
    init_feature_store_db,
)

__all__ = [
    "IFeatureRepository",
    "InMemoryFeatureRepository",
    "init_feature_store_db",
    "SQLiteFeatureRepository",
]
