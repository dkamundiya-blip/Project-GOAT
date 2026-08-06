"""
Project GOAT v0.7 — Market Regime & Edge Applicability Enums

Defines deterministic enums for regime types, activation states, volatility, liquidity, participation, and trend states.
"""

from enum import Enum


class RegimeType(str, Enum):
    """Supported deterministic market regime classifications."""

    TRENDING = "TRENDING"
    RANGING = "RANGING"
    BREAKOUT = "BREAKOUT"
    REVERSAL = "REVERSAL"
    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    LIQUIDITY_EXPANSION = "LIQUIDITY_EXPANSION"
    LIQUIDITY_CONTRACTION = "LIQUIDITY_CONTRACTION"
    TRANSITIONAL = "TRANSITIONAL"
    UNDEFINED = "UNDEFINED"


class EdgeActivationState(str, Enum):
    """Deterministic activation states for candidate quantitative edges."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CONDITIONAL = "CONDITIONAL"
    WATCHLIST = "WATCHLIST"
    REJECTED = "REJECTED"


class VolatilityState(str, Enum):
    """Classifications of market volatility state."""

    HIGH = "HIGH"
    LOW = "LOW"
    NORMAL = "NORMAL"


class LiquidityState(str, Enum):
    """Classifications of market liquidity state."""

    EXPANSION = "EXPANSION"
    CONTRACTION = "CONTRACTION"
    NORMAL = "NORMAL"


class ParticipationState(str, Enum):
    """Classifications of market participant activity."""

    INSTITUTIONAL = "INSTITUTIONAL"
    RETAIL = "RETAIL"
    BALANCED = "BALANCED"


class TrendState(str, Enum):
    """Classifications of market trend state."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class StructuralState(str, Enum):
    """Classifications of market structural state."""

    CONSOLIDATION = "CONSOLIDATION"
    BREAKOUT_EXPANSION = "BREAKOUT_EXPANSION"
    MEAN_REVERTING = "MEAN_REVERTING"
