"""
Project GOAT v0.8 — Market Data Persistence Repositories

Provides SQLite repositories enforcing foreign keys (PRAGMA foreign_keys = ON),
round-trip serialization, and query methods for:
- MarketTickRepository
- MarketCandleRepository
- MarketStreamRepository
- MarketGapRepository
- ReplaySnapshotRepository
- MarketReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Sequence

from goat.marketdata.core.enums import GapReason, MarketTimeframe, StreamConnectionStatus
from goat.marketdata.core.models import (
    MarketCandle,
    MarketGap,
    MarketStreamState,
    MarketTick,
    ReplaySnapshot,
)


def init_marketdata_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database for Market Data subsystem with PRAGMA foreign_keys = ON."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_ticks (
                tick_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                broker TEXT NOT NULL,
                bid REAL NOT NULL,
                ask REAL NOT NULL,
                spread REAL NOT NULL,
                timestamp TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                source_latency REAL NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_candles (
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_stream_states (
                stream_id TEXT PRIMARY KEY,
                broker TEXT NOT NULL,
                symbol TEXT NOT NULL,
                connection_status TEXT NOT NULL,
                heartbeat_timestamp TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                packets_received INTEGER NOT NULL,
                packets_dropped INTEGER NOT NULL,
                reconnect_count INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_gaps (
                gap_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                start_timestamp TEXT NOT NULL,
                end_timestamp TEXT NOT NULL,
                missing_packets INTEGER NOT NULL,
                reason TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS replay_snapshots (
                replay_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                replay_timestamp TEXT NOT NULL,
                replay_checksum TEXT NOT NULL,
                snapshot_reference TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                markdown_content TEXT NOT NULL,
                json_content TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
    return conn


class MarketTickRepository:
    """SQLite repository for MarketTick persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, tick: MarketTick) -> None:
        """Insert or replace MarketTick in SQLite database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_ticks (
                    tick_id, symbol, broker, bid, ask, spread, timestamp,
                    sequence_number, source_latency, checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    tick.tick_id,
                    tick.symbol,
                    tick.broker,
                    tick.bid,
                    tick.ask,
                    tick.spread,
                    tick.timestamp,
                    tick.sequence_number,
                    tick.source_latency,
                    tick.checksum,
                    json.dumps(tick.metadata, sort_keys=True),
                    tick.canonical_hash,
                ),
            )

    def get_by_id(self, tick_id: str) -> MarketTick | None:
        """Fetch MarketTick by tick_id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM market_ticks WHERE tick_id = ?;", (tick_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return MarketTick(
            tick_id=row[0],
            symbol=row[1],
            broker=row[2],
            bid=row[3],
            ask=row[4],
            spread=row[5],
            timestamp=row[6],
            sequence_number=row[7],
            source_latency=row[8],
            checksum=row[9],
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )

    def get_by_symbol(self, symbol: str, limit: int = 100) -> list[MarketTick]:
        """Fetch recent MarketTicks by symbol."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM market_ticks WHERE symbol = ? ORDER BY sequence_number ASC LIMIT ?;",
            (symbol.strip().upper(), limit),
        )
        rows = cursor.fetchall()
        return [
            MarketTick(
                tick_id=r[0],
                symbol=r[1],
                broker=r[2],
                bid=r[3],
                ask=r[4],
                spread=r[5],
                timestamp=r[6],
                sequence_number=r[7],
                source_latency=r[8],
                checksum=r[9],
                metadata=json.loads(r[10]),
                canonical_hash=r[11],
            )
            for r in rows
        ]


class MarketCandleRepository:
    """SQLite repository for MarketCandle persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, candle: MarketCandle) -> None:
        """Insert or replace MarketCandle in SQLite database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_candles (
                    candle_id, symbol, timeframe, open, high, low, close,
                    volume, open_timestamp, close_timestamp, completed, checksum, metadata_json, canonical_hash
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

    def get_by_id(self, candle_id: str) -> MarketCandle | None:
        """Fetch MarketCandle by candle_id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM market_candles WHERE candle_id = ?;", (candle_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return MarketCandle(
            candle_id=row[0],
            symbol=row[1],
            timeframe=MarketTimeframe(row[2]),
            open=row[3],
            high=row[4],
            low=row[5],
            close=row[6],
            volume=row[7],
            open_timestamp=row[8],
            close_timestamp=row[9],
            completed=bool(row[10]),
            checksum=row[11],
            metadata=json.loads(row[12]),
            canonical_hash=row[13],
        )


