"""
Project GOAT Phase 4 — Storage Layer Repository Interfaces

Abstract base interfaces enforcing the Repository Pattern for loose coupling and pluggable persistence backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from goat.market_intelligence.models.candle import IntelligenceCandle
from goat.market_intelligence.models.event import MarketEvent
from goat.market_intelligence.models.market_state import MarketState
from goat.market_intelligence.models.quality import DataQualityReport
from goat.market_intelligence.models.statistics import MarketStatistics
from goat.market_intelligence.models.tick import RecordedTick


class ITickRepository(ABC):
    """Repository interface for RecordedTick persistence."""

    @abstractmethod
    def save_tick(self, tick: RecordedTick) -> None:
        """Persist a single recorded tick."""
        pass

    @abstractmethod
    def save_ticks(self, ticks: Sequence[RecordedTick]) -> None:
        """Persist a batch of recorded ticks."""
        pass

    @abstractmethod
    def get_recent_ticks(self, symbol: str, limit: int = 100) -> list[RecordedTick]:
        """Fetch recent ticks for a symbol ordered by sequence/timestamp ascending."""
        pass

    @abstractmethod
    def get_ticks_range(self, symbol: str, start_iso: str, end_iso: str) -> list[RecordedTick]:
        """Fetch ticks for a symbol within a timestamp interval."""
        pass

    @abstractmethod
    def get_latest_tick(self, symbol: str) -> RecordedTick | None:
        """Get latest tick for symbol."""
        pass

    @abstractmethod
    def count(self, symbol: str | None = None) -> int:
        """Count persisted ticks."""
        pass


class ICandleRepository(ABC):
    """Repository interface for IntelligenceCandle persistence."""

    @abstractmethod
    def save_candle(self, candle: IntelligenceCandle) -> None:
        """Persist a single intelligence candle bar."""
        pass

    @abstractmethod
    def save_candles(self, candles: Sequence[IntelligenceCandle]) -> None:
        """Persist a batch of intelligence candles."""
        pass

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> list[IntelligenceCandle]:
        """Fetch completed candles for symbol and timeframe ordered ascending."""
        pass

    @abstractmethod
    def get_latest_candle(self, symbol: str, timeframe: str) -> IntelligenceCandle | None:
        """Get latest candle for symbol and timeframe."""
        pass

    @abstractmethod
    def count(self, symbol: str | None = None, timeframe: str | None = None) -> int:
        """Count persisted candles."""
        pass


class IMarketStatisticsRepository(ABC):
    """Repository interface for MarketStatistics persistence."""

    @abstractmethod
    def save_statistics(self, stats: MarketStatistics) -> None:
        """Persist a single market statistics calculation."""
        pass

    @abstractmethod
    def get_recent_statistics(self, symbol: str, limit: int = 50) -> list[MarketStatistics]:
        """Fetch recent statistics for symbol ordered ascending."""
        pass

    @abstractmethod
    def get_latest_statistics(self, symbol: str) -> MarketStatistics | None:
        """Get latest market statistics for symbol."""
        pass


class IMarketStateRepository(ABC):
    """Repository interface for MarketState persistence."""

    @abstractmethod
    def save_state(self, state: MarketState) -> None:
        """Persist a single market state classification."""
        pass

    @abstractmethod
    def get_recent_states(self, symbol: str, limit: int = 50) -> list[MarketState]:
        """Fetch recent market state classifications for symbol ordered ascending."""
        pass

    @abstractmethod
    def get_latest_state(self, symbol: str) -> MarketState | None:
        """Get latest classified market state for symbol."""
        pass


class IEventRepository(ABC):
    """Repository interface for MarketEvent persistence."""

    @abstractmethod
    def save_event(self, event: MarketEvent) -> None:
        """Persist a single detected market event."""
        pass

    @abstractmethod
    def get_recent_events(self, symbol: str | None = None, limit: int = 50) -> list[MarketEvent]:
        """Fetch recent market events ordered ascending by timestamp."""
        pass

    @abstractmethod
    def get_events_by_type(self, event_type: str, symbol: str | None = None, limit: int = 50) -> list[MarketEvent]:
        """Fetch events filtered by event category."""
        pass


class IDataQualityRepository(ABC):
    """Repository interface for DataQualityReport persistence."""

    @abstractmethod
    def save_report(self, report: DataQualityReport) -> None:
        """Persist a data quality audit report."""
        pass

    @abstractmethod
    def get_recent_reports(self, symbol: str | None = None, limit: int = 50) -> list[DataQualityReport]:
        """Fetch recent data quality reports."""
        pass
