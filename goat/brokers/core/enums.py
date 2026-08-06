"""
Project GOAT v0.8 — Core Enums for Broker Abstraction Framework

Defines deterministic enums for broker management:
- BrokerType
- ConnectionStatus
- OrderSide
- OrderType
- TimeInForce
"""

from enum import Enum


class BrokerType(str, Enum):
    """Supported broker technology type enum."""

    DERIV = "DERIV"
    WELTRADE = "WELTRADE"
    MT5 = "MT5"
    GENERIC = "GENERIC"


class ConnectionStatus(str, Enum):
    """Broker connection state enum."""

    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    RECONNECTING = "RECONNECTING"
    FAILED = "FAILED"


class OrderSide(str, Enum):
    """Order transaction side enum."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order execution model enum."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class TimeInForce(str, Enum):
    """Order duration policy enum."""

    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate Or Cancel
    FOK = "FOK"  # Fill Or Kill
