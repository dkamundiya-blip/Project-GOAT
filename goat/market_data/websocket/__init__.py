"""
Project GOAT v1.0 — Market Data WebSocket Subsystem Package
"""

from goat.market_data.websocket.deriv_client import DerivWebSocketClient
from goat.market_data.websocket.heartbeat import HeartbeatMonitor
from goat.market_data.websocket.reconnect import ReconnectPolicy, ReconnectState
from goat.market_data.websocket.websocket_manager import WebSocketManager

__all__ = [
    "DerivWebSocketClient",
    "HeartbeatMonitor",
    "ReconnectPolicy",
    "ReconnectState",
    "WebSocketManager",
]
