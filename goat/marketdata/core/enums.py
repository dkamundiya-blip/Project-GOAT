"""
Project GOAT v0.8 — Core Enums for Live Market Data Infrastructure

Defines deterministic enums for stream state, timeframes, gap reasons,
and safety gate status.
"""

from enum import Enum


class StreamConnectionStatus(str, Enum):
    """Status of live data feed stream connection."""

    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"
    DEGRADED = "DEGRADED"
    TERMINATED = "TERMINATED"


class MarketTimeframe(str, Enum):
    """Supported market aggregation timeframes."""

    TICK = "TICK"
    S1 = "1S"
    M1 = "1M"
    M5 = "5M"
    M15 = "15M"
    H1 = "1H"
    D1 = "1D"


class GapReason(str, Enum):
    """Reason for detected market data gap."""

    SEQUENCE_DISCONTINUITY = "SEQUENCE_DISCONTINUITY"
    TIMESTAMP_JUMP = "TIMESTAMP_JUMP"
    CONNECTION_LOST = "CONNECTION_LOST"
    HEARTBEAT_TIMEOUT = "HEARTBEAT_TIMEOUT"
    REPLAY_DISCONTINUITY = "REPLAY_DISCONTINUITY"
    PACKET_CORRUPTION = "PACKET_CORRUPTION"


class SafetyGateStatus(str, Enum):
    """Operational status emitted by Production Safety Gate."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class DerivSymbol(str, Enum):
    """Supported Deriv Synthetic Index symbols."""

    R_10 = "R_10"  # Volatility 10 Index
    R_25 = "R_25"  # Volatility 25 Index
    R_50 = "R_50"  # Volatility 50 Index
    R_75 = "R_75"  # Volatility 75 Index
    R_100 = "R_100"  # Volatility 100 Index
    BOOM500 = "BOOM500"  # Boom 500 Index
    BOOM1000 = "BOOM1000"  # Boom 1000 Index
    CRASH500 = "CRASH500"  # Crash 500 Index
    CRASH1000 = "CRASH1000"  # Crash 1000 Index
    JUMP10 = "JUMP10"  # Jump 10 Index
    JUMP25 = "JUMP25"  # Jump 25 Index
    STEP = "STEP"  # Step Index
