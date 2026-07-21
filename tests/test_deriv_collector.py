"""
Project GOAT v0.2 — Unit Tests for Deriv Market Data Collector
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from goat.config import GoatSettings
from goat.data.collector.deriv import DerivMarketDataCollector
from goat.data.collector.base import CollectorStatus
from goat.data.schemas import DataSource


@pytest.mark.asyncio
async def test_deriv_collector_lifecycle_and_request() -> None:
    """Test connect, request correlation via req_id, and disconnect."""
    mock_ws = AsyncMock()
    msg_queue: asyncio.Queue[str] = asyncio.Queue()

    async def mock_send(msg_str):
        data = json.loads(msg_str)
        req_id = data.get("req_id")
        await msg_queue.put(json.dumps({"ping": "pong", "req_id": req_id}))

    async def mock_recv():
        return await msg_queue.get()

    mock_ws.send = mock_send
    mock_ws.recv = mock_recv

    with patch("websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
        collector = DerivMarketDataCollector(
            settings=GoatSettings(heartbeat_interval=0)
        )
        await collector.connect()
        assert await collector.get_status() == CollectorStatus.CONNECTED

        resp = await collector.request({"ping": 1})
        assert resp["ping"] == "pong"
        assert resp["req_id"] == 1

        await collector.disconnect()
        assert await collector.get_status() == CollectorStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_deriv_collector_subscribe_and_unsubscribe() -> None:
    """Test tick subscription and unsubscription lifecycle."""
    mock_ws = AsyncMock()
    msg_queue: asyncio.Queue[str] = asyncio.Queue()

    async def mock_send(msg_str):
        data = json.loads(msg_str)
        req_id = data.get("req_id")
        if "ticks" in data:
            await msg_queue.put(
                json.dumps({
                    "req_id": req_id,
                    "subscription": {"id": "sub_R_75_001"},
                })
            )
        elif "forget" in data:
            await msg_queue.put(
                json.dumps({
                    "req_id": req_id,
                    "forget": "sub_R_75_001",
                })
            )

    async def mock_recv():
        return await msg_queue.get()

    mock_ws.send = mock_send
    mock_ws.recv = mock_recv

    with patch("websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
        collector = DerivMarketDataCollector(
            settings=GoatSettings(heartbeat_interval=0)
        )
        await collector.connect()

        sub_id = await collector.subscribe_ticks("R_75")
        assert sub_id == "sub_R_75_001"
        assert "R_75" in collector._active_subscriptions

        # Duplicate subscribe returns existing sub_id without re-sending
        sub_id_dup = await collector.subscribe_ticks("R_75")
        assert sub_id_dup == "sub_R_75_001"

        await collector.unsubscribe_ticks("R_75")
        assert "R_75" not in collector._active_subscriptions

        await collector.disconnect()


@pytest.mark.asyncio
async def test_deriv_collector_live_tick_routing() -> None:
    """Test receiving live tick frames and converting to GOAT Tick schema."""
    collector = DerivMarketDataCollector()
    collector._status = CollectorStatus.CONNECTED
    collector._tick_queues["R_75"] = asyncio.Queue()

    live_tick_msg = {
        "msg_type": "tick",
        "tick": {
            "symbol": "R_75",
            "quote": 750.123,
            "epoch": 1721623200,
            "id": "t_001",
        },
    }

    collector._handle_message(live_tick_msg)

    queue = collector._tick_queues["R_75"]
    assert queue.qsize() == 1
    tick = queue.get_nowait()
    assert tick.symbol == "R_75"
    assert float(tick.price) == 750.123
    assert tick.source == DataSource.LIVE
