"""
Project GOAT Phase 4 — Storage Layer Package (`goat.market_intelligence.persistence`)
"""

from goat.market_intelligence.persistence.in_memory import (
    InMemoryCandleRepository,
    InMemoryDataQualityRepository,
    InMemoryEventRepository,
    InMemoryMarketStateRepository,
    InMemoryMarketStatisticsRepository,
    InMemoryTickRepository,
)
from goat.market_intelligence.persistence.interfaces import (
    ICandleRepository,
    IDataQualityRepository,
    IEventRepository,
    IMarketStateRepository,
    IMarketStatisticsRepository,
    ITickRepository,
)
from goat.market_intelligence.persistence.sqlite import (
    SQLiteCandleRepository,
    SQLiteDataQualityRepository,
    SQLiteEventRepository,
    SQLiteMarketStateRepository,
    SQLiteMarketStatisticsRepository,
    SQLiteTickRepository,
    init_market_intelligence_db,
)

__all__ = [
    # Interfaces
    "ITickRepository",
    "ICandleRepository",
    "IMarketStatisticsRepository",
    "IMarketStateRepository",
    "IEventRepository",
    "IDataQualityRepository",
    # In-Memory Implementations
    "InMemoryTickRepository",
    "InMemoryCandleRepository",
    "InMemoryMarketStatisticsRepository",
    "InMemoryMarketStateRepository",
    "InMemoryEventRepository",
    "InMemoryDataQualityRepository",
    # SQLite Implementations
    "init_market_intelligence_db",
    "SQLiteTickRepository",
    "SQLiteCandleRepository",
    "SQLiteMarketStatisticsRepository",
    "SQLiteMarketStateRepository",
    "SQLiteEventRepository",
    "SQLiteDataQualityRepository",
]
