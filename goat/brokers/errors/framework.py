"""
Project GOAT v0.8 — Broker Error Framework

Defines deterministic, broker-independent error models and custom exceptions:
- BrokerError
- ConnectionError
- AuthenticationError
- PermissionError
- RateLimitError
- OrderValidationError
- BrokerUnavailableError
- TimeoutError
- ReplayError
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.brokers.core.canonical import compute_error_id


class BrokerErrorModel(BaseModel):
    """Immutable model representing a broker-independent error payload."""

    error_id: str = Field(
        ...,
        description="Unique error ID formatted as BRE_<HEX16>",
        pattern=r"^BRE_[A-Fa-f0-9]{16}$",
    )
    code: str = Field(..., description="Machine-readable error code string")
    category: str = Field(..., description="Error category classification")
    message: str = Field(..., description="Human-readable error description")
    explanation: str = Field(..., description="Deterministic explanation of root cause")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Operational metadata")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class BrokerError(Exception):
    """Base exception class for all broker-independent errors."""

    def __init__(self, code: str, category: str, message: str, explanation: str, metadata: dict[str, Any] | None = None):
        self.code = str(code).strip().upper()
        self.category = str(category).strip().upper()
        self.message = str(message).strip()
        self.explanation = str(explanation).strip()
        self.metadata = metadata or {}

        error_id, canonical_hash = compute_error_id(self.code, self.category, self.message)
        self.model = BrokerErrorModel(
            error_id=error_id,
            code=self.code,
            category=self.category,
            message=self.message,
            explanation=self.explanation,
            metadata=self.metadata,
            canonical_hash=canonical_hash,
        )
        super().__init__(f"[{self.category}:{self.code}] {self.message} — {self.explanation}")


class ConnectionError(BrokerError):
    """Session connection or network failure error."""

    def __init__(self, message: str, explanation: str = "Connection to broker gateway failed or was forcibly closed", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_CONNECTION_FAILED", "CONNECTION", message, explanation, metadata)


class AuthenticationError(BrokerError):
    """API token or authentication failure error."""

    def __init__(self, message: str, explanation: str = "Broker API credentials or tokens were rejected", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_AUTHENTICATION_FAILED", "AUTHENTICATION", message, explanation, metadata)


class PermissionError(BrokerError):
    """Account authorization or permission failure error."""

    def __init__(self, message: str, explanation: str = "Account lacks required permissions to perform request", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_PERMISSION_DENIED", "PERMISSION", message, explanation, metadata)


class RateLimitError(BrokerError):
    """API request rate limit exceeded error."""

    def __init__(self, message: str, explanation: str = "Broker API call frequency exceeded rate limits", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_RATE_LIMIT_EXCEEDED", "RATE_LIMIT", message, explanation, metadata)


class OrderValidationError(BrokerError):
    """Order intent validation or capability check failure error."""

    def __init__(self, message: str, explanation: str = "Order intent failed structural or capability rules", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_ORDER_VALIDATION_FAILED", "ORDER_VALIDATION", message, explanation, metadata)


class BrokerUnavailableError(BrokerError):
    """Broker system maintenance or outage error."""

    def __init__(self, message: str, explanation: str = "Target broker service is currently unavailable or under maintenance", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_BROKER_UNAVAILABLE", "AVAILABILITY", message, explanation, metadata)


class TimeoutError(BrokerError):
    """Gateway response timeout error."""

    def __init__(self, message: str, explanation: str = "Broker gateway response exceeded timeout limit", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_TIMEOUT", "TIMEOUT", message, explanation, metadata)


class ReplayError(BrokerError):
    """Replay verification or checksum mismatch error."""

    def __init__(self, message: str, explanation: str = "Replay sequence integrity or checksum validation failed", metadata: dict[str, Any] | None = None):
        super().__init__("ERR_REPLAY_FAILED", "REPLAY", message, explanation, metadata)
