"""
Project GOAT v0.8 — Market State Core Subpackage
"""

from goat.marketstate.core.canonical import (
    compute_liquidity_id,
    compute_market_state_id,
    compute_quality_id,
    compute_report_id,
    compute_structure_id,
    compute_volatility_id,
)
from goat.marketstate.core.enums import (
    ActivityState,
    LiquidityState,
    QualityState,
    SpreadState,
    StructureState,
    TrendState,
    VolatilityState,
)
from goat.marketstate.core.models import (
    LiquidityAssessment,
    MarketQualityAssessment,
    MarketState,
    StructureAssessment,
    VolatilityAssessment,
)

__all__ = [
    # Enums
    "TrendState",
    "VolatilityState",
    "LiquidityState",
    "SpreadState",
    "ActivityState",
    "StructureState",
    "QualityState",
    # Core Models
    "MarketState",
    "VolatilityAssessment",
    "LiquidityAssessment",
    "StructureAssessment",
    "MarketQualityAssessment",
    # Identifiers
    "compute_market_state_id",
    "compute_volatility_id",
    "compute_liquidity_id",
    "compute_structure_id",
    "compute_quality_id",
    "compute_report_id",
]
