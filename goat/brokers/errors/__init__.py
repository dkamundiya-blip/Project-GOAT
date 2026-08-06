"""
Project GOAT v0.8 — Broker Errors Subpackage
"""

from goat.brokers.errors.framework import (
    AuthenticationError,
    BrokerError,
    BrokerErrorModel,
    BrokerUnavailableError,
    ConnectionError,
    OrderValidationError,
    PermissionError,
    RateLimitError,
    ReplayError,
    TimeoutError,
)

__all__ = [
    "BrokerErrorModel",
    "BrokerError",
    "ConnectionError",
    "AuthenticationError",
    "PermissionError",
    "RateLimitError",
    "OrderValidationError",
    "BrokerUnavailableError",
    "TimeoutError",
    "ReplayError",
]
