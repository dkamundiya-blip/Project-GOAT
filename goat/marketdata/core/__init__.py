"""
Project GOAT v0.8 — Market Data Core Subpackage
"""

from goat.marketdata.core.canonical import (
    compute_candle_id,
    compute_gap_id,
    compute_replay_id,
    compute_report_id,
    compute_stream_id,
    compute_tick_id,
)
from goat.marketdata.core.enums import (
    DerivSymbol,
    GapReason,
    MarketTimeframe,
    SafetyGateStatus,
    StreamConnectionStatus,
)
from goat.marketdata.core.models import (
    MarketCandle,
    MarketGap,
    MarketStreamState,
    MarketTick,
    ReplaySnapshot,
)

__all__ = [
    # Enums
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
]
