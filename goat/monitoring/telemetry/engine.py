"""
Project GOAT v0.8 — Telemetry Engine

Collects and records abstract operational performance metrics: CPU, Memory, Disk, DB/Tick/Execution/Notification latencies, Queue Depth, Processing Time, Repository Size, and Event Throughput.

STRICT RULE: No OS-specific system API calls (e.g. psutil/win32). Abstract and fully replayable.
"""

from __future__ import annotations

from typing import Any

from goat.monitoring.core.canonical import compute_telemetry_id
from goat.monitoring.core.models import TelemetrySnapshot


class TelemetryEngine:
    """Engine recording abstract operational metrics and performance snapshots."""

    def __init__(self):
        self._snapshots: list[TelemetrySnapshot] = []

    def record_snapshot(
        self,
        timestamp: str,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        disk_usage: float = 0.0,
        database_latency_ms: float = 0.0,
        tick_latency_ms: float = 0.0,
        notification_latency_ms: float = 0.0,
        execution_latency_ms: float = 0.0,
        queue_depth: int = 0,
        processing_time_ms: float = 0.0,
        repository_size_bytes: int = 0,
        replay_throughput_eps: float = 0.0,
        event_throughput_eps: float = 0.0,
    ) -> TelemetrySnapshot:
        """Create and record an immutable TelemetrySnapshot."""
        tel_id, tel_hash = compute_telemetry_id(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            timestamp=timestamp,
        )

        snapshot = TelemetrySnapshot(
            snapshot_id=tel_id,
            cpu_usage=float(cpu_usage),
            memory_usage=float(memory_usage),
            disk_usage=float(disk_usage),
            database_latency_ms=float(database_latency_ms),
            tick_latency_ms=float(tick_latency_ms),
            notification_latency_ms=float(notification_latency_ms),
            execution_latency_ms=float(execution_latency_ms),
            queue_depth=int(queue_depth),
            processing_time_ms=float(processing_time_ms),
            repository_size_bytes=int(repository_size_bytes),
            replay_throughput_eps=float(replay_throughput_eps),
            event_throughput_eps=float(event_throughput_eps),
            timestamp=timestamp,
            canonical_hash=tel_hash,
        )

        self._snapshots.append(snapshot)
        return snapshot

    def get_latest_snapshot(self) -> TelemetrySnapshot | None:
        return self._snapshots[-1] if self._snapshots else None

    def get_all_snapshots(self) -> list[TelemetrySnapshot]:
        return list(self._snapshots)
