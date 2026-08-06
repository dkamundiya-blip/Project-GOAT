"""
Project GOAT v0.9 — Quantitative Edge Discovery Engine Enums
"""

from enum import Enum


class EdgeCategory(str, Enum):
    """Categories of Discovered Quantitative Edges."""
    STATISTICAL_ARBITRAGE = "STATISTICAL_ARBITRAGE"
    MICROSTRUCTURE_ANOMALY = "MICROSTRUCTURE_ANOMALY"
    REGIME_TRANSITION = "REGIME_TRANSITION"
    CROSS_ASSET_CORRELATION = "CROSS_ASSET_CORRELATION"
    JUMP_PERSISTENCE = "JUMP_PERSISTENCE"


class PatternType(str, Enum):
    """Types of Discovered Statistical Patterns."""
    VOLATILITY_EXPANSION_PATTERN = "VOLATILITY_EXPANSION_PATTERN"
    JUMP_CLUSTERING_PATTERN = "JUMP_CLUSTERING_PATTERN"
    LIQUIDITY_IMBALANCE_PATTERN = "LIQUIDITY_IMBALANCE_PATTERN"
    LATENCY_ASYMMETRY_PATTERN = "LATENCY_ASYMMETRY_PATTERN"
    SPREAD_DISPERSION_PATTERN = "SPREAD_DISPERSION_PATTERN"


class ValidationStatus(str, Enum):
    """Validation status for Edge Candidate."""
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


class RejectionReason(str, Enum):
    """Protocol rejection reasons for edge validation."""
    NONE = "NONE"
    INSUFFICIENT_OBSERVATIONS = "INSUFFICIENT_OBSERVATIONS"
    DUPLICATE_EDGE = "DUPLICATE_EDGE"
    POOR_CONFIDENCE = "POOR_CONFIDENCE"
    OVERFIT_EVIDENCE = "OVERFIT_EVIDENCE"
    SINGLE_REGIME_BEHAVIOR = "SINGLE_REGIME_BEHAVIOR"


class NoveltyStatus(str, Enum):
    """Novelty classification status."""
    GENUINELY_NOVEL = "GENUINELY_NOVEL"
    MODERATE_NOVELTY = "MODERATE_NOVELTY"
    DUPLICATE_EXISTS = "DUPLICATE_EXISTS"


class QualityTier(str, Enum):
    """Institutional edge scoring quality tiers."""
    INSTITUTIONAL_GRADE = "INSTITUTIONAL_GRADE"
    HIGH_QUALITY = "HIGH_QUALITY"
    MARGINAL = "MARGINAL"
    SUBPAR = "SUBPAR"
