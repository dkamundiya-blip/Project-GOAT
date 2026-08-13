"""
Project GOAT v1.0 — Master Live Market Data Ingestion Engine

Central coordinator orchestrating:
- Live WebSocket Manager & Deriv Streaming Client
- Tick Normalization Engine (Deriv WS payload -> Canonical LiveTick)
- Sliding-window In-Memory Buffer (LiveTickBuffer)
- Multi-Timeframe Candle Aggregation Engine (LiveCandleBuilder)
- Buffered Persistence Engine (BufferedTickWriter -> SQLite)
- Operational Telemetry & Latency Monitoring
"""

from __future__ import annotations

import asyncio
import datetime
from pathlib import Path
from typing import Any

from goat.logging import get_logger
from goat.market_data.candles.builder import LiveCandleBuilder
from goat.market_data.models.candle import MarketCandle
from goat.market_data.models.quote import LiveQuote
from goat.market_data.models.symbol import SUPPORTED_SYMBOLS, DerivSymbolConfig, get_symbol_config
from goat.market_data.models.tick import LiveTick
from goat.market_data.normalization.tick_normalizer import TickNormalizer
from goat.market_data.persistence.buffer import LiveTickBuffer
from goat.market_data.persistence.tick_writer import BufferedTickWriter, init_live_market_data_db
from goat.market_data.telemetry.latency import LatencyTracker
from goat.market_data.telemetry.metrics import IngestionMetricsCollector, IngestionTelemetrySnapshot
from goat.market_data.websocket.websocket_manager import WebSocketManager

_log = get_logger("market_data.engine")


