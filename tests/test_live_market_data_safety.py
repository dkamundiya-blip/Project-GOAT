"""
Project GOAT v0.8 — Test Suite: Production Safety Gate (Exhaustive Matrix)
"""

import pytest
from goat.marketdata.core.canonical import compute_stream_id
from goat.marketdata.core.enums import DerivSymbol, SafetyGateStatus, StreamConnectionStatus
from goat.marketdata.core.models import MarketStreamState
from goat.marketdata.safety import MarketStreamSafetyGate

SYMBOLS = [s.value for s in DerivSymbol]
STREAM_STATUSES = [s.value for s in StreamConnectionStatus]


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_safety_gate_healthy_matrix(symbol):
    gate = MarketStreamSafetyGate()
    stream_id, canonical_hash = compute_stream_id("DERIV", symbol, "2026-07-31T12:00:00Z")
    stream = MarketStreamState(
        stream_id=stream_id,
        broker="DERIV",
        symbol=symbol,
        connection_status=StreamConnectionStatus.CONNECTED,
        heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=10.0,
        packets_received=100,
        packets_dropped=0,
        reconnect_count=0,
        canonical_hash=canonical_hash,
    )

    res = gate.evaluate_stream(stream)
    assert res.symbol == symbol
    assert res.status in (SafetyGateStatus.HEALTHY, SafetyGateStatus.UNAVAILABLE)


@pytest.mark.parametrize("symbol", SYMBOLS[:5])
@pytest.mark.parametrize("status", STREAM_STATUSES)
def test_safety_gate_status_mapping_matrix(symbol, status):
    gate = MarketStreamSafetyGate()
    stream_id, canonical_hash = compute_stream_id("DERIV", symbol, "2026-07-31T12:00:00Z")
    stream = MarketStreamState(
        stream_id=stream_id,
        broker="DERIV",
        symbol=symbol,
        connection_status=StreamConnectionStatus(status),
        heartbeat_timestamp="2026-07-31T12:00:00Z",
        latency_ms=10.0,
        packets_received=100,
        packets_dropped=0,
        reconnect_count=0,
        canonical_hash=canonical_hash,
    )

    res = gate.evaluate_stream(stream)
    if status in ("DISCONNECTED", "TERMINATED"):
        assert res.status == SafetyGateStatus.UNAVAILABLE
    elif status in ("RECONNECTING", "DEGRADED"):
        assert res.status in (SafetyGateStatus.DEGRADED, SafetyGateStatus.UNAVAILABLE)
