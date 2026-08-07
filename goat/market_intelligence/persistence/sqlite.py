"""
Project GOAT Phase 4 — Production SQLite Storage Backend

Provides high-performance, indexed, thread-safe SQLite implementations of all Phase 4 repository interfaces.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import threading
from typing import Sequence

from goat.market_intelligence.models.candle import IntelligenceCandle, IntelligenceTimeframe
from goat.market_intelligence.models.event import IntelligenceEventType, MarketEvent
from goat.market_intelligence.models.market_state import (
    LiquidityLevel,
    MarketState,
    MomentumState,
    RegimeState,
    TrendState,
    VolatilityLevel,
)
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


def init_market_intelligence_db(conn_or_path: sqlite3.Connection | str | Path) -> sqlite3.Connection:
    """Initialize SQLite database tables and indices for Phase 4 Market Intelligence storage."""
    if isinstance(conn_or_path, (str, Path)):
        path_str = str(conn_or_path)
        if path_str != ":memory:":
            Path(path_str).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path_str, check_same_thread=False)
    else:
        conn = conn_or_path

    with conn:
        # 1. Ticks table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence_recorded_ticks (
                tick_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                bid REAL NOT NULL,
                ask REAL NOT NULL,
                mid_price REAL NOT NULL,
                spread REAL NOT NULL,
                latency_ms REAL NOT NULL,
                sequence_number INTEGER NOT NULL,
                source TEXT NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_ticks_sym_ts ON intelligence_recorded_ticks (symbol, timestamp);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_ticks_seq ON intelligence_recorded_ticks (symbol, sequence_number);")

        # 2. Candles table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence_candles (
                candle_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                open_timestamp TEXT NOT NULL,
                close_timestamp TEXT NOT NULL,
                completed INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_candles_sym_tf ON intelligence_candles (symbol, timeframe);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_candles_open_ts ON intelligence_candles (open_timestamp);")

        # 3. Market Statistics table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence_market_statistics (
                stat_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                window_size INTEGER NOT NULL,
                atr REAL NOT NULL,
                true_range REAL NOT NULL,
                rolling_volatility REAL NOT NULL,
                standard_deviation REAL NOT NULL,
                variance REAL NOT NULL,
                average_tick_rate REAL NOT NULL,
                average_candle_size REAL NOT NULL,
                mean_spread REAL NOT NULL,
                min_spread REAL NOT NULL,
                max_spread REAL NOT NULL,
                spread_variance REAL NOT NULL,
                market_speed REAL NOT NULL,
                rolling_high REAL NOT NULL,
                rolling_low REAL NOT NULL,
                rolling_vwap REAL NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_stats_sym_ts ON intelligence_market_statistics (symbol, timestamp);")

        # 4. Market States table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence_market_states (
                state_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                trend TEXT NOT NULL,
                volatility TEXT NOT NULL,
                momentum TEXT NOT NULL,
                regime TEXT NOT NULL,
                liquidity TEXT NOT NULL,
                trend_score REAL NOT NULL,
                volatility_score REAL NOT NULL,
                momentum_score REAL NOT NULL,
                liquidity_score REAL NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_states_sym_ts ON intelligence_market_states (symbol, timestamp);")

        # 5. Events table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence_events (
                event_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_events_sym_type ON intelligence_events (symbol, event_type);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_events_ts ON intelligence_events (timestamp);")

        # 6. Data Quality Reports table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence_quality_reports (
                report_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                total_ticks_checked INTEGER NOT NULL,
                valid_ticks_count INTEGER NOT NULL,
                rejected_ticks_count INTEGER NOT NULL,
                pass_rate REAL NOT NULL,
                issues_breakdown_json TEXT NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_intel_quality_sym_ts ON intelligence_quality_reports (symbol, timestamp);")

    return conn


class SQLiteTickRepository(ITickRepository):
    """SQLite implementation of ITickRepository."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    def save_tick(self, tick: RecordedTick) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_recorded_ticks (
                    tick_id, symbol, timestamp, bid, ask, mid_price, spread, latency_ms,
                    sequence_number, source, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    tick.tick_id,
                    tick.symbol,
                    tick.timestamp,
                    tick.bid,
                    tick.ask,
                    tick.mid_price,
                    tick.spread,
                    tick.latency_ms,
                    tick.sequence_number,
                    tick.source,
                    tick.checksum,
                    json.dumps(tick.metadata, sort_keys=True),
                    tick.canonical_hash,
                ),
            )

    def save_ticks(self, ticks: Sequence[RecordedTick]) -> None:
        if not ticks:
            return
        data = [
            (
                t.tick_id,
                t.symbol,
                t.timestamp,
                t.bid,
                t.ask,
                t.mid_price,
                t.spread,
                t.latency_ms,
                t.sequence_number,
                t.source,
                t.checksum,
                json.dumps(t.metadata, sort_keys=True),
                t.canonical_hash,
            )
            for t in ticks
        ]
        with self._lock, self.conn:
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO intelligence_recorded_ticks (
                    tick_id, symbol, timestamp, bid, ask, mid_price, spread, latency_ms,
                    sequence_number, source, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                data,
            )

    def get_recent_ticks(self, symbol: str, limit: int = 100) -> list[RecordedTick]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT tick_id, symbol, timestamp, bid, ask, mid_price, spread, latency_ms,
                       sequence_number, source, checksum, metadata_json, canonical_hash
                FROM (
                    SELECT tick_id, symbol, timestamp, bid, ask, mid_price, spread, latency_ms,
                           sequence_number, source, checksum, metadata_json, canonical_hash
                    FROM intelligence_recorded_ticks
                    WHERE symbol = ?
                    ORDER BY sequence_number DESC, timestamp DESC
                    LIMIT ?
                ) ORDER BY sequence_number ASC, timestamp ASC;
                """,
                (symbol.upper(), limit),
            )
            rows = cursor.fetchall()
            return [
                RecordedTick(
                    tick_id=r[0],
                    symbol=r[1],
                    timestamp=r[2],
                    bid=r[3],
                    ask=r[4],
                    mid_price=r[5],
                    spread=r[6],
                    latency_ms=r[7],
                    sequence_number=r[8],
                    source=r[9],
                    checksum=r[10],
                    metadata=json.loads(r[11]),
                    canonical_hash=r[12],
                )
                for r in rows
            ]

    def get_ticks_range(self, symbol: str, start_iso: str, end_iso: str) -> list[RecordedTick]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT tick_id, symbol, timestamp, bid, ask, mid_price, spread, latency_ms,
                       sequence_number, source, checksum, metadata_json, canonical_hash
                FROM intelligence_recorded_ticks
                WHERE symbol = ? AND timestamp >= ? AND timestamp <= ?
                ORDER BY sequence_number ASC, timestamp ASC;
                """,
                (symbol.upper(), start_iso, end_iso),
            )
            rows = cursor.fetchall()
            return [
                RecordedTick(
                    tick_id=r[0],
                    symbol=r[1],
                    timestamp=r[2],
                    bid=r[3],
                    ask=r[4],
                    mid_price=r[5],
                    spread=r[6],
                    latency_ms=r[7],
                    sequence_number=r[8],
                    source=r[9],
                    checksum=r[10],
                    metadata=json.loads(r[11]),
                    canonical_hash=r[12],
                )
                for r in rows
            ]

    def get_latest_tick(self, symbol: str) -> RecordedTick | None:
        ticks = self.get_recent_ticks(symbol, limit=1)
        return ticks[0] if ticks else None

    def count(self, symbol: str | None = None) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            if symbol:
                cursor.execute("SELECT COUNT(*) FROM intelligence_recorded_ticks WHERE symbol = ?;", (symbol.upper(),))
            else:
                cursor.execute("SELECT COUNT(*) FROM intelligence_recorded_ticks;")
            return cursor.fetchone()[0]