class LiveMarketDataIngestionEngine:
    """Master Institutional Market Data Ingestion Engine."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        ws_manager: WebSocketManager | None = None,
        autostart: bool = False,
    ):
        if isinstance(db_path, str) and db_path == ":memory:":
            self.db_path = ":memory:"
        else:
            self.db_path = Path(db_path) if db_path else Path("data/live_market_data.db")
            if not self.db_path.parent.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_conn = init_live_market_data_db(self.db_path)
        self.ws_manager = ws_manager or WebSocketManager()
        self.normalizer = TickNormalizer()
        self.buffer = LiveTickBuffer()
        self.candle_builder = LiveCandleBuilder(db_conn=self.db_conn)
        self.writer = BufferedTickWriter(db_conn=self.db_conn)
        self.metrics = IngestionMetricsCollector()
        self.latency_tracker = LatencyTracker()

        self._sequence_counters: dict[str, int] = {}
        self._is_running = False

        # Register raw tick handler from WebSocket
        self.ws_manager.set_on_tick_callback(self._on_raw_tick_received)

    async def start(self) -> None:
        """Start the ingestion engine and background flushing tasks."""
        if self._is_running:
            return
        _log.info("starting_live_market_data_ingestion_engine")
        self._is_running = True
        await self.writer.start()

    async def stop(self) -> None:
        """Stop the ingestion engine, disconnect WebSocket, and flush persistence queue."""
        if not self._is_running:
            return
        _log.info("stopping_live_market_data_ingestion_engine")
        self._is_running = False
        await self.ws_manager.disconnect()
        await self.writer.stop()
        _log.info("live_market_data_ingestion_engine_stopped")

    async def connect_feed(self) -> bool:
        """Connect WebSocket market data feed."""
        if not self._is_running:
            await self.start()
        return await self.ws_manager.connect()

    async def disconnect_feed(self) -> None:
        """Disconnect WebSocket feed while keeping engine alive."""
        await self.ws_manager.disconnect()

    async def reconnect_feed(self) -> bool:
        """Force reconnect WebSocket feed."""
        await self.disconnect_feed()
        await asyncio.sleep(0.5)
        return await self.connect_feed()

    async def subscribe(self, symbol_id: str) -> bool:
        """Subscribe to a symbol stream."""
        return await self.ws_manager.subscribe(symbol_id)

    async def unsubscribe(self, symbol_id: str) -> bool:
        """Unsubscribe from a symbol stream."""
        return await self.ws_manager.unsubscribe(symbol_id)

    async def subscribe_all(self) -> int:
        """Subscribe to all 8 supported symbols."""
        return await self.ws_manager.subscribe_all_supported()

    async def unsubscribe_all(self) -> int:
        """Unsubscribe from all active symbols."""
        return await self.ws_manager.unsubscribe_all()

    async def _on_raw_tick_received(self, raw_payload: dict[str, Any]) -> None:
        """Processing pipeline for every incoming raw tick payload."""

        # 1. Resolve Symbol & Sequence
        raw_sym = str(
            raw_payload.get("tick", {}).get("symbol", raw_payload.get("symbol", "UNKNOWN"))
            if isinstance(raw_payload.get("tick"), dict)
            else raw_payload.get("symbol", "UNKNOWN")
        ).strip()

        cfg = get_symbol_config(raw_sym)
        sym_id = cfg.symbol_id if cfg else raw_sym.upper()

        seq = self._sequence_counters.get(sym_id, 0) + 1

        # 2. Normalization
        norm_res = self.normalizer.normalize(
            raw_payload=raw_payload,
            sequence_number=seq,
        )

        if not norm_res.success or norm_res.tick is None:
            self.metrics.record_packet_dropped()
            _log.warning("tick_normalization_failed", reason=norm_res.rejection_reason)
            return

        tick: LiveTick = norm_res.tick
        self._sequence_counters[sym_id] = seq

        # 3. Latency & Telemetry Tracking
        self.latency_tracker.record_latency(sym_id, tick.latency_ms)

        # 4. In-Memory Tick Buffer
        self.buffer.append_tick(tick)

        # 5. Multi-Timeframe Candle Aggregation (1M, 5M, 15M, 30M, 1H, 4H, 1D)
        self.candle_builder.process_tick(tick)

        # 6. Non-Blocking Persistence Batching
        self.writer.write_tick_sync(tick)

    def get_symbol_quote(self, symbol_id: str) -> LiveQuote:
        """Get live quote snapshot for a symbol."""
        conn_status = self.ws_manager.connection_state
        return self.buffer.get_live_quote(symbol_id, connection_status=conn_status)

    def get_all_quotes(self) -> list[LiveQuote]:
        """Get live quote snapshots for all supported instruments."""
        conn_status = self.ws_manager.connection_state
        return self.buffer.get_all_quotes(connection_status=conn_status)

    def get_recent_ticks(self, symbol_id: str, limit: int = 100) -> list[LiveTick]:
        """Get recent ticks for symbol from buffer or DB fallback."""
        buffer_ticks = self.buffer.get_recent_ticks(symbol_id, limit=limit)
        if buffer_ticks:
            return buffer_ticks
        return self.writer.get_ticks_from_db(symbol_id, limit=limit)

    def get_latest_candle(self, symbol_id: str, timeframe: str = "1M") -> MarketCandle | None:
        """Get latest forming or completed candle for symbol and timeframe."""
        return self.candle_builder.get_latest_candle(symbol_id, timeframe=timeframe)

    def get_historical_candles(
        self, symbol_id: str, timeframe: str = "1M", limit: int = 100
    ) -> list[MarketCandle]:
        """Fetch historical completed candles for symbol and timeframe."""
        return self.candle_builder.get_historical_candles(symbol_id, timeframe=timeframe, limit=limit)

    def get_telemetry_snapshot(self) -> IngestionTelemetrySnapshot:
        """Get real-time operational telemetry snapshot for dashboard."""
        total_ticks = self.buffer.total_ticks_received
        lat_snap = self.latency_tracker.get_global_latency()

        # Calculate average ticks/sec
        all_quotes = self.get_all_quotes()
        ticks_per_sec = sum(q.tick_frequency for q in all_quotes)

        return self.metrics.snapshot(
            total_ticks=total_ticks,
            ticks_per_sec=ticks_per_sec,
            ws_connected_time=self.ws_manager.uptime_seconds,
            queue_size=0,
            buffer_size=self.writer.get_buffer_size(),
            db_writes_per_sec=self.writer.get_writes_per_second(),
            latency_snap=lat_snap,
        )