class MarketStreamRepository:
    """SQLite repository for MarketStreamState persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, stream: MarketStreamState) -> None:
        """Insert or replace MarketStreamState."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_stream_states (
                    stream_id, broker, symbol, connection_status, heartbeat_timestamp,
                    latency_ms, packets_received, packets_dropped, reconnect_count, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    stream.stream_id,
                    stream.broker,
                    stream.symbol,
                    stream.connection_status.value,
                    stream.heartbeat_timestamp,
                    stream.latency_ms,
                    stream.packets_received,
                    stream.packets_dropped,
                    stream.reconnect_count,
                    json.dumps(stream.metadata, sort_keys=True),
                    stream.canonical_hash,
                ),
            )

    def get_by_id(self, stream_id: str) -> MarketStreamState | None:
        """Fetch MarketStreamState by stream_id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM market_stream_states WHERE stream_id = ?;", (stream_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return MarketStreamState(
            stream_id=row[0],
            broker=row[1],
            symbol=row[2],
            connection_status=StreamConnectionStatus(row[3]),
            heartbeat_timestamp=row[4],
            latency_ms=row[5],
            packets_received=row[6],
            packets_dropped=row[7],
            reconnect_count=row[8],
            metadata=json.loads(row[9]),
            canonical_hash=row[10],
        )


class MarketGapRepository:
    """SQLite repository for MarketGap persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, gap: MarketGap) -> None:
        """Insert or replace MarketGap."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_gaps (
                    gap_id, symbol, start_timestamp, end_timestamp,
                    missing_packets, reason, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    gap.gap_id,
                    gap.symbol,
                    gap.start_timestamp,
                    gap.end_timestamp,
                    gap.missing_packets,
                    gap.reason.value,
                    json.dumps(gap.metadata, sort_keys=True),
                    gap.canonical_hash,
                ),
            )

    def get_by_id(self, gap_id: str) -> MarketGap | None:
        """Fetch MarketGap by gap_id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM market_gaps WHERE gap_id = ?;", (gap_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return MarketGap(
            gap_id=row[0],
            symbol=row[1],
            start_timestamp=row[2],
            end_timestamp=row[3],
            missing_packets=row[4],
            reason=GapReason(row[5]),
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class ReplaySnapshotRepository:
    """SQLite repository for ReplaySnapshot persistence."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, snapshot: ReplaySnapshot) -> None:
        """Insert or replace ReplaySnapshot."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO replay_snapshots (
                    replay_id, symbol, replay_timestamp, replay_checksum,
                    snapshot_reference, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    snapshot.replay_id,
                    snapshot.symbol,
                    snapshot.replay_timestamp,
                    snapshot.replay_checksum,
                    snapshot.snapshot_reference,
                    json.dumps(snapshot.metadata, sort_keys=True),
                    snapshot.canonical_hash,
                ),
            )

    def get_by_id(self, replay_id: str) -> ReplaySnapshot | None:
        """Fetch ReplaySnapshot by replay_id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM replay_snapshots WHERE replay_id = ?;", (replay_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return ReplaySnapshot(
            replay_id=row[0],
            symbol=row[1],
            replay_timestamp=row[2],
            replay_checksum=row[3],
            snapshot_reference=row[4],
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class MarketReportRepository:
    """SQLite repository for storing generated MarketData reports."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_report(
        self,
        report_id: str,
        report_type: str,
        symbol: str,
        timestamp: str,
        markdown_content: str,
        json_content: str,
        canonical_hash: str,
    ) -> None:
        """Save a market report record."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_reports (
                    report_id, report_type, symbol, timestamp, markdown_content, json_content, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    report_id,
                    report_type,
                    symbol,
                    timestamp,
                    markdown_content,
                    json_content,
                    canonical_hash,
                ),
            )