class SQLiteCandleRepository(ICandleRepository):
    """SQLite implementation of ICandleRepository."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    def save_candle(self, candle: IntelligenceCandle) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_candles (
                    candle_id, symbol, timeframe, open, high, low, close, volume,
                    open_timestamp, close_timestamp, completed, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    candle.candle_id,
                    candle.symbol,
                    candle.timeframe.value,
                    candle.open,
                    candle.high,
                    candle.low,
                    candle.close,
                    candle.volume,
                    candle.open_timestamp,
                    candle.close_timestamp,
                    1 if candle.completed else 0,
                    candle.checksum,
                    json.dumps(candle.metadata, sort_keys=True),
                    candle.canonical_hash,
                ),
            )

    def save_candles(self, candles: Sequence[IntelligenceCandle]) -> None:
        if not candles:
            return
        data = [
            (
                c.candle_id,
                c.symbol,
                c.timeframe.value,
                c.open,
                c.high,
                c.low,
                c.close,
                c.volume,
                c.open_timestamp,
                c.close_timestamp,
                1 if c.completed else 0,
                c.checksum,
                json.dumps(c.metadata, sort_keys=True),
                c.canonical_hash,
            )
            for c in candles
        ]
        with self._lock, self.conn:
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO intelligence_candles (
                    candle_id, symbol, timeframe, open, high, low, close, volume,
                    open_timestamp, close_timestamp, completed, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                data,
            )

    def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> list[IntelligenceCandle]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT candle_id, symbol, timeframe, open, high, low, close, volume,
                       open_timestamp, close_timestamp, completed, checksum, metadata_json, canonical_hash
                FROM (
                    SELECT candle_id, symbol, timeframe, open, high, low, close, volume,
                           open_timestamp, close_timestamp, completed, checksum, metadata_json, canonical_hash
                    FROM intelligence_candles
                    WHERE symbol = ? AND timeframe = ?
                    ORDER BY open_timestamp DESC
                    LIMIT ?
                ) ORDER BY open_timestamp ASC;
                """,
                (symbol.upper(), timeframe.lower(), limit),
            )
            rows = cursor.fetchall()
            return [
                IntelligenceCandle(
                    candle_id=r[0],
                    symbol=r[1],
                    timeframe=IntelligenceTimeframe(r[2]),
                    open=r[3],
                    high=r[4],
                    low=r[5],
                    close=r[6],
                    volume=r[7],
                    open_timestamp=r[8],
                    close_timestamp=r[9],
                    completed=bool(r[10]),
                    checksum=r[11],
                    metadata=json.loads(r[12]),
                    canonical_hash=r[13],
                )
                for r in rows
            ]

    def get_latest_candle(self, symbol: str, timeframe: str) -> IntelligenceCandle | None:
        candles = self.get_candles(symbol, timeframe, limit=1)
        return candles[0] if candles else None

    def count(self, symbol: str | None = None, timeframe: str | None = None) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            if symbol and timeframe:
                cursor.execute("SELECT COUNT(*) FROM intelligence_candles WHERE symbol = ? AND timeframe = ?;", (symbol.upper(), timeframe.lower()))
            elif symbol:
                cursor.execute("SELECT COUNT(*) FROM intelligence_candles WHERE symbol = ?;", (symbol.upper(),))
            else:
                cursor.execute("SELECT COUNT(*) FROM intelligence_candles;")
            return cursor.fetchone()[0]


