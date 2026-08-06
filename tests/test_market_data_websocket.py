"""
Project GOAT v1.0 — Test Suite for WebSocket Manager and Connection Resilience
"""

import pytest
import asyncio
from goat.market_data.websocket import ReconnectPolicy, HeartbeatMonitor, WebSocketManager


def test_reconnect_policy_exponential_backoff():
    """Verify exponential backoff delay calculation and retries limit."""
    policy = ReconnectPolicy(base_delay=1.0, max_delay=10.0, max_retries=5)
    
    assert policy.should_retry() is True
    
    delay1 = policy.compute_next_delay()
    assert 1.0 <= delay1 <= 2.0

    delay2 = policy.compute_next_delay()
    assert 2.0 <= delay2 <= 4.0

    # Exhaust retries
    policy.compute_next_delay()
    policy.compute_next_delay()
    policy.compute_next_delay()
    assert policy.should_retry() is False

    # Reset on successful connection
    policy.record_successful_connection()
    assert policy.should_retry() is True


@pytest.mark.asyncio
async def test_heartbeat_monitor_lifecycle():
    """Verify HeartbeatMonitor start/stop and pong recording."""
    ping_called = False

    async def mock_ping():
        nonlocal ping_called
        ping_called = True
        return True

    async def mock_timeout():
        pass

    monitor = HeartbeatMonitor(ping_interval_seconds=0.1, timeout_seconds=0.5)
    monitor.start(ping_fn=mock_ping, on_timeout_fn=mock_timeout)

    await asyncio.sleep(0.25)
    assert ping_called is True

    await monitor.stop()


def test_websocket_manager_initial_state():
    """Verify WebSocketManager initial state and subscription tracking."""
    manager = WebSocketManager()
    assert manager.connection_state == "DISCONNECTED"
    assert manager.uptime_seconds == 0.0
    assert len(manager.subscribed_symbols) == 0


@pytest.mark.asyncio
async def test_websocket_manager_subscriptions():
    """Verify subscribing and unsubscribing symbol tracking."""
    manager = WebSocketManager()
    
    await manager.subscribe("VOLATILITY_100")
    assert "VOLATILITY_100" in manager.subscribed_symbols

    await manager.subscribe("STEP_INDEX")
    assert "STEP_INDEX" in manager.subscribed_symbols
    assert len(manager.subscribed_symbols) == 2

    await manager.unsubscribe("VOLATILITY_100")
    assert "VOLATILITY_100" not in manager.subscribed_symbols
    assert len(manager.subscribed_symbols) == 1
