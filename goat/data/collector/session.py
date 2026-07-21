"""
Project GOAT v0.2 — Collection Session Manager & Metrics

Orchestrates multi-symbol data collection sessions, integrating real-time validation,
storage persistence, duplicate tracking, and session summary reporting.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from goat.config import GoatSettings
from goat.data.collector.deriv import DerivMarketDataCollector
from goat.data.schemas import Tick
from goat.data.storage.parquet import ParquetStorage
from goat.data.validation.validators import ValidationReport, validate_ticks
from goat.logging import get_logger

_log = get_logger("collector.session")


class CollectionSessionManager:
    """Orchestrates live market-data collection session with metrics tracking.

    Args:
        collector: DerivMarketDataCollector instance.
        storage: Optional ParquetStorage instance.
        settings: Optional GoatSettings instance.
    """

    def __init__(
        self,
        collector: DerivMarketDataCollector,
        storage: ParquetStorage | None = None,
        settings: GoatSettings | None = None,
    ) -> None:
        self.collector = collector
        self.settings = settings or GoatSettings()
        self.storage = storage or ParquetStorage(
            raw_dir=self.settings.get_raw_data_dir(),
            processed_dir=self.settings.get_processed_data_dir(),
        )

        # Session Metrics
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None
        self.symbols_subscribed: list[str] = []
        self.tick_counts: dict[str, int] = {}
        self.last_tick_timestamps: dict[str, datetime] = {}
        self.records_written: int = 0
        self.duplicate_count: int = 0
        self.validation_report: ValidationReport = ValidationReport()

    async def run_session(
        self,
        symbols: list[str],
        duration_seconds: float | None = None,
    ) -> None:
        """Run collection session for specified symbols.

        Args:
            symbols: List of provider symbols to subscribe and collect (e.g. ``["R_10", "R_75"]``).
            duration_seconds: Run duration limit in seconds. If None, runs until cancelled.
        """
        self.start_time = datetime.now(timezone.utc)
        self.symbols_subscribed = list(symbols)
        for s in symbols:
            self.tick_counts[s] = 0

        _log.info(
            "collection_session_starting",
            symbols=symbols,
            duration=duration_seconds,
        )

        async with self.collector:
            # Subscribe to all symbols
            for s in symbols:
                await self.collector.subscribe_ticks(s)

            tasks = [
                asyncio.create_task(self._consume_symbol_ticks(s))
                for s in symbols
            ]

            try:
                if duration_seconds is not None:
                    await asyncio.sleep(duration_seconds)
                else:
                    await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                _log.info("collection_session_cancelled")
            finally:
                for t in tasks:
                    if not t.done():
                        t.cancel()
                self.end_time = datetime.now(timezone.utc)
                _log.info("collection_session_completed")

    async def _consume_symbol_ticks(self, symbol: str) -> None:
        """Consume incoming ticks for a symbol, validate, track, and store them."""
        start_t = datetime.now(timezone.utc)
        end_t = datetime.max.replace(tzinfo=timezone.utc)

        buffer: list[Tick] = []
        batch_size = 50

        try:
            async for tick in self.collector.collect_ticks(symbol, start_t, end_t):
                # 1. Update stats
                self.tick_counts[symbol] = self.tick_counts.get(symbol, 0) + 1
                self.last_tick_timestamps[symbol] = tick.timestamp

                # 2. Buffer for persistent batch storage
                buffer.append(tick)
                if len(buffer) >= batch_size:
                    df = pd.DataFrame([
                        {"symbol": t.symbol, "timestamp": t.timestamp, "price": float(t.price), "tick_id": t.tick_id}
                        for t in buffer
                    ])
                    report = validate_ticks(df)
                    if not report.is_valid:
                        self.duplicate_count += report.warning_count + report.error_count

                    written = self.storage.write_ticks(symbol, buffer)
                    self.records_written += written
                    buffer.clear()

        except asyncio.CancelledError:
            pass
        finally:
            if buffer:
                df = pd.DataFrame([
                    {"symbol": t.symbol, "timestamp": t.timestamp, "price": float(t.price), "tick_id": t.tick_id}
                    for t in buffer
                ])
                report = validate_ticks(df)
                if not report.is_valid:
                    self.duplicate_count += report.warning_count + report.error_count

                written = self.storage.write_ticks(symbol, buffer)
                self.records_written += written
                buffer.clear()

    def get_summary(self) -> dict[str, Any]:
        """Return structured session statistics summary dictionary."""
        now = datetime.now(timezone.utc)
        start = self.start_time or now
        end = self.end_time or now
        duration_sec = max((end - start).total_seconds(), 0.0)

        return {
            "session_start": start.isoformat(),
            "session_duration_seconds": round(duration_sec, 2),
            "symbols_subscribed": self.symbols_subscribed,
            "tick_counts_by_symbol": self.tick_counts,
            "total_ticks_received": sum(self.tick_counts.values()),
            "records_written": self.records_written,
            "duplicate_count": self.duplicate_count,
            "validation_issues": self.duplicate_count,
            "reconnect_count": self.collector.reconnect_count,
            "last_tick_timestamps": {
                s: dt.isoformat() for s, dt in self.last_tick_timestamps.items()
            },
        }

    def format_summary_text(self) -> str:
        """Format summary dictionary into clean human-readable text block."""
        s = self.get_summary()
        lines = [
            "==================================================",
            "PROJECT GOAT v0.2 — COLLECTION SESSION SUMMARY",
            "==================================================",
            f"Session Start      : {s['session_start']}",
            f"Duration (seconds) : {s['session_duration_seconds']}s",
            f"Symbols Subscribed : {', '.join(s['symbols_subscribed'])}",
            f"Total Ticks Recv   : {s['total_ticks_received']}",
            f"Records Persisted  : {s['records_written']}",
            f"Duplicates Detected: {s['duplicate_count']}",
            f"Validation Issues  : {s['validation_issues']}",
            f"Reconnect Count    : {s['reconnect_count']}",
            "--- Ticks by Symbol ---",
        ]
        for sym, count in s["tick_counts_by_symbol"].items():
            last_ts = s["last_tick_timestamps"].get(sym, "N/A")
            lines.append(f"  - {sym}: {count} ticks (last: {last_ts})")
        lines.append("==================================================")
        return "\n".join(lines)