class SQLiteMarketStatisticsRepository(IMarketStatisticsRepository):
    """SQLite implementation of IMarketStatisticsRepository."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    def save_statistics(self, stats: MarketStatistics) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_market_statistics (
                    stat_id, symbol, timestamp, window_size, atr, true_range, rolling_volatility,
                    standard_deviation, variance, average_tick_rate, average_candle_size, mean_spread,
                    min_spread, max_spread, spread_variance, market_speed, rolling_high, rolling_low,
                    rolling_vwap, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    stats.stat_id,
                    stats.symbol,
                    stats.timestamp,
                    stats.window_size,
                    stats.atr,
                    stats.true_range,
                    stats.rolling_volatility,
                    stats.standard_deviation,
                    stats.variance,
                    stats.average_tick_rate,
                    stats.average_candle_size,
                    stats.mean_spread,
                    stats.min_spread,
                    stats.max_spread,
                    stats.spread_variance,
                    stats.market_speed,
                    stats.rolling_high,
                    stats.rolling_low,
                    stats.rolling_vwap,
                    stats.checksum,
                    json.dumps(stats.metadata, sort_keys=True),
                    stats.canonical_hash,
                ),
            )

    def get_recent_statistics(self, symbol: str, limit: int = 50) -> list[MarketStatistics]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT stat_id, symbol, timestamp, window_size, atr, true_range, rolling_volatility,
                       standard_deviation, variance, average_tick_rate, average_candle_size, mean_spread,
                       min_spread, max_spread, spread_variance, market_speed, rolling_high, rolling_low,
                       rolling_vwap, checksum, metadata_json, canonical_hash
                FROM (
                    SELECT stat_id, symbol, timestamp, window_size, atr, true_range, rolling_volatility,
                           standard_deviation, variance, average_tick_rate, average_candle_size, mean_spread,
                           min_spread, max_spread, spread_variance, market_speed, rolling_high, rolling_low,
                           rolling_vwap, checksum, metadata_json, canonical_hash
                    FROM intelligence_market_statistics
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ) ORDER BY timestamp ASC;
                """,
                (symbol.upper(), limit),
            )
            rows = cursor.fetchall()
            return [
                MarketStatistics(
                    stat_id=r[0],
                    symbol=r[1],
                    timestamp=r[2],
                    window_size=r[3],
                    atr=r[4],
                    true_range=r[5],
                    rolling_volatility=r[6],
                    standard_deviation=r[7],
                    variance=r[8],
                    average_tick_rate=r[9],
                    average_candle_size=r[10],
                    mean_spread=r[11],
                    min_spread=r[12],
                    max_spread=r[13],
                    spread_variance=r[14],
                    market_speed=r[15],
                    rolling_high=r[16],
                    rolling_low=r[17],
                    rolling_vwap=r[18],
                    checksum=r[19],
                    metadata=json.loads(r[20]),
                    canonical_hash=r[21],
                )
                for r in rows
            ]

    def get_latest_statistics(self, symbol: str) -> MarketStatistics | None:
        stats = self.get_recent_statistics(symbol, limit=1)
        return stats[0] if stats else None


