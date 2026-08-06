"""
Project GOAT v0.8 — Test Suite: Stream Engine Telemetry (Exhaustive)
"""

import time
import pytest
from goat.marketdata.core.enums import DerivSymbol, StreamConnectionStatus
from goat.marketdata.stream.engine import MarketStreamEngine

SYMBOLS = [s.value for s in DerivSymbol]
LATENCIES = [0.1, 5.0, 50.0, 500.0, 1500.0, 2500.0]


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_stream_engine_lifecycle_matrix(symbol):
    engine = MarketStreamEngine(broker="DERIV", heartbeat_timeout_seconds=2.0)
    state = engine.get_or_create_stream_state(symbol)

    assert state.symbol == symbol
    assert state.packets_received == 0
    assert state.packets_dropped == 0

    s1 = engine.record_packet_received(symbol, latency_ms=10.0)
    assert s1.packets_received == 1
    assert s1.connection_status == StreamConnectionStatus.CONNECTED

    s2 = engine.record_packet_dropped(symbol, reason="MALFORMED_JSON")
    assert s2.packets_dropped == 1

    s3 = engine.record_reconnect(symbol)
    assert s3.reconnect_count == 1
    assert s3.connection_status == StreamConnectionStatus.RECONNECTING


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("lat", LATENCIES)
def test_stream_engine_latency_matrix(symbol, lat):
    engine = MarketStreamEngine(broker="DERIV")
    s = engine.record_packet_received(symbol, latency_ms=lat)
    if lat > 2000.0:
        assert s.connection_status == StreamConnectionStatus.DEGRADED
    else:
        assert s.connection_status == StreamConnectionStatus.CONNECTED


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
def test_stream_engine_heartbeat_timeout_matrix(symbol):
    engine = MarketStreamEngine(broker="DERIV", heartbeat_timeout_seconds=0.05)
    engine.get_or_create_stream_state(symbol)

    time.sleep(0.06)
    status = engine.evaluate_stream_health(symbol)
    assert status == StreamConnectionStatus.DISCONNECTED
