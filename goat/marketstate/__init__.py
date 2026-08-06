"""
Project GOAT v0.8 — Market State Intelligence Engine Package (`goat.marketstate`)

Step 7.1 Package for describing observable market conditions (Trend, Volatility,
Liquidity, Structure, Quality, Activity, Spread) using normalized Step 7.0 data.
"""

from goat.marketstate.classification import MarketClassificationEngine
from goat.marketstate.core import (
    ActivityState,
    LiquidityAssessment,
    LiquidityState,
    MarketQualityAssessment,
    MarketState,
    QualityState,
    SpreadState,
    StructureAssessment,
    StructureState,
    TrendState,
    VolatilityAssessment,
    VolatilityState,
    compute_liquidity_id,
    compute_market_state_id,
    compute_quality_id,
    compute_report_id,
    compute_structure_id,
    compute_volatility_id,
)
from goat.marketstate.engine import MarketStateEngine
from goat.marketstate.liquidity import LiquidityAssessmentEngine
from goat.marketstate.persistence import (
    LiquidityRepository,
    MarketStateReportRepository,
    MarketStateRepository,
    QualityRepository,
    StructureRepository,
    VolatilityRepository,
    init_marketstate_db,
)
from goat.marketstate.quality import MarketQualityEngine
from goat.marketstate.reporting import (
    LiquidityReport,
    MarketStateExecutiveReport,
    MarketStateReport,
    QualityReport,
    StructureReport,
    VolatilityReport,
)
from goat.marketstate.structure import StructureAssessmentEngine
from goat.marketstate.volatility import VolatilityAssessmentEngine

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
    # Assessment Engines & Coordinators
    "MarketStateEngine",
    "VolatilityAssessmentEngine",
    "LiquidityAssessmentEngine",
    "StructureAssessmentEngine",
    "MarketQualityEngine",
    "MarketClassificationEngine",
    # Persistence
    "init_marketstate_db",
    "MarketStateRepository",
    "VolatilityRepository",
    "LiquidityRepository",
    "StructureRepository",
    "QualityRepository",
    "MarketStateReportRepository",
    # Reporting
    "MarketStateReport",
    "VolatilityReport",
    "LiquidityReport",
    "StructureReport",
    "QualityReport",
    "MarketStateExecutiveReport",
]