class SQLiteMarketStateRepository(IMarketStateRepository):
    """SQLite implementation of IMarketStateRepository."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    def save_state(self, state: MarketState) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_market_states (
                    state_id, symbol, timestamp, trend, volatility, momentum, regime, liquidity,
                    trend_score, volatility_score, momentum_score, liquidity_score, checksum,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    state.state_id,
                    state.symbol,
                    state.timestamp,
                    state.trend.value,
                    state.volatility.value,
                    state.momentum.value,
                    state.regime.value,
                    state.liquidity.value,
                    state.trend_score,
                    state.volatility_score,
                    state.momentum_score,
                    state.liquidity_score,
                    state.checksum,
                    json.dumps(state.metadata, sort_keys=True),
                    state.canonical_hash,
                ),
            )

    def get_recent_states(self, symbol: str, limit: int = 50) -> list[MarketState]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT state_id, symbol, timestamp, trend, volatility, momentum, regime, liquidity,
                       trend_score, volatility_score, momentum_score, liquidity_score, checksum,
                       metadata_json, canonical_hash
                FROM (
                    SELECT state_id, symbol, timestamp, trend, volatility, momentum, regime, liquidity,
                           trend_score, volatility_score, momentum_score, liquidity_score, checksum,
                           metadata_json, canonical_hash
                    FROM intelligence_market_states
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ) ORDER BY timestamp ASC;
                """,
                (symbol.upper(), limit),
            )
            rows = cursor.fetchall()
            return [
                MarketState(
                    state_id=r[0],
                    symbol=r[1],
                    timestamp=r[2],
                    trend=TrendState(r[3]),
                    volatility=VolatilityLevel(r[4]),
                    momentum=MomentumState(r[5]),
                    regime=RegimeState(r[6]),
                    liquidity=LiquidityLevel(r[7]),
                    trend_score=r[8],
                    volatility_score=r[9],
                    momentum_score=r[10],
                    liquidity_score=r[11],
                    checksum=r[12],
                    metadata=json.loads(r[13]),
                    canonical_hash=r[14],
                )
                for r in rows
            ]

    def get_latest_state(self, symbol: str) -> MarketState | None:
        states = self.get_recent_states(symbol, limit=1)
        return states[0] if states else None


