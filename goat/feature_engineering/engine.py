"""
Project GOAT Phase 5 — Master Feature Engineering Engine (`goat.feature_engineering.engine`)

Master coordinator orchestrating all 7 quantitative feature engines:
Trend, Volatility, Momentum, Market Structure, Liquidity, Session Intelligence, and Statistical features.
Persists immutable FeatureVectors into the Feature Store and provides a thread-safe Observer EventBus.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable

from goat.feature_engineering.liquidity.engine import LiquidityFeatureEngine
from goat.feature_engineering.models.feature_vector import (
    FeatureVector,
    compute_feature_vector_id,
)
from goat.feature_engineering.momentum.engine import MomentumFeatureEngine
from goat.feature_engineering.persistence.in_memory import InMemoryFeatureRepository
from goat.feature_engineering.persistence.interfaces import IFeatureRepository
from goat.feature_engineering.persistence.sqlite import (
    SQLiteFeatureRepository,
    init_feature_store_db,
)
from goat.feature_engineering.session.engine import SessionIntelligenceEngine
from goat.feature_engineering.statistical.engine import StatisticalFeatureEngine
from goat.feature_engineering.structure.engine import MarketStructureFeatureEngine
from goat.feature_engineering.trend.engine import TrendFeatureEngine
from goat.feature_engineering.volatility.engine import VolatilityFeatureEngine
from goat.logging import get_logger
from goat.market_intelligence.models.candle import IntelligenceCandle
from goat.market_intelligence.models.statistics import MarketStatistics
from goat.market_intelligence.models.tick import RecordedTick
from goat.research.edge.canonical import compute_canonical_sha256

_log = get_logger("feature_engineering.engine")


class MasterFeatureEngineeringEngine:
    """Master Feature Engineering Engine generating 64 quantitative features across 7 specialized engines."""

    def __init__(
        self,
        db_path: str | Path | sqlite3.Connection | None = None,
        repository: IFeatureRepository | None = None,
        version: str = "5.0.0",
    ):
        self.version = version

        # 1. Initialize Persistence Repository
        if repository is not None:
            self.repository = repository
            self.conn = None
        elif db_path is not None:
            self.conn = init_feature_store_db(db_path)
            self.repository = SQLiteFeatureRepository(self.conn)
        else:
            self.conn = None
            self.repository = InMemoryFeatureRepository()

        # 2. Instantiate 7 Feature Engines
        self.trend_engine = TrendFeatureEngine()
        self.volatility_engine = VolatilityFeatureEngine()
        self.momentum_engine = MomentumFeatureEngine()
        self.structure_engine = MarketStructureFeatureEngine()
        self.liquidity_engine = LiquidityFeatureEngine()
        self.session_engine = SessionIntelligenceEngine()
        self.statistical_engine = StatisticalFeatureEngine()

        # 3. Thread-Safe Observer EventBus
        self._vector_listeners: list[Callable[[FeatureVector], None]] = []
        self._bus_lock = threading.RLock()

    def subscribe_feature_vectors(self, callback: Callable[[FeatureVector], None]) -> None:
        """Subscribe to streaming engineered FeatureVector updates."""
        with self._bus_lock:
            self._vector_listeners.append(callback)

    def process_candle(
        self,
        candle: IntelligenceCandle,
        current_stats: MarketStatistics | None = None,
    ) -> FeatureVector:
        """Process an IntelligenceCandle and generate a complete 64-feature FeatureVector."""
        features: dict[str, float] = {}

        # Module 1: Trend Features (10)
        features.update(self.trend_engine.compute_features(candle))

        # Module 2: Volatility Features (9)
        features.update(self.volatility_engine.compute_features(candle, current_stats=current_stats))

        # Module 3: Momentum Features (8)
        features.update(self.momentum_engine.compute_features(candle))

        # Module 4: Market Structure Features (10)
        features.update(self.structure_engine.compute_features(candle))

        # Module 5: Liquidity Features (8)
        features.update(self.liquidity_engine.compute_features(candle))

        # Module 6: Session Intelligence Features (9)
        features.update(self.session_engine.compute_features(candle))

        # Module 7: Statistical Features (10)
        features.update(self.statistical_engine.compute_features(candle))

        # Compute Deterministic ID & Canonical Hashes
        sym = candle.symbol.upper()
        tf = candle.timeframe.value.lower()
        ts = candle.close_timestamp

        vector_id, canon_hash = compute_feature_vector_id(
            symbol=sym,
            timeframe=tf,
            timestamp=ts,
            features=features,
            version=self.version,
        )

        checksum = compute_canonical_sha256(
            {
                "feature_count": len(features),
                "symbol": sym,
                "timeframe": tf,
                "timestamp": ts,
                "version": self.version,
            }
        )

        vector = FeatureVector(
            vector_id=vector_id,
            symbol=sym,
            timeframe=tf,
            timestamp=ts,
            version=self.version,
            features=features,
            checksum=checksum,
            metadata={"feature_count": len(features), "candle_id": candle.candle_id},
            canonical_hash=canon_hash,
        )

        # Save to Feature Store
        self.repository.save_vector(vector)

        # Notify EventBus subscribers
        with self._bus_lock:
            for cb in self._vector_listeners:
                try:
                    cb(vector)
                except Exception as exc:
                    _log.error("feature_vector_listener_exception", error=str(exc))

        return vector

    def get_latest_feature_vector(self, symbol: str, timeframe: str) -> FeatureVector | None:
        """Query the latest feature vector from the Feature Store."""
        return self.repository.get_latest_vector(symbol, timeframe)


# Convenience alias matching prompt naming
FeatureEngineeringEngine = MasterFeatureEngineeringEngine
