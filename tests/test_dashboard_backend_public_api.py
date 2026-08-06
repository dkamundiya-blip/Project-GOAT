"""
Project GOAT v1.0 — Test Suite: Dashboard Backend Public API Exports
"""

import goat.dashboard as dashboard

EXPECTED_EXPORTS = [
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
    "MasterDashboardServer",
    "DashboardRESTHandler",
    "create_dashboard_router",
    "SystemTelemetryCollector",
    "WebSocketConnectionManager",
    "WebSocketTelemetryEngine",
    "DashboardReadOnlyRepositoryAdapter",
    "generate_dashboard_session_report",
    "generate_dashboard_json_report",
]


def test_dashboard_backend_public_api_exports():
    for export in EXPECTED_EXPORTS:
        assert hasattr(dashboard, export), f"Missing public export: {export}"
        assert export in dashboard.__all__, f"Export {export} not in __all__"
