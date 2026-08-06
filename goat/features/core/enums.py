"""
Project GOAT v0.7 — Feature Core Enums

Defines domain enums for feature taxonomy, output data types, determinism classification,
stationarity properties, and deprecation status.
"""

from __future__ import annotations

import enum


class TaxonomyCategory(str, enum.Enum):
    """Hierarchical taxonomy categories for Project GOAT features (Part 2 Taxonomy)."""
    PRICE_STRUCTURE = "price_structure"
    TREND = "trend"
    VOLATILITY = "volatility"
    MOMENTUM = "momentum"
    LIQUIDITY = "liquidity"
    MARKET_GEOMETRY = "market_geometry"
    TIME = "time"
    RANGE = "range"
    WICK_BEHAVIOUR = "wick_behaviour"
    CANDLE_BEHAVIOUR = "candle_behaviour"
    SESSION_BEHAVIOUR = "session_behaviour"
    MICROSTRUCTURE = "microstructure"
    STATISTICAL = "statistical"
    CROSS_TIMEFRAME = "cross_timeframe"
    COMPOSITE = "composite"
    META = "meta"


class DataType(str, enum.Enum):
    """Output data type classification for feature calculations."""
    FLOAT64 = "float64"
    INT64 = "int64"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"


class DeterminismClass(str, enum.Enum):
    """Numerical determinism classification."""
    IEEE_754_STRICT = "ieee_754_strict"
    STOCHASTIC_APPROXIMATED = "stochastic_approximated"


class StationarityType(str, enum.Enum):
    """Statistical stationarity property of feature outputs."""
    STATIONARY = "stationary"
    DIFFERENCED_STATIONARY = "differenced_stationary"
    NON_STATIONARY_RAW = "non_stationary_raw"


class DeprecationStatus(str, enum.Enum):
    """Feature operational lifecycle status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
