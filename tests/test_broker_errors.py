"""
Project GOAT v0.8 — Test Suite: Broker Error Framework (Exhaustive Matrix)
"""

import pytest

from goat.brokers.errors.framework import (
    AuthenticationError,
    BrokerError,
    BrokerUnavailableError,
    ConnectionError,
    OrderValidationError,
    PermissionError,
    RateLimitError,
    ReplayError,
    TimeoutError,
)
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]

ERROR_CLASSES = [
    (ConnectionError, "CONNECTION"),
    (AuthenticationError, "AUTHENTICATION"),
    (PermissionError, "PERMISSION"),
    (RateLimitError, "RATE_LIMIT"),
    (OrderValidationError, "ORDER_VALIDATION"),
    (BrokerUnavailableError, "AVAILABILITY"),
    (TimeoutError, "TIMEOUT"),
    (ReplayError, "REPLAY"),
]


@pytest.mark.parametrize("err_cls, expected_cat", ERROR_CLASSES)
@pytest.mark.parametrize("symbol", SYMBOLS)
def test_broker_error_framework_matrix(err_cls, expected_cat, symbol):
    msg = f"Test error message for {symbol}"
    exc = err_cls(msg)
    assert isinstance(exc, BrokerError)
    assert exc.category == expected_cat
    assert exc.model.error_id.startswith("BRE_")
    assert exc.model.category == expected_cat
    assert msg in str(exc)
    assert exc.model.canonical_hash != ""
