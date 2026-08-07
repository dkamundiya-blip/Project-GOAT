"""
Project GOAT Phase 4 — Market Intelligence Engine Package (`goat.market_intelligence`)

Modular, institutional-grade market data collection, validation, enrichment, multi-timeframe candle building,
continuous statistical calculation, 5-dimensional state classification, event detection, and pluggable storage.
"""

from goat.market_intelligence.candles import UniversalCandleBuilder
from goat.market_intelligence.engine import (
    MarketIntelligenceEngine,
    MasterMarketIntelligenceEngine,
)
from goat.market_intelligence.events import EventDetectionEngine
from goat.market_intelligence.market_state import MarketStateEngine
from goat.market_intelligence.models import (
    TIMEFRAME_SECONDS,
    DataQualityCheckResult,
    DataQualityReport,
    IntelligenceCandle,
    IntelligenceEventType,
    IntelligenceTimeframe,
    LiquidityLevel,
    MarketEvent,
    MarketState,
    MarketStatistics,
    MomentumState,
    QualityIssue,
    QualityIssueReason,
    RecordedTick,
    RegimeState,
    TrendState,
    VolatilityLevel,
    compute_data_quality_report_id,
    compute_intelligence_candle_id,
    compute_market_event_id,
    compute_market_state_id,
    compute_market_statistics_id,
    compute_recorded_tick_id,
)
from goat.market_intelligence.persistence import (
    ICandleRepository,
    IDataQualityRepository,
    IEventRepository,
    IMarketStateRepository,
    IMarketStatisticsRepository,
    InMemoryCandleRepository,
    InMemoryDataQualityRepository,
    InMemoryEventRepository,
    InMemoryMarketStateRepository,
    InMemoryMarketStatisticsRepository,
    InMemoryTickRepository,
    ITickRepository,
    SQLiteCandleRepository,
    SQLiteDataQualityRepository,
    SQLiteEventRepository,
    SQLiteMarketStateRepository,
    SQLiteMarketStatisticsRepository,
    SQLiteTickRepository,
    init_market_intelligence_db,
)
from goat.market_intelligence.quality import DataQualityEngine
from goat.market_intelligence.recorder import TickRecorder
from goat.market_intelligence.statistics import MarketStatisticsEngine

__all__ = [
    # Master Engine & Orchestrator
    "MasterMarketIntelligenceEngine",
    "MarketIntelligenceEngine",
    # Sub-Engines
    "TickRecorder",
    "UniversalCandleBuilder",
    "MarketStatisticsEngine",
    "MarketStateEngine",
    "EventDetectionEngine",
    "DataQualityEngine",
    # Domain Models & Enums
    "RecordedTick",
    "IntelligenceCandle",
    "IntelligenceTimeframe",
    "TIMEFRAME_SECONDS",
    "MarketStatistics",
    "MarketState",
    "TrendState",
    "VolatilityLevel",
    "MomentumState",
    "RegimeState",
    "LiquidityLevel",
    "MarketEvent",
    "IntelligenceEventType",
    "DataQualityCheckResult",
    "DataQualityReport",
    "QualityIssue",
    "QualityIssueReason",
    # ID Identifiers & Canonical Helpers
    "compute_recorded_tick_id",
    "compute_intelligence_candle_id",
    "compute_market_statistics_id",
    "compute_market_state_id",
    "compute_market_event_id",
    "compute_data_quality_report_id",
    # Storage Interfaces & Implementations
    "ITickRepository",
    "ICandleRepository",
    "IMarketStatisticsRepository",
    "IMarketStateRepository",
    "IEventRepository",
    "IDataQualityRepository",
    "InMemoryTickRepository",
    "InMemoryCandleRepository",
    "InMemoryMarketStatisticsRepository",
    "InMemoryMarketStateRepository",
    "InMemoryEventRepository",
    "InMemoryDataQualityRepository",
    "init_market_intelligence_db",
    "SQLiteTickRepository",
    "SQLiteCandleRepository",
    "SQLiteMarketStatisticsRepository",
    "SQLiteMarketStateRepository",
    "SQLiteEventRepository",
    "SQLiteDataQualityRepository",
]
