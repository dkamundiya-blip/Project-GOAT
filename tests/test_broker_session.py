"""
Project GOAT v0.8 — Test Suite: Broker Session Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.session.engine import BrokerSessionEngine

BROKER_IDS = ["BRK_DERIV12345678", "BRK_WELTRADE12345", "BRK_MT51234567890", "BRK_GENERIC123456"]
LATENCIES = [1.0, 5.0, 15.0, 50.0, 150.0, 1200.0]
RECONNECT_STEPS = [1, 2, 3, 5]


@pytest.mark.parametrize("b_id", BROKER_IDS)
@pytest.mark.parametrize("latency", LATENCIES)
@pytest.mark.parametrize("rec_steps", RECONNECT_STEPS)
def test_broker_session_lifecycle_matrix(b_id, latency, rec_steps):
    engine = BrokerSessionEngine(b_id)
    assert engine.get_current_connection() is None

    conn1 = engine.establish_session()
    assert conn1.broker_id == b_id
    assert conn1.status == ConnectionStatus.CONNECTED

    conn2 = engine.record_heartbeat(latency_ms=latency)
    assert conn2.latency_ms == latency
    if latency > 1000.0:
        assert conn2.status == ConnectionStatus.DEGRADED

    for _ in range(rec_steps):
        conn3 = engine.trigger_reconnect()
        assert conn3.status == ConnectionStatus.RECONNECTING

    assert conn3.reconnect_attempts == rec_steps

    conn4 = engine.terminate_session()
    assert conn4.status == ConnectionStatus.DISCONNECTED
    assert conn4.disconnected_at is not None
