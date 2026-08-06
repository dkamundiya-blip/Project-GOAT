"""
Project GOAT v1.0 — Test Suite: Dashboard Backend WebSocket Engine
"""

import pytest

from goat.dashboard.core.enums import StreamState, TelemetryChannel
from goat.dashboard.telemetry.collector import SystemTelemetryCollector
from goat.dashboard.websocket.engine import WebSocketTelemetryEngine
from goat.dashboard.websocket.manager import WebSocketConnectionManager


@pytest.mark.asyncio
async def test_websocket_connection_manager():
    manager = WebSocketConnectionManager()
    assert manager.connection_count == 0

    collector = SystemTelemetryCollector()
    engine = WebSocketTelemetryEngine(manager=manager, collector=collector)
    assert engine is not None
