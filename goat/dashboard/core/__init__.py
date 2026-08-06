"""
Project GOAT v1.0 — Dashboard Core Package
"""

from goat.dashboard.core.canonical import (
    compute_api_payload_id,
    compute_dashboard_session_id,
    compute_telemetry_frame_id,
    compute_ws_connection_id,
    serialize_canonical_json,
)
from goat.dashboard.core.enums import APIRouteGroup, ServerStatus, StreamState, TelemetryChannel
from goat.dashboard.core.models import (
    APIResponsePayload,
    DashboardHealthStatus,
    DashboardSession,
    TelemetryFrame,
    WSConnectionState,
)

__all__ = [
    "ServerStatus",
    "TelemetryChannel",
    "StreamState",
    "APIRouteGroup",
    "DashboardSession",
    "TelemetryFrame",
    "WSConnectionState",
    "APIResponsePayload",
    "DashboardHealthStatus",
    "compute_dashboard_session_id",
    "compute_telemetry_frame_id",
    "compute_ws_connection_id",
    "compute_api_payload_id",
    "serialize_canonical_json",
]
