"""
Project GOAT v1.0 — Dashboard WebSocket Telemetry Broadcast Engine
"""

from typing import Any, Dict
from goat.dashboard.core.enums import TelemetryChannel
from goat.dashboard.telemetry.collector import SystemTelemetryCollector
from goat.dashboard.websocket.manager import WebSocketConnectionManager


class WebSocketTelemetryEngine:
    """Coordinates telemetry collection and real-time broadcasting."""

    def __init__(
        self,
        manager: WebSocketConnectionManager,
        collector: SystemTelemetryCollector,
    ) -> None:
        self.manager = manager
        self.collector = collector

    async def broadcast_system_telemetry(self) -> int:
        """Collect and broadcast system telemetry frame."""
        frame = self.collector.collect_system_telemetry(active_ws_clients=self.manager.connection_count)
        return await self.manager.broadcast_frame(frame)

    async def broadcast_custom_event(self, channel: TelemetryChannel, payload: Dict[str, Any]) -> int:
        """Collect and broadcast custom event frame."""
        frame = self.collector.create_custom_telemetry_frame(channel=channel, payload=payload)
        return await self.manager.broadcast_frame(frame)
