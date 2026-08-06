"""
Project GOAT v1.0 — Dashboard WebSocket Package
"""

from goat.dashboard.websocket.engine import WebSocketTelemetryEngine
from goat.dashboard.websocket.manager import WebSocketConnectionManager

__all__ = ["WebSocketConnectionManager", "WebSocketTelemetryEngine"]
