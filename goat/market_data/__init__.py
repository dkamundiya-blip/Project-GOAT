"""
Project GOAT v1.0 — Institutional Market Data Ingestion Subsystem (`goat.market_data`)

Live Deriv streaming ingestion, tick normalization, buffered persistence,
connection resilience, operational telemetry, and REST endpoints.
"""

from goat.market_data.engine import LiveMarketDataIngestionEngine
from goat.market_data.models import (
    SUPPORTED_SYMBOLS,
    DerivSymbolConfig,
    LiveQuote,
    LiveTick,
    MarketCandle,
    MarketTimeframe,
    SymbolType,
    compute_live_tick_id,
    get_symbol_config,
)
from goat.market_data.normalization import (
    TickNormalizationResult,
    TickNormalizer,
    compute_latency_ms,
    epoch_to_iso,
    now_utc_iso,
)
from goat.market_data.persistence import (
    BufferedTickWriter,
    LiveTickBuffer,
    init_live_market_data_db,
)
from goat.market_data.telemetry import (
    IngestionMetricsCollector,
    IngestionTelemetrySnapshot,
    LatencySnapshot,
    LatencyTracker,
)
from goat.market_data.websocket import (
    DerivWebSocketClient,
    HeartbeatMonitor,
    ReconnectPolicy,
    ReconnectState,
    WebSocketManager,
)

__all__ = [
    "LiveMarketDataIngestionEngine",
    # Models
    "LiveTick",
    "compute_live_tick_id",
    "LiveQuote",
    "MarketCandle",
    "MarketTimeframe",
    "DerivSymbolConfig",
    "SymbolType",
    "SUPPORTED_SYMBOLS",
    "get_symbol_config",
    # Normalization
    "TickNormalizer",
    "TickNormalizationResult",
    "epoch_to_iso",
    "now_utc_iso",
    "compute_latency_ms",
    # Persistence
    "LiveTickBuffer",
    "BufferedTickWriter",
    "init_live_market_data_db",
    # Telemetry
    "LatencyTracker",
    "LatencySnapshot",
    "IngestionMetricsCollector",
    "IngestionTelemetrySnapshot",
    # WebSocket
    "DerivWebSocketClient",
    "HeartbeatMonitor",
    "ReconnectPolicy",
    "ReconnectState",
    "WebSocketManager",
]
