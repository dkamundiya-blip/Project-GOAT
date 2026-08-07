"""
Project GOAT Phase 4 — High-Performance In-Memory Repository Implementations

Provides thread-safe in-memory sliding-window implementations of all Phase 4 storage interfaces.
"""

from __future__ import annotations

from collections import defaultdict
import threading
from typing import Sequence

from goat.market_intelligence.models.candle import IntelligenceCandle
from goat.market_intelligence.models.event import MarketEvent
from goat.market_intelligence.models.market_state import MarketState
from goat.market_intelligence.models.quality import DataQualityReport
from goat.market_intelligence.models.statistics import MarketStatistics
from goat.market_intelligence.models.tick import RecordedTick
from goat.market_intelligence.persistence.interfaces import (
    ICandleRepository,
    IDataQualityRepository,
    IEventRepository,
    IMarketStateRepository,
    IMarketStatisticsRepository,
    ITickRepository,
)


class InMemoryTickRepository(ITickRepository):
    """Thread-safe in-memory tick repository with max capacity limit."""

    def __init__(self, max_ticks_per_symbol: int = 10000):
        self.max_ticks_per_symbol = max_ticks_per_symbol
        self._ticks: dict[str, list[RecordedTick]] = defaultdict(list)
        self._lock = threading.RLock()

    def save_tick(self, tick: RecordedTick) -> None:
        with self._lock:
            sym_list = self._ticks[tick.symbol]
            # Avoid duplicate tick_id
            if not any(t.tick_id == tick.tick_id for t in sym_list[-50:]):
                sym_list.append(tick)
                if len(sym_list) > self.max_ticks_per_symbol:
                    sym_list.pop(0)

    def save_ticks(self, ticks: Sequence[RecordedTick]) -> None:
        for t in ticks:
            self.save_tick(t)

    def get_recent_ticks(self, symbol: str, limit: int = 100) -> list[RecordedTick]:
        with self._lock:
            return list(self._ticks[symbol.upper()][-limit:])

    def get_ticks_range(self, symbol: str, start_iso: str, end_iso: str) -> list[RecordedTick]:
        with self._lock:
            return [
                t for t in self._ticks[symbol.upper()]
                if start_iso <= t.timestamp <= end_iso
            ]

    def get_latest_tick(self, symbol: str) -> RecordedTick | None:
        with self._lock:
            sym_list = self._ticks[symbol.upper()]
            return sym_list[-1] if sym_list else None

    def count(self, symbol: str | None = None) -> int:
        with self._lock:
            if symbol:
                return len(self._ticks[symbol.upper()])
            return sum(len(v) for v in self._ticks.values())


class InMemoryCandleRepository(ICandleRepository):
    """Thread-safe in-memory candle repository."""

    def __init__(self, max_candles_per_tf: int = 5000):
        self.max_candles_per_tf = max_candles_per_tf
        self._candles: dict[tuple[str, str], list[IntelligenceCandle]] = defaultdict(list)
        self._lock = threading.RLock()

    def save_candle(self, candle: IntelligenceCandle) -> None:
        key = (candle.symbol.upper(), candle.timeframe.value.lower())
        with self._lock:
            cand_list = self._candles[key]
            # Update or replace if candle_id exists
            for idx, existing in enumerate(cand_list[-20:]):
                if existing.candle_id == candle.candle_id:
                    cand_list[len(cand_list) - 20 + idx] = candle
                    return
            cand_list.append(candle)
            if len(cand_list) > self.max_candles_per_tf:
                cand_list.pop(0)

    def save_candles(self, candles: Sequence[IntelligenceCandle]) -> None:
        for c in candles:
            self.save_candle(c)

    def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> list[IntelligenceCandle]:
        key = (symbol.upper(), timeframe.lower())
        with self._lock:
            return list(self._candles[key][-limit:])

    def get_latest_candle(self, symbol: str, timeframe: str) -> IntelligenceCandle | None:
        key = (symbol.upper(), timeframe.lower())
        with self._lock:
            cand_list = self._candles[key]
            return cand_list[-1] if cand_list else None

    def count(self, symbol: str | None = None, timeframe: str | None = None) -> int:
        with self._lock:
            if symbol and timeframe:
                return len(self._candles[(symbol.upper(), timeframe.lower())])
            if symbol:
                return sum(len(v) for k, v in self._candles.items() if k[0] == symbol.upper())
            return sum(len(v) for v in self._candles.values())


