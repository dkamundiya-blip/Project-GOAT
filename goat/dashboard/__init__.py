"""
Project GOAT v1.0 — Dashboard Backend Package

Public API Exports for Step 1.1.
"""

from goat.dashboard.api import DashboardRESTHandler, create_dashboard_router
from goat.dashboard.core import (
    APIResponsePayload,
    APIRouteGroup,
    DashboardHealthStatus,
    DashboardSession,
    ServerStatus,
    StreamState,
    TelemetryChannel,
    TelemetryFrame,
    WSConnectionState,
    compute_api_payload_id,
    compute_dashboard_session_id,
    compute_telemetry_frame_id,
    compute_ws_connection_id,
    serialize_canonical_json,
)
from goat.dashboard.persistence import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.reporting import (
    generate_dashboard_json_report,
    generate_dashboard_session_report,
)
from goat.dashboard.server import MasterDashboardServer
from goat.dashboard.telemetry import SystemTelemetryCollector
from goat.dashboard.websocket import WebSocketConnectionManager, WebSocketTelemetryEngine

__all__ = [
    # Enums & Models
    "ServerStatus",
    "TelemetryChannel",
    "StreamState",
    "APIRouteGroup",
    "DashboardSession",
    "TelemetryFrame",
    "WSConnectionState",
    "APIResponsePayload",
    "DashboardHealthStatus",
    # Identifiers & Canonical Hashing
    "compute_dashboard_session_id",
    "compute_telemetry_frame_id",
    "compute_ws_connection_id",
    "compute_api_payload_id",
    "serialize_canonical_json",
    # Core Server & Handlers
    "MasterDashboardServer",
    "DashboardRESTHandler",
    "create_dashboard_router",
    "SystemTelemetryCollector",
    "WebSocketConnectionManager",
    "WebSocketTelemetryEngine",
    "DashboardReadOnlyRepositoryAdapter",
    # Reports
    "generate_dashboard_session_report",
    "generate_dashboard_json_report",
]
