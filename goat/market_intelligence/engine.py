"""
Project GOAT Phase 4 — Master Market Intelligence Engine (`goat.market_intelligence.engine`)

Master orchestrator coordinating Data Quality Engine, Tick Recorder, Universal Candle Builder,
Market Statistics Engine, Market State Engine, Event Detection Engine, and Storage Layer.
Provides a thread-safe Observer/Event Bus for real-time streaming notifications.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable

from goat.logging import get_logger
from goat.market_intelligence.candles.builder import UniversalCandleBuilder
from goat.market_intelligence.events.engine import EventDetectionEngine
from goat.market_intelligence.market_state.engine import MarketStateEngine
from goat.market_intelligence.models.candle import IntelligenceCandle, IntelligenceTimeframe
from goat.market_intelligence.models.event import MarketEvent
from goat.market_intelligence.models.market_state import MarketState
from goat.market_intelligence.models.quality import DataQualityCheckResult, DataQualityReport
from goat.market_intelligence.models.statistics import MarketStatistics
from goat.market_intelligence.models.tick import RecordedTick
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
from goat.market_intelligence.quality.engine import DataQualityEngine
from goat.market_intelligence.recorder.tick_recorder import TickRecorder
from goat.market_intelligence.statistics.engine import MarketStatisticsEngine

_log = get_logger("market_intelligence.engine")


class MasterMarketIntelligenceEngine:
    """Master Institutional Market Intelligence Engine with thread-safe Observer EventBus."""

    def __init__(
        self,
        db_path: str | Path | sqlite3.Connection | None = None,
        tick_repo: ITickRepository | None = None,
        candle_repo: ICandleRepository | None = None,
        stats_repo: IMarketStatisticsRepository | None = None,
        state_repo: IMarketStateRepository | None = None,
        event_repo: IEventRepository | None = None,
        quality_repo: IDataQualityRepository | None = None,
    ):
        # 1. Initialize Repositories (SQLite or In-Memory)
        if db_path is not None:
            self.conn = init_market_intelligence_db(db_path)
            self.tick_repo = tick_repo or SQLiteTickRepository(self.conn)
            self.candle_repo = candle_repo or SQLiteCandleRepository(self.conn)
            self.stats_repo = stats_repo or SQLiteMarketStatisticsRepository(self.conn)
            self.state_repo = state_repo or SQLiteMarketStateRepository(self.conn)
            self.event_repo = event_repo or SQLiteEventRepository(self.conn)
            self.quality_repo = quality_repo or SQLiteDataQualityRepository(self.conn)
        else:
            self.conn = None
            self.tick_repo = tick_repo or InMemoryTickRepository()
            self.candle_repo = candle_repo or InMemoryCandleRepository()
            self.stats_repo = stats_repo or InMemoryMarketStatisticsRepository()
            self.state_repo = state_repo or InMemoryMarketStateRepository()
            self.event_repo = event_repo or InMemoryEventRepository()
            self.quality_repo = quality_repo or InMemoryDataQualityRepository()

        # 2. Instantiate Component Engines
        self.quality_engine = DataQualityEngine(repository=self.quality_repo)
        self.recorder = TickRecorder(repository=self.tick_repo)
        self.candle_builder = UniversalCandleBuilder(
            repository=self.candle_repo,
            on_candle_finalized_callback=self._on_candle_finalized_internal,
        )
        self.statistics_engine = MarketStatisticsEngine(repository=self.stats_repo)
        self.market_state_engine = MarketStateEngine(repository=self.state_repo)
        self.event_detection_engine = EventDetectionEngine(repository=self.event_repo)

        # 3. Thread-Safe Observer / Event Bus Callbacks
        self._tick_listeners: list[Callable[[RecordedTick], None]] = []
        self._candle_listeners: list[Callable[[IntelligenceCandle], None]] = []
        self._stats_listeners: list[Callable[[MarketStatistics], None]] = []
        self._state_listeners: list[Callable[[MarketState], None]] = []
        self._event_listeners: list[Callable[[MarketEvent], None]] = []
        self._rejected_listeners: list[Callable[[DataQualityCheckResult], None]] = []
        self._bus_lock = threading.RLock()

    # --- Event Bus Subscription Methods ---

    def subscribe_ticks(self, callback: Callable[[RecordedTick], None]) -> None:
        with self._bus_lock:
            self._tick_listeners.append(callback)

    def subscribe_candles(self, callback: Callable[[IntelligenceCandle], None]) -> None:
        with self._bus_lock:
            self._candle_listeners.append(callback)

    def subscribe_statistics(self, callback: Callable[[MarketStatistics], None]) -> None:
        with self._bus_lock:
            self._stats_listeners.append(callback)

    def subscribe_states(self, callback: Callable[[MarketState], None]) -> None:
        with self._bus_lock:
            self._state_listeners.append(callback)

    def subscribe_events(self, callback: Callable[[MarketEvent], None]) -> None:
        with self._bus_lock:
            self._event_listeners.append(callback)

    def subscribe_rejected(self, callback: Callable[[DataQualityCheckResult], None]) -> None:
        with self._bus_lock:
            self._rejected_listeners.append(callback)

    # --- Core Processing Pipeline ---

    def process_raw_tick(self, raw_payload: dict[str, Any], arrival_latency_ms: float = 0.0) -> RecordedTick | None:
        """Master Ingestion Pipeline:
        1. Validate with Data Quality Engine
        2. If invalid, record quality metrics & notify listeners
        3. If valid, record tick with TickRecorder & save to TickRepository
        4. Update UniversalCandleBuilder across all 12 timeframes
        5. Update MarketStatisticsEngine (O(1) rolling calculations)
        6. Classify MarketState (Trend, Volatility, Momentum, Regime, Liquidity)
        7. Run EventDetectionEngine (Spikes, Crashes, Gaps, Extremes, Anomalies)
        8. Dispatch streaming updates to all EventBus subscribers
        """
        # 1. Quality Check
        check_res = self.quality_engine.evaluate_tick(raw_payload)
        if not check_res.passed:
            _log.warning("tick_rejected_by_data_quality_engine", symbol=check_res.symbol, issues=[i.reason.value for i in check_res.issues])
            with self._bus_lock:
                for cb in self._rejected_listeners:
                    try:
                        cb(check_res)
                    except Exception as exc:
                        _log.error("rejected_listener_exception", error=str(exc))
            return None

        # 2. Record Tick
        tick = self.recorder.record_raw_tick(raw_payload, arrival_latency_ms=arrival_latency_ms)

        # Notify Tick Subscribers
        with self._bus_lock:
            for cb in self._tick_listeners:
                try:
                    cb(tick)
                except Exception as exc:
                    _log.error("tick_listener_exception", error=str(exc))

        # 3. Update Multi-Timeframe Candle Builder
        finalized_candles = self.candle_builder.process_tick(tick)

        # 4. Compute Continuous Streaming Statistics
        stats = self.statistics_engine.process_tick(tick)

        with self._bus_lock:
            for cb in self._stats_listeners:
                try:
                    cb(stats)
                except Exception as exc:
                    _log.error("stats_listener_exception", error=str(exc))

        # 5. Classify Market State
        state = self.market_state_engine.classify_state(stats, current_tick=tick)

        with self._bus_lock:
            for cb in self._state_listeners:
                try:
                    cb(state)
                except Exception as exc:
                    _log.error("state_listener_exception", error=str(exc))

        # 6. Detect Tick & Stat Events
        events = self.event_detection_engine.process_tick(tick, current_stats=stats)
        events.extend(self.event_detection_engine.process_statistics(stats))

        for ev in events:
            with self._bus_lock:
                for cb in self._event_listeners:
                    try:
                        cb(ev)
                    except Exception as exc:
                        _log.error("event_listener_exception", error=str(exc))

        return tick

    def _on_candle_finalized_internal(self, candle: IntelligenceCandle) -> None:
        """Internal handler called when UniversalCandleBuilder completes a candle bar."""
        # Update statistics & event detection with finalized candle
        self.statistics_engine.process_candle(candle)
        c_events = self.event_detection_engine.process_candle(candle)

        # Notify Candle Subscribers
        with self._bus_lock:
            for cb in self._candle_listeners:
                try:
                    cb(candle)
                except Exception as exc:
                    _log.error("candle_listener_exception", error=str(exc))

        # Notify Event Subscribers for candle events
        for ev in c_events:
            with self._bus_lock:
                for cb in self._event_listeners:
                    try:
                        cb(ev)
                    except Exception as exc:
                        _log.error("event_listener_exception", error=str(exc))

    def generate_quality_report(self, symbol: str) -> DataQualityReport:
        """Generate audit report from DataQualityEngine."""
        return self.quality_engine.generate_report(symbol)

    def force_finalize(self) -> list[IntelligenceCandle]:
        """Force finalize all currently forming candles across all symbols and timeframes."""
        return self.candle_builder.force_finalize_all()


# Convenience alias matching prompt naming
MarketIntelligenceEngine = MasterMarketIntelligenceEngine
