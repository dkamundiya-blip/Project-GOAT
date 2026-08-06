"""
Project GOAT v1.0 — Latency Tracking Module

Tracks per-symbol and global arrival/network latency metrics across sliding windows.
"""

from __future__ import annotations

from collections import deque
from pydantic import BaseModel, Field


class LatencySnapshot(BaseModel):
    """Immutable latency summary statistics."""

    current_latency_ms: float = Field(default=0.0, description="Latest tick latency in ms")
    average_latency_ms: float = Field(default=0.0, description="Window average latency in ms")
    max_latency_ms: float = Field(default=0.0, description="Window maximum latency in ms")
    min_latency_ms: float = Field(default=0.0, description="Window minimum latency in ms")
    samples_count: int = Field(default=0, ge=0, description="Total samples in calculation window")

    class Config:
        frozen = True
        extra = "forbid"


class LatencyTracker:
    """Sliding-window latency recorder."""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self._samples: dict[str, deque[float]] = {}
        self._global_samples: deque[float] = deque(maxlen=window_size)
        self._current_latency: dict[str, float] = {}

    def record_latency(self, symbol: str, latency_ms: float) -> None:
        """Record a latency measurement for a symbol."""
        sym = symbol.strip().upper()
        if sym not in self._samples:
            self._samples[sym] = deque(maxlen=self.window_size)
        val = max(0.0, float(latency_ms))
        self._samples[sym].append(val)
        self._global_samples.append(val)
        self._current_latency[sym] = val

    def get_symbol_latency(self, symbol: str) -> LatencySnapshot:
        """Get latency snapshot for a specific symbol."""
        sym = symbol.strip().upper()
        if sym not in self._samples or len(self._samples[sym]) == 0:
            return LatencySnapshot()

        samples = list(self._samples[sym])
        curr = self._current_latency.get(sym, samples[-1])
        avg = sum(samples) / len(samples)
        mx = max(samples)
        mn = min(samples)

        return LatencySnapshot(
            current_latency_ms=round(curr, 2),
            average_latency_ms=round(avg, 2),
            max_latency_ms=round(mx, 2),
            min_latency_ms=round(mn, 2),
            samples_count=len(samples),
        )

    def get_global_latency(self) -> LatencySnapshot:
        """Get global aggregate latency snapshot across all symbols."""
        if not self._global_samples:
            return LatencySnapshot()

        samples = list(self._global_samples)
        curr = samples[-1]
        avg = sum(samples) / len(samples)
        mx = max(samples)
        mn = min(samples)

        return LatencySnapshot(
            current_latency_ms=round(curr, 2),
            average_latency_ms=round(avg, 2),
            max_latency_ms=round(mx, 2),
            min_latency_ms=round(mn, 2),
            samples_count=len(samples),
        )

    def clear(self) -> None:
        """Clear recorded latency history."""
        self._samples.clear()
        self._global_samples.clear()
        self._current_latency.clear()
