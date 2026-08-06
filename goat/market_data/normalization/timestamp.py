"""
Project GOAT v1.0 — Market Data Timestamp Normalization

Handles conversions between Unix epoch integers, ISO 8601 UTC strings,
and arrival latency calculations.
"""

from __future__ import annotations

import datetime
from datetime import timezone


def epoch_to_iso(epoch: int | float) -> str:
    """Convert Unix epoch timestamp to ISO 8601 UTC string."""
    dt = datetime.datetime.fromtimestamp(float(epoch), tz=timezone.utc)
    return dt.isoformat()


def now_utc_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.datetime.now(timezone.utc).isoformat()


def compute_latency_ms(epoch: int | float, arrival_time: datetime.datetime | None = None) -> float:
    """Compute network/ingestion latency in milliseconds.

    Args:
        epoch: Provider epoch timestamp in seconds.
        arrival_time: Optional arrival datetime (defaults to now UTC).

    Returns:
        Latency in milliseconds (>= 0.0).
    """
    if arrival_time is None:
        arrival_time = datetime.datetime.now(timezone.utc)
    elif arrival_time.tzinfo is None:
        arrival_time = arrival_time.replace(tzinfo=timezone.utc)

    provider_dt = datetime.datetime.fromtimestamp(float(epoch), tz=timezone.utc)
    latency_sec = (arrival_time - provider_dt).total_seconds()
    return max(0.0, round(latency_sec * 1000.0, 3))
