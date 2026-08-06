"""
Project GOAT v1.0 — Buffered Persistence Tick Writer

High-throughput, non-blocking batch persistence layer for LiveTick objects
into SQLite (future PostgreSQL compatible parameterized statements).
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from pathlib import Path
from typing import Sequence

from goat.market_data.models.tick import LiveTick


def init_live_market_data_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database for live market data with WAL journal mode."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS live_market_ticks (
                tick_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                bid REAL NOT NULL,
                ask REAL NOT NULL,
                spread REAL NOT NULL,
                epoch_timestamp INTEGER NOT NULL,
                arrival_timestamp TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                connection_id TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                checksum TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_live_ticks_symbol ON live_market_ticks (symbol);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_live_ticks_epoch ON live_market_ticks (epoch_timestamp);")
    return conn


class BufferedTickWriter:
    """Non-blocking batch tick persistence engine."""

    def __init__(
        self,
        db_conn: sqlite3.Connection | None = None,
        db_path: str | Path | None = None,
        batch_size: int = 50,
        flush_interval_seconds: float = 2.0,
    ):
        if db_conn:
            self.conn = db_conn
        elif db_path:
            self.conn = init_live_market_data_db(db_path)
        else:
            self.conn = init_live_market_data_db(":memory:")

        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        self._buffer: list[LiveTick] = []
        self._queue: asyncio.Queue[LiveTick] | None = None
        self._flush_task: asyncio.Task[None] | None = None
        self._running = False
        self._total_writes = 0
        self._last_flush_time = time.time()
        self._recent_writes_count = 0
        self._writes_per_sec = 0.0

    def write_tick_sync(self, tick: LiveTick) -> None:
        """Synchronously enqueue and flush tick if batch capacity reached."""
        self._buffer.append(tick)
        if len(self._buffer) >= self.batch_size:
            self.flush_sync()

    def flush_sync(self) -> int:
        """Synchronously write buffered ticks into database in a single transaction."""
        if not self._buffer:
            return 0

        ticks_to_write = list(self._buffer)
        self._buffer.clear()

        rows = [
            (
                t.tick_id,
                t.symbol,
                t.price,
                t.bid,
                t.ask,
                t.spread,
                t.epoch_timestamp,
                t.arrival_timestamp,
                t.sequence_number,
                t.connection_id,
                t.latency_ms,
                t.checksum,
                json.dumps(t.metadata, sort_keys=True),
                t.canonical_hash,
            )
            for t in ticks_to_write
        ]

        with self.conn:
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO live_market_ticks (
                    tick_id, symbol, price, bid, ask, spread, epoch_timestamp,
                    arrival_timestamp, sequence_number, connection_id, latency_ms,
                    checksum, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                rows,
            )

        count = len(rows)
        self._total_writes += count
        self._recent_writes_count += count
        now = time.time()
        elapsed = now - self._last_flush_time
        if elapsed >= 1.0:
            self._writes_per_sec = round(self._recent_writes_count / elapsed, 2)
            self._recent_writes_count = 0
            self._last_flush_time = now

        return count

    async def start(self) -> None:
        """Start async background flushing loop."""
        self._queue = asyncio.Queue()
        self._running = True
        self._flush_task = asyncio.create_task(self._background_flush_loop())

    async def stop(self) -> None:
        """Stop background flusher and perform final flush."""
        self._running = False
        if self._flush_task and not self._flush_task.done():
            self._flush_task.cancel()
            try:
                await self._flush_task
            except (asyncio.CancelledError, Exception):
                pass
        self.flush_sync()

    async def enqueue_tick_async(self, tick: LiveTick) -> None:
        """Enqueue tick asynchronously."""
        self._buffer.append(tick)
        if len(self._buffer) >= self.batch_size:
            self.flush_sync()

    async def _background_flush_loop(self) -> None:
        """Periodic background flush task."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval_seconds)
                self.flush_sync()
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def get_total_writes(self) -> int:
        """Total persisted tick count."""
        return self._total_writes

    def get_writes_per_second(self) -> float:
        """Recent database writes per second."""
        return self._writes_per_sec

    def get_buffer_size(self) -> int:
        """Current un-flushed buffer item count."""
        return len(self._buffer)

    def get_ticks_from_db(self, symbol: str, limit: int = 100) -> list[LiveTick]:
        """Fetch persisted LiveTicks from database."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT tick_id, symbol, price, bid, ask, spread, epoch_timestamp,
                   arrival_timestamp, sequence_number, connection_id, latency_ms,
                   checksum, metadata_json, canonical_hash
            FROM live_market_ticks
            WHERE symbol = ?
            ORDER BY sequence_number ASC
            LIMIT ?;
            """,
            (symbol.strip().upper(), limit),
        )
        rows = cursor.fetchall()
        return [
            LiveTick(
                tick_id=r[0],
                symbol=r[1],
                price=r[2],
                bid=r[3],
                ask=r[4],
                spread=r[5],
                epoch_timestamp=r[6],
                arrival_timestamp=r[7],
                sequence_number=r[8],
                connection_id=r[9],
                latency_ms=r[10],
                checksum=r[11],
                metadata=json.loads(r[12]),
                canonical_hash=r[13],
            )
            for r in rows
        ]
