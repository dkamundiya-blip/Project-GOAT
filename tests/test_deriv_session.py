"""
Project GOAT v0.8 — Test Suite: Deriv Session Engine (Exhaustive Matrix)
"""

import pytest

from goat.brokers.core.enums import ConnectionStatus
from goat.brokers.deriv.session.engine import DerivSessionEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
BROKER_IDS = ["BRK_DERIV", "BRK_DERIV_DEMO", "BRK_DERIV_REAL"]
LATENCIES = [5.0, 15.0, 50.0, 150.0, 1200.0]


@pytest.mark.parametrize("b_id", BROKER_IDS)
@pytest.mark.parametrize("latency", LATENCIES)
def test_deriv_session_engine_lifecycle_matrix(b_id, latency):
    engine = DerivSessionEngine(broker_id=b_id)
    assert engine.get_current_session() is None

    session1 = engine.establish_session(timestamp="2026-07-31T12:00:00Z")
    assert session1.session_id.startswith("DRS_")
    assert session1.broker_id == b_id
    assert session1.status == ConnectionStatus.CONNECTED

    hb = engine.process_ping_pong("2026-07-31T12:00:00Z", "2026-07-31T12:00:00Z", latency_ms=latency)
    assert hb.heartbeat_id.startswith("DHB_")
    assert hb.roundtrip_ms == latency

    session2 = engine.terminate_session(timestamp="2026-07-31T12:01:00Z")
    assert session2.status == ConnectionStatus.DISCONNECTED


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("latency", [10.0, 50.0, 500.0, 1500.0])
def test_deriv_session_symbols_matrix(symbol, latency):
    b_id = f"BRK_DERIV_{symbol}"
    engine = DerivSessionEngine(broker_id=b_id)
    session = engine.establish_session()
    assert session.broker_id == b_id

    hb = engine.process_ping_pong("2026-07-31T12:00:00Z", "2026-07-31T12:00:00Z", latency_ms=latency)
    if latency > 1000.0:
        assert engine.get_current_session().status == ConnectionStatus.DEGRADED