class InMemoryMarketStatisticsRepository(IMarketStatisticsRepository):
    """Thread-safe in-memory statistics repository."""

    def __init__(self, max_records_per_symbol: int = 2000):
        self.max_records_per_symbol = max_records_per_symbol
        self._stats: dict[str, list[MarketStatistics]] = defaultdict(list)
        self._lock = threading.RLock()

    def save_statistics(self, stats: MarketStatistics) -> None:
        with self._lock:
            stat_list = self._stats[stats.symbol.upper()]
            stat_list.append(stats)
            if len(stat_list) > self.max_records_per_symbol:
                stat_list.pop(0)

    def get_recent_statistics(self, symbol: str, limit: int = 50) -> list[MarketStatistics]:
        with self._lock:
            return list(self._stats[symbol.upper()][-limit:])

    def get_latest_statistics(self, symbol: str) -> MarketStatistics | None:
        with self._lock:
            stat_list = self._stats[symbol.upper()]
            return stat_list[-1] if stat_list else None


class InMemoryMarketStateRepository(IMarketStateRepository):
    """Thread-safe in-memory market state repository."""

    def __init__(self, max_records_per_symbol: int = 2000):
        self.max_records_per_symbol = max_records_per_symbol
        self._states: dict[str, list[MarketState]] = defaultdict(list)
        self._lock = threading.RLock()

    def save_state(self, state: MarketState) -> None:
        with self._lock:
            state_list = self._states[state.symbol.upper()]
            state_list.append(state)
            if len(state_list) > self.max_records_per_symbol:
                state_list.pop(0)

    def get_recent_states(self, symbol: str, limit: int = 50) -> list[MarketState]:
        with self._lock:
            return list(self._states[symbol.upper()][-limit:])

    def get_latest_state(self, symbol: str) -> MarketState | None:
        with self._lock:
            state_list = self._states[symbol.upper()]
            return state_list[-1] if state_list else None


class InMemoryEventRepository(IEventRepository):
    """Thread-safe in-memory event repository."""

    def __init__(self, max_events: int = 5000):
        self.max_events = max_events
        self._events: list[MarketEvent] = []
        self._lock = threading.RLock()

    def save_event(self, event: MarketEvent) -> None:
        with self._lock:
            self._events.append(event)
            if len(self._events) > self.max_events:
                self._events.pop(0)

    def get_recent_events(self, symbol: str | None = None, limit: int = 50) -> list[MarketEvent]:
        with self._lock:
            if symbol:
                filtered = [e for e in self._events if e.symbol.upper() == symbol.upper()]
                return filtered[-limit:]
            return list(self._events[-limit:])

    def get_events_by_type(self, event_type: str, symbol: str | None = None, limit: int = 50) -> list[MarketEvent]:
        with self._lock:
            ev_type_str = str(event_type).upper()
            filtered = [
                e for e in self._events
                if e.event_type.value.upper() == ev_type_str
                and (symbol is None or e.symbol.upper() == symbol.upper())
            ]
            return filtered[-limit:]


class InMemoryDataQualityRepository(IDataQualityRepository):
    """Thread-safe in-memory data quality repository."""

    def __init__(self, max_reports: int = 1000):
        self.max_reports = max_reports
        self._reports: list[DataQualityReport] = []
        self._lock = threading.RLock()

    def save_report(self, report: DataQualityReport) -> None:
        with self._lock:
            self._reports.append(report)
            if len(self._reports) > self.max_reports:
                self._reports.pop(0)

    def get_recent_reports(self, symbol: str | None = None, limit: int = 50) -> list[DataQualityReport]:
        with self._lock:
            if symbol:
                filtered = [r for r in self._reports if r.symbol.upper() == symbol.upper()]
                return filtered[-limit:]
            return list(self._reports[-limit:])
