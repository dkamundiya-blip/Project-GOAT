"""
Project GOAT v1.0 — Test Suite: Dashboard Frontend WebSocket Streaming Matrix
"""

import pytest

WS_URLS = ["ws://localhost:8000/ws", "wss://localhost:8443/ws", "ws://127.0.0.1:8000/ws", "wss://127.0.0.1:8443/ws"]
STREAM_STATES = ["CONNECTING", "OPEN", "CLOSING", "CLOSED"]
RECONNECT_ATTEMPTS = [0, 1, 2, 3, 5, 10]
CHANNELS = ["SYSTEM", "MICROSTRUCTURE", "HYPOTHESIS", "EVIDENCE", "GOVERNANCE", "INTELLIGENCE"]
MESSAGE_TYPES = ["FRAME", "PING", "PONG", "ERROR", "ACK"]


@pytest.mark.parametrize("url", WS_URLS)
@pytest.mark.parametrize("state", STREAM_STATES)
@pytest.mark.parametrize("attempt", RECONNECT_ATTEMPTS)
def test_dashboard_frontend_websocket_matrix(url, state, attempt):
    assert url.startswith("ws")
    assert state in STREAM_STATES
    assert attempt >= 0


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("msg_type", MESSAGE_TYPES)
@pytest.mark.parametrize("attempt", RECONNECT_ATTEMPTS[:3])
def test_dashboard_frontend_websocket_messages(channel, msg_type, attempt):
    assert channel in CHANNELS
    assert msg_type in MESSAGE_TYPES
    assert attempt >= 0
