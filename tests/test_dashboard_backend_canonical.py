"""
Project GOAT v1.0 — Test Suite: Dashboard Backend Canonical Hashing
"""

import pytest

from goat.dashboard.core.canonical import (
    compute_api_payload_id,
    compute_dashboard_session_id,
    compute_telemetry_frame_id,
    compute_ws_connection_id,
    serialize_canonical_json,
)

PORTS = [8000, 8080, 9000, 9090]
TIMES = [f"2026-08-06T{h:02d}:00:00Z" for h in range(12)]
CHANNELS = ["SYSTEM", "MICROSTRUCTURE", "HYPOTHESIS", "EVIDENCE", "GOVERNANCE"]


@pytest.mark.parametrize("port", PORTS)
@pytest.mark.parametrize("t", TIMES)
def test_dashboard_session_id_determinism_matrix(port, t):
    id1 = compute_dashboard_session_id("127.0.0.1", port, t)
    id2 = compute_dashboard_session_id("127.0.0.1", port, t)
    assert id1 == id2
    assert id1.startswith("DSH_")
    assert len(id1) == 20


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("seq", [1, 5, 10, 50, 100])
@pytest.mark.parametrize("t", TIMES[:4])
def test_telemetry_frame_id_determinism_matrix(channel, seq, t):
    id1 = compute_telemetry_frame_id(channel, t, seq)
    id2 = compute_telemetry_frame_id(channel, t, seq)
    assert id1 == id2
    assert id1.startswith("DTR_")
    assert len(id1) == 20


@pytest.mark.parametrize("client_id", [f"C_{i}" for i in range(10)])
@pytest.mark.parametrize("t", TIMES[:5])
def test_ws_connection_id_determinism_matrix(client_id, t):
    id1 = compute_ws_connection_id(client_id, t)
    id2 = compute_ws_connection_id(client_id, t)
    assert id1 == id2
    assert id1.startswith("DWS_")
    assert len(id1) == 20


@pytest.mark.parametrize("code", [200, 404, 500])
@pytest.mark.parametrize("route", ["/health", "/api/v1/summary", "/api/v1/hypotheses"])
@pytest.mark.parametrize("t", TIMES[:4])
def test_api_payload_id_determinism_matrix(code, route, t):
    id1 = compute_api_payload_id(route, t, code)
    id2 = compute_api_payload_id(route, t, code)
    assert id1 == id2
    assert id1.startswith("DAP_")
    assert len(id1) == 20


def test_serialize_canonical_json_sorting():
    d1 = {"z": 1, "a": 2, "m": {"b": 3, "a": 4}}
    d2 = {"a": 2, "m": {"a": 4, "b": 3}, "z": 1}
    assert serialize_canonical_json(d1) == serialize_canonical_json(d2)
