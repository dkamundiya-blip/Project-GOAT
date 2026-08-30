"""Focused regression coverage for the Phase 2B browser tick path."""

from __future__ import annotations

import pytest

import goat.server as server
from goat.market_data.websocket.deriv_client import DerivWebSocketClient


@pytest.mark.asyncio
async def test_deriv_subscription_requests_a_continuous_tick_stream():
    client = DerivWebSocketClient(endpoint_url="wss://example.test/websockets/v3", app_id=1)
    requests: list[dict[str, object]] = []

    async def request(payload: dict[str, object], timeout: float = 10.0) -> dict[str, object]:
        requests.append(payload)
        return {"subscription": {"id": "sub-123"}}

    client.request = request  # type: ignore[method-assign]

    assert await client.subscribe_symbol("R_100") == "sub-123"
    assert requests == [{"ticks": "R_100", "subscribe": 1}]


@pytest.mark.asyncio
async def test_broadcast_keeps_healthy_clients_and_discards_failed_ones():
    class HealthySocket:
        def __init__(self):
            self.messages = []

        async def send_json(self, payload):
            self.messages.append(payload)

    class FailedSocket:
        async def send_json(self, _payload):
            raise RuntimeError("connection closed")

    healthy, failed = HealthySocket(), FailedSocket()
    original_connections = server.connected_websockets.copy()
    server.connected_websockets.clear()
    server.connected_websockets.update({healthy, failed})
    payload = {"tick": {"symbol": "R_100", "quote": 1234.5, "epoch": 1}}

    try:
        await server.broadcast_tick_to_websockets(payload)
        assert healthy.messages == [payload]
        assert failed not in server.connected_websockets
    finally:
        server.connected_websockets.clear()
        server.connected_websockets.update(original_connections)
