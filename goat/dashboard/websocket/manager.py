"""
Project GOAT v1.0 — Dashboard WebSocket Connection Manager
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from goat.dashboard.core.canonical import compute_ws_connection_id
from goat.dashboard.core.enums import StreamState
from goat.dashboard.core.models import TelemetryFrame, WSConnectionState


class WebSocketConnectionManager:
    """Manages active WebSocket client connections and frame broadcasting."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, Any] = {}
        self.connection_states: Dict[str, WSConnectionState] = {}

    async def connect(self, websocket: Any, client_id: str) -> WSConnectionState:
        """Register and accept new incoming WebSocket connection."""
        if hasattr(websocket, "accept"):
            await websocket.accept()

        now = datetime.now(timezone.utc).isoformat()
        conn_id = compute_ws_connection_id(client_id, now)

        remote_addr = getattr(getattr(websocket, "client", None), "host", "127.0.0.1")
        state = WSConnectionState(
            connection_id=conn_id,
            client_id=client_id,
            remote_addr=remote_addr,
            connect_time=now,
            state=StreamState.OPEN,
        )
        self.active_connections[conn_id] = websocket
        self.connection_states[conn_id] = state
        return state

    def disconnect(self, connection_id: str) -> None:
        """Disconnect and cleanup client connection state."""
        self.active_connections.pop(connection_id, None)
        if conn_state := self.connection_states.get(connection_id):
            self.connection_states[connection_id] = WSConnectionState(
                connection_id=conn_state.connection_id,
                client_id=conn_state.client_id,
                remote_addr=conn_state.remote_addr,
                connect_time=conn_state.connect_time,
                state=StreamState.CLOSED,
            )

    async def broadcast_frame(self, frame: TelemetryFrame) -> int:
        """Broadcast telemetry frame to all connected WebSocket clients."""
        payload_dict = frame.model_dump()
        sent_count = 0
        dead_connections: List[str] = []

        for conn_id, ws in self.active_connections.items():
            try:
                if hasattr(ws, "send_json"):
                    await ws.send_json(payload_dict)
                elif hasattr(ws, "send"):
                    await ws.send(str(payload_dict))
                sent_count += 1
            except Exception:
                dead_connections.append(conn_id)

        for conn_id in dead_connections:
            self.disconnect(conn_id)

        return sent_count

    @property
    def connection_count(self) -> int:
        """Total count of active open connections."""
        return len(self.active_connections)
