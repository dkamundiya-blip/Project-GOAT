"""
Project GOAT v1.0 — Reconnect Policy Module

Implements bounded exponential backoff with random jitter for resilient WebSocket reconnections.
"""

from __future__ import annotations

import random
from pydantic import BaseModel, Field


class ReconnectState(BaseModel):
    """Immutable state snapshot of connection reconnection attempts."""

    attempt_count: int = Field(default=0, ge=0, description="Consecutive retries attempted")
    next_delay_seconds: float = Field(default=1.0, ge=0.0, description="Calculated delay before next attempt")
    total_reconnects: int = Field(default=0, ge=0, description="Lifetime reconnection count")

    class Config:
        frozen = True
        extra = "forbid"


class ReconnectPolicy:
    """Bounded exponential backoff policy calculator."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        max_retries: int = 20,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self._attempt_count = 0
        self._total_reconnects = 0

    def compute_next_delay(self) -> float:
        """Compute next backoff delay with 50% random jitter."""
        self._attempt_count += 1
        exp_delay = min(self.max_delay, self.base_delay * (2 ** (self._attempt_count - 1)))
        jitter = random.uniform(0, 0.5 * exp_delay)
        return round(exp_delay + jitter, 2)

    def record_successful_connection(self) -> None:
        """Reset consecutive attempt counter on successful connection."""
        if self._attempt_count > 0:
            self._total_reconnects += 1
        self._attempt_count = 0

    def should_retry(self) -> bool:
        """Check if retry attempt is within max_retries limit."""
        return self._attempt_count < self.max_retries

    def get_state(self) -> ReconnectState:
        """Get snapshot of current reconnect state."""
        return ReconnectState(
            attempt_count=self._attempt_count,
            next_delay_seconds=self.base_delay if self._attempt_count == 0 else min(self.max_delay, self.base_delay * (2 ** self._attempt_count)),
            total_reconnects=self._total_reconnects,
        )

    def reset(self) -> None:
        """Reset all counters."""
        self._attempt_count = 0
        self._total_reconnects = 0