class SQLiteEventRepository(IEventRepository):
    """SQLite implementation of IEventRepository."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    def save_event(self, event: MarketEvent) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_events (
                    event_id, symbol, timestamp, event_type, confidence, checksum,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event.event_id,
                    event.symbol,
                    event.timestamp,
                    event.event_type.value,
                    event.confidence,
                    event.checksum,
                    json.dumps(event.metadata, sort_keys=True),
                    event.canonical_hash,
                ),
            )

    def get_recent_events(self, symbol: str | None = None, limit: int = 50) -> list[MarketEvent]:
        with self._lock:
            cursor = self.conn.cursor()
            if symbol:
                cursor.execute(
                    """
                    SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                    FROM (
                        SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                        FROM intelligence_events
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ) ORDER BY timestamp ASC;
                    """,
                    (symbol.upper(), limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                    FROM (
                        SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                        FROM intelligence_events
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ) ORDER BY timestamp ASC;
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [
                MarketEvent(
                    event_id=r[0],
                    symbol=r[1],
                    timestamp=r[2],
                    event_type=IntelligenceEventType(r[3]),
                    confidence=r[4],
                    checksum=r[5],
                    metadata=json.loads(r[6]),
                    canonical_hash=r[7],
                )
                for r in rows
            ]

    def get_events_by_type(self, event_type: str, symbol: str | None = None, limit: int = 50) -> list[MarketEvent]:
        with self._lock:
            cursor = self.conn.cursor()
            ev_str = str(event_type).upper()
            if symbol:
                cursor.execute(
                    """
                    SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                    FROM (
                        SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                        FROM intelligence_events
                        WHERE event_type = ? AND symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ) ORDER BY timestamp ASC;
                    """,
                    (ev_str, symbol.upper(), limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                    FROM (
                        SELECT event_id, symbol, timestamp, event_type, confidence, checksum, metadata_json, canonical_hash
                        FROM intelligence_events
                        WHERE event_type = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ) ORDER BY timestamp ASC;
                    """,
                    (ev_str, limit),
                )
            rows = cursor.fetchall()
            return [
                MarketEvent(
                    event_id=r[0],
                    symbol=r[1],
                    timestamp=r[2],
                    event_type=IntelligenceEventType(r[3]),
                    confidence=r[4],
                    checksum=r[5],
                    metadata=json.loads(r[6]),
                    canonical_hash=r[7],
                )
                for r in rows
            ]


class SQLiteDataQualityRepository(IDataQualityRepository):
    """SQLite implementation of IDataQualityRepository."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    def save_report(self, report: DataQualityReport) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_quality_reports (
                    report_id, symbol, timestamp, total_ticks_checked, valid_ticks_count,
                    rejected_ticks_count, pass_rate, issues_breakdown_json, checksum,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    report.report_id,
                    report.symbol,
                    report.timestamp,
                    report.total_ticks_checked,
                    report.valid_ticks_count,
                    report.rejected_ticks_count,
                    report.pass_rate,
                    json.dumps(report.issues_breakdown, sort_keys=True),
                    report.checksum,
                    json.dumps(report.metadata, sort_keys=True),
                    report.canonical_hash,
                ),
            )

    def get_recent_reports(self, symbol: str | None = None, limit: int = 50) -> list[DataQualityReport]:
        with self._lock:
            cursor = self.conn.cursor()
            if symbol:
                cursor.execute(
                    """
                    SELECT report_id, symbol, timestamp, total_ticks_checked, valid_ticks_count,
                           rejected_ticks_count, pass_rate, issues_breakdown_json, checksum, metadata_json, canonical_hash
                    FROM (
                        SELECT report_id, symbol, timestamp, total_ticks_checked, valid_ticks_count,
                               rejected_ticks_count, pass_rate, issues_breakdown_json, checksum, metadata_json, canonical_hash
                        FROM intelligence_quality_reports
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ) ORDER BY timestamp ASC;
                    """,
                    (symbol.upper(), limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT report_id, symbol, timestamp, total_ticks_checked, valid_ticks_count,
                           rejected_ticks_count, pass_rate, issues_breakdown_json, checksum, metadata_json, canonical_hash
                    FROM (
                        SELECT report_id, symbol, timestamp, total_ticks_checked, valid_ticks_count,
                               rejected_ticks_count, pass_rate, issues_breakdown_json, checksum, metadata_json, canonical_hash
                        FROM intelligence_quality_reports
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ) ORDER BY timestamp ASC;
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [
                DataQualityReport(
                    report_id=r[0],
                    symbol=r[1],
                    timestamp=r[2],
                    total_ticks_checked=r[3],
                    valid_ticks_count=r[4],
                    rejected_ticks_count=r[5],
                    pass_rate=r[6],
                    issues_breakdown=json.loads(r[7]),
                    checksum=r[8],
                    metadata=json.loads(r[9]),
                    canonical_hash=r[10],
                )
                for r in rows
            ]
