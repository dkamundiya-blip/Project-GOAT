"""
Project GOAT v1.0 — Market Data Telemetry & Operational Metrics

Provides real-time system resource telemetry (CPU, Memory) and market ingestion
performance metrics (queue size, buffer size, writes/sec, latency, drops).
"""

from __future__ import annotations

import datetime
import os
from pydantic import BaseModel, Field

try:
    import psutil
except ImportError:
    psutil = None

from goat.market_data.telemetry.latency import LatencySnapshot


class IngestionTelemetrySnapshot(BaseModel):
    """Immutable operational telemetry frame for Control Room and System Monitoring."""

    total_ticks_received: int = Field(default=0, ge=0, description="Cumulative tick count")
    ticks_per_second: float = Field(default=0.0, ge=0.0, description="Current throughput rate")
    websocket_uptime_seconds: float = Field(default=0.0, ge=0.0, description="WebSocket connection uptime")
    dropped_packets: int = Field(default=0, ge=0, description="Total dropped or malformed packets")
    reconnect_count: int = Field(default=0, ge=0, description="Total WebSocket reconnection attempts")
    cpu_usage_percent: float = Field(default=0.0, ge=0.0, description="Process CPU usage percentage")
    memory_usage_mb: float = Field(default=0.0, ge=0.0, description="Process RAM consumption in MB")
    queue_size: int = Field(default=0, ge=0, description="Pending ingestion queue size")
    buffer_size: int = Field(default=0, ge=0, description="Current un-flushed persistence buffer size")
    database_writes_per_second: float = Field(default=0.0, ge=0.0, description="SQLite write rate per sec")
    average_latency_ms: float = Field(default=0.0, ge=0.0, description="Average network latency in ms")
    maximum_latency_ms: float = Field(default=0.0, ge=0.0, description="Maximum network latency in ms")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    class Config:
        frozen = True
        extra = "forbid"


class IngestionMetricsCollector:
    """Collects system resources and market ingestion operational telemetry."""

    def __init__(self):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.dropped_packets = 0
        self.reconnect_count = 0
        self._process = psutil.Process(os.getpid()) if psutil else None

    def record_packet_dropped(self) -> None:
        """Increment dropped packet count."""
        self.dropped_packets += 1

    def record_reconnect(self) -> None:
        """Increment reconnect count."""
        self.reconnect_count += 1

    def snapshot(
        self,
        total_ticks: int = 0,
        ticks_per_sec: float = 0.0,
        ws_connected_time: float = 0.0,
        queue_size: int = 0,
        buffer_size: int = 0,
        db_writes_per_sec: float = 0.0,
        latency_snap: LatencySnapshot | None = None,
    ) -> IngestionTelemetrySnapshot:
        """Generate an immutable telemetry snapshot."""

        cpu_percent = 0.0
        memory_mb = 0.0

        if self._process:
            try:
                cpu_percent = round(self._process.cpu_percent(interval=None), 1)
                memory_mb = round(self._process.memory_info().rss / (1024 * 1024), 2)
            except Exception:
                pass

        avg_lat = latency_snap.average_latency_ms if latency_snap else 0.0
        max_lat = latency_snap.max_latency_ms if latency_snap else 0.0

        return IngestionTelemetrySnapshot(
            total_ticks_received=total_ticks,
            ticks_per_second=round(ticks_per_sec, 2),
            websocket_uptime_seconds=round(ws_connected_time, 1),
            dropped_packets=self.dropped_packets,
            reconnect_count=self.reconnect_count,
            cpu_usage_percent=cpu_percent,
            memory_usage_mb=memory_mb,
            queue_size=queue_size,
            buffer_size=buffer_size,
            database_writes_per_second=round(db_writes_per_sec, 2),
            average_latency_ms=avg_lat,
            maximum_latency_ms=max_lat,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
