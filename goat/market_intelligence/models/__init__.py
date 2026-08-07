"""
Project GOAT Phase 4 — Market Intelligence Domain Models Package
"""

from goat.market_intelligence.models.candle import (
    TIMEFRAME_SECONDS,
    IntelligenceCandle,
    IntelligenceTimeframe,
    compute_intelligence_candle_id,
)
from goat.market_intelligence.models.event import (
    IntelligenceEventType,
    MarketEvent,
    compute_market_event_id,
)
from goat.market_intelligence.models.market_state import (
    LiquidityLevel,
    MarketState,
    MomentumState,
    RegimeState,
    TrendState,
    VolatilityLevel,
    compute_market_state_id,
)
from goat.market_intelligence.models.quality import (
    DataQualityCheckResult,
    DataQualityReport,
    QualityIssue,
    QualityIssueReason,
    compute_data_quality_report_id,
)
from goat.market_intelligence.models.statistics import (
    MarketStatistics,
    compute_market_statistics_id,
)
from goat.market_intelligence.models.tick import (
    RecordedTick,
    compute_recorded_tick_id,
)

__all__ = [
    # RecordedTick
    "RecordedTick",
    "compute_recorded_tick_id",
    # IntelligenceCandle
    "IntelligenceCandle",
    "IntelligenceTimeframe",
    "TIMEFRAME_SECONDS",
    "compute_intelligence_candle_id",
    # MarketStatistics
    "MarketStatistics",
    "compute_market_statistics_id",
    # MarketState & Enums
    "MarketState",
    "TrendState",
    "VolatilityLevel",
    "MomentumState",
    "RegimeState",
    "LiquidityLevel",
    "compute_market_state_id",
    # MarketEvent & EventType
    "MarketEvent",
    "IntelligenceEventType",
    "compute_market_event_id",
    # DataQuality & Issues
    "QualityIssueReason",
    "QualityIssue",
    "DataQualityCheckResult",
    "DataQualityReport",
    "compute_data_quality_report_id",
]
