"""
Project GOAT v1.0 — Dashboard System Telemetry Collector
"""

import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

from goat.dashboard.core.canonical import compute_telemetry_frame_id
from goat.dashboard.core.enums import TelemetryChannel
from goat.dashboard.core.models import TelemetryFrame


class SystemTelemetryCollector:
    """Collects real-time system and research platform telemetry metrics using stdlib."""

    def __init__(self) -> None:
        self._sequence_map: Dict[TelemetryChannel, int] = {channel: 0 for channel in TelemetryChannel}
        self._start_time = time.time()

    def _next_sequence(self, channel: TelemetryChannel) -> int:
        self._sequence_map[channel] += 1
        return self._sequence_map[channel]

    def collect_system_telemetry(self, active_ws_clients: int = 0) -> TelemetryFrame:
        """Collect current host process system telemetry frame."""
        now = datetime.now(timezone.utc).isoformat()
        seq = self._next_sequence(TelemetryChannel.SYSTEM)

        payload: Dict[str, Any] = {
            "uptime_seconds": round(time.time() - self._start_time, 2),
            "python_version": sys.version.split()[0],
            "active_ws_clients": active_ws_clients,
            "status": "HEALTHY",
        }

        frame_id = compute_telemetry_frame_id(TelemetryChannel.SYSTEM.value, now, seq)
        return TelemetryFrame(
            frame_id=frame_id,
            channel=TelemetryChannel.SYSTEM,
            sequence=seq,
            timestamp=now,
            payload=payload,
        )

    def create_custom_telemetry_frame(self, channel: TelemetryChannel, payload: Dict[str, Any]) -> TelemetryFrame:
        """Create custom telemetry frame for specific channel."""
        now = datetime.now(timezone.utc).isoformat()
        seq = self._next_sequence(channel)
        frame_id = compute_telemetry_frame_id(channel.value, now, seq)
        return TelemetryFrame(
            frame_id=frame_id,
            channel=channel,
            sequence=seq,
            timestamp=now,
            payload=payload,
        )
