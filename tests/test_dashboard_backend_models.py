"""
Project GOAT v1.0 — Test Suite: Dashboard Backend Domain Models
"""

import pytest

from goat.dashboard.core.enums import APIRouteGroup, ServerStatus, StreamState, TelemetryChannel
from goat.dashboard.core.models import (
    APIResponsePayload,
    DashboardHealthStatus,
    DashboardSession,
    TelemetryFrame,
    WSConnectionState,
)

SERVER_STATUSES = list(ServerStatus)
CHANNELS = list(TelemetryChannel)
STREAM_STATES = list(StreamState)
ROUTE_GROUPS = list(APIRouteGroup)


@pytest.mark.parametrize("status", SERVER_STATUSES)
@pytest.mark.parametrize("port", [8000, 8080, 9000, 9090])
def test_dashboard_session_model_matrix(status, port):
    session = DashboardSession(
        session_id="DSH_0123456789ABCDEF",
        host="127.0.0.1",
        port=port,
        status=status,
        start_time="2026-08-06T12:00:00Z",
    )
    assert session.session_id == "DSH_0123456789ABCDEF"
    assert session.status == status
    assert session.port == port
    assert session.frozen_version == "v0.9.1"

    with pytest.raises(Exception):
        session.status = ServerStatus.STOPPED


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("seq", [1, 10, 100, 1000])
def test_telemetry_frame_model_matrix(channel, seq):
    frame = TelemetryFrame(
        frame_id=f"DTR_{seq:016d}",
        channel=channel,
        sequence=seq,
        timestamp="2026-08-06T12:00:00Z",
        payload={"seq": seq, "ch": channel.value},
    )
    assert frame.channel == channel
    assert frame.sequence == seq
    assert frame.payload["seq"] == seq


@pytest.mark.parametrize("state", STREAM_STATES)
@pytest.mark.parametrize("client_id", [f"CLIENT_{i}" for i in range(10)])
def test_ws_connection_state_matrix(state, client_id):
    conn = WSConnectionState(
        connection_id=f"DWS_{client_id}",
        client_id=client_id,
        connect_time="2026-08-06T12:00:00Z",
        state=state,
    )
    assert conn.client_id == client_id
    assert conn.state == state


@pytest.mark.parametrize("code", [200, 201, 400, 404, 500])
@pytest.mark.parametrize("route", ["/health", "/api/v1/summary", "/api/v1/hypotheses", "/api/v1/governance"])
def test_api_response_payload_matrix(code, route):
    resp = APIResponsePayload(
        payload_id="DAP_0123456789ABCDEF",
        route=route,
        status_code=code,
        timestamp="2026-08-06T12:00:00Z",
        data={"route": route},
    )
    assert resp.status_code == code
    assert resp.route == route
    assert resp.data["route"] == route
