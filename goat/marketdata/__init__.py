"""
Project GOAT v0.8 — Live Market Data Infrastructure Package (`goat.marketdata`)

Step 7.0 Reference Package for live tick streaming, structure normalization,
stream telemetry, validation rules, gap detection, deterministic replay,
production safety gate, reporting, and SQLite persistence.
"""

from goat.marketdata.core import (
    DerivSymbol,
    GapReason,
    MarketCandle,
    MarketGap,
    MarketStreamState,
    MarketTick,
    MarketTimeframe,
    ReplaySnapshot,
    SafetyGateStatus,
    StreamConnectionStatus,
    compute_candle_id,
    compute_gap_id,
    compute_replay_id,
    compute_report_id,
    compute_stream_id,
    compute_tick_id,
)
from goat.marketdata.engine import LiveMarketDataEngine, ProcessTickOutput
from goat.marketdata.gap import MarketGapDetectionEngine
from goat.marketdata.ingestion import IngestionResult, MarketIngestionEngine
from goat.marketdata.persistence import (
    MarketCandleRepository,
    MarketGapRepository,
    MarketReportRepository,
    MarketStreamRepository,
    MarketTickRepository,
    ReplaySnapshotRepository,
    init_marketdata_db,
)
from goat.marketdata.replay import MarketReplayEngine, ReplayResult
from goat.marketdata.reporting import (
    MarketCandleReport,
    MarketDataExecutiveReport,
    MarketGapReport,
    MarketStreamReport,
    MarketTickReport,
    ReplaySnapshotReport,
)
from goat.marketdata.safety import MarketStreamSafetyGate, SafetyGateResult
from goat.marketdata.storage import MarketDataBuffer
from goat.marketdata.stream import MarketStreamEngine
from goat.marketdata.validation import MarketValidationEngine, ValidationResult

__all__ = [
    # Core Enums
    "StreamConnectionStatus",
    "MarketTimeframe",
    "GapReason",
    "SafetyGateStatus",
    "DerivSymbol",
    # Core Models
    "MarketTick",
    "MarketCandle",
    "MarketStreamState",
    "MarketGap",
    "ReplaySnapshot",
    # Canonical Hashing & Identifiers
    "compute_tick_id",
    "compute_candle_id",
    "compute_stream_id",
    "compute_gap_id",
    "compute_replay_id",
    "compute_report_id",
    # Engines & Coordinators
    "LiveMarketDataEngine",
    "ProcessTickOutput",
    "MarketIngestionEngine",
    "IngestionResult",
    "MarketStreamEngine",
    "MarketValidationEngine",
    "ValidationResult",
    "MarketGapDetectionEngine",
    "MarketReplayEngine",
    "ReplayResult",
    "MarketStreamSafetyGate",
    "SafetyGateResult",
    # Storage & Persistence
    "MarketDataBuffer",
    "init_marketdata_db",
    "MarketTickRepository",
    "MarketCandleRepository",
    "MarketStreamRepository",
    "MarketGapRepository",
    "ReplaySnapshotRepository",
    "MarketReportRepository",
    # Reporting Models
    "MarketTickReport",
    "MarketCandleReport",
    "MarketStreamReport",
    "MarketGapReport",
    "ReplaySnapshotReport",
    "MarketDataExecutiveReport",
]
