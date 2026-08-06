"""
Project GOAT v0.8 — Core Enums for Market State Intelligence Engine

Defines deterministic enums for market state classification:
- TrendState
- VolatilityState
- LiquidityState
- SpreadState
- ActivityState
- StructureState
- QualityState
"""

from enum import Enum


class TrendState(str, Enum):
    """Trend direction and strength classification."""

    STRONG_UPTREND = "STRONG_UPTREND"
    UPTREND = "UPTREND"
    SIDEWAYS = "SIDEWAYS"
    DOWNTREND = "DOWNTREND"
    STRONG_DOWNTREND = "STRONG_DOWNTREND"
    UNKNOWN = "UNKNOWN"


class VolatilityState(str, Enum):
    """Realized volatility level classification."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class LiquidityState(str, Enum):
    """Market liquidity depth and continuity classification."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class SpreadState(str, Enum):
    """Spread width classification."""

    TIGHT = "TIGHT"
    NORMAL = "NORMAL"
    WIDE = "WIDE"
    EXTREME = "EXTREME"


class ActivityState(str, Enum):
    """Market tick frequency and activity intensity classification."""

    QUIET = "QUIET"
    NORMAL = "NORMAL"
    ACTIVE = "ACTIVE"
    VERY_ACTIVE = "VERY_ACTIVE"


class StructureState(str, Enum):
    """Market price action structure classification."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    RANGING = "RANGING"
    TRANSITIONAL = "TRANSITIONAL"
    UNKNOWN = "UNKNOWN"


class QualityState(str, Enum):
    """Market data stream and validation quality classification."""

    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    POOR = "POOR"
    INVALID = "INVALID"
