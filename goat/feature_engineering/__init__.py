"""
Project GOAT Phase 5 — Feature Engineering Engine Package (`goat.feature_engineering`)

Modular, institutional-grade quantitative feature engineering subsystem exporting 64 features across
7 specialized feature engines and a dedicated Feature Store persistence layer.
"""

from goat.feature_engineering.engine import (
    FeatureEngineeringEngine,
    MasterFeatureEngineeringEngine,
)
from goat.feature_engineering.liquidity import LiquidityFeatureEngine
from goat.feature_engineering.models import (
    FeatureVector,
    compute_feature_vector_id,
)
from goat.feature_engineering.momentum import MomentumFeatureEngine
from goat.feature_engineering.persistence import (
    IFeatureRepository,
    InMemoryFeatureRepository,
    SQLiteFeatureRepository,
    init_feature_store_db,
)
from goat.feature_engineering.session import SessionIntelligenceEngine
from goat.feature_engineering.statistical import StatisticalFeatureEngine
from goat.feature_engineering.structure import MarketStructureFeatureEngine
from goat.feature_engineering.trend import TrendFeatureEngine
from goat.feature_engineering.volatility import VolatilityFeatureEngine

__all__ = [
    # Master Engine
    "MasterFeatureEngineeringEngine",
    "FeatureEngineeringEngine",
    # Sub-Engines
    "TrendFeatureEngine",
    "VolatilityFeatureEngine",
    "MomentumFeatureEngine",
    "MarketStructureFeatureEngine",
    "LiquidityFeatureEngine",
    "SessionIntelligenceEngine",
    "StatisticalFeatureEngine",
    # Models & Identifiers
    "FeatureVector",
    "compute_feature_vector_id",
    # Persistence & Feature Store
    "IFeatureRepository",
    "InMemoryFeatureRepository",
    "init_feature_store_db",
    "SQLiteFeatureRepository",
]
