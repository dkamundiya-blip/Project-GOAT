"""
Project GOAT v0.8 — Core Enums for Deriv Production Adapter

Defines Deriv-specific protocol enums:
- DerivContractType
- DerivDurationUnit
- DerivStreamType
"""

from enum import Enum


class DerivContractType(str, Enum):
    """Deriv contract type enum."""

    RISE = "CALL"
    FALL = "PUT"
    MULTUP = "MULTUP"
    MULTDOWN = "MULTDOWN"
    DIGITMATCH = "DIGITMATCH"
    DIGITDIFF = "DIGITDIFF"


class DerivDurationUnit(str, Enum):
    """Deriv contract duration unit enum."""

    TICKS = "t"
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"


class DerivStreamType(str, Enum):
    """Deriv WebSocket payload stream category enum."""

    TICK = "tick"
    CANDLE = "ohlc"
    PROPOSAL = "proposal"
    BALANCE = "balance"
    TRANSACTION = "transaction"
    PING = "ping"
