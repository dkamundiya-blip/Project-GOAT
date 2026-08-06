"""
Project GOAT v1.0 — Dashboard Core Domain Models
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from goat.dashboard.core.enums import ServerStatus, StreamState, TelemetryChannel


class DashboardSession(BaseModel):
    """Immutable session metadata model for Dashboard server."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str
    host: str = "127.0.0.1"
    port: int = 8000
    status: ServerStatus = ServerStatus.INITIALIZING
    start_time: str
    active_connections: int = 0
    frozen_version: str = "v0.9.1"


class TelemetryFrame(BaseModel):
    """Immutable real-time telemetry frame broadcast payload."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    frame_id: str
    channel: TelemetryChannel
    sequence: int
    timestamp: str
    payload: Dict[str, Any]


class WSConnectionState(BaseModel):
    """Immutable WebSocket client connection state model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    connection_id: str
    client_id: str
    remote_addr: str = "127.0.0.1"
    connect_time: str
    state: StreamState = StreamState.CONNECTING


class APIResponsePayload(BaseModel):
    """Immutable API response payload model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    payload_id: str
    route: str
    status_code: int = 200
    timestamp: str
    data: Dict[str, Any]
    meta: Dict[str, Any] = Field(default_factory=dict)


class DashboardHealthStatus(BaseModel):
    """Dashboard system health status overview."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: ServerStatus = ServerStatus.RUNNING
    uptime_seconds: float = 0.0
    active_ws_clients: int = 0
    system_memory_mb: float = 0.0
    database_status: str = "HEALTHY"
    frozen_backend_version: str = "v0.9.1"
