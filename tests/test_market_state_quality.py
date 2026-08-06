"""
Project GOAT v0.8 — Test Suite: Market Quality Engine (Exhaustive Matrix)
"""

import pytest
from goat.marketdata.core.canonical import compute_stream_id
from goat.marketdata.core.enums import DerivSymbol, SafetyGateStatus, StreamConnectionStatus
from goat.marketdata.core.models import MarketStreamState
from goat.marketstate.core.enums import QualityState
from goat.marketstate.quality.engine import MarketQualityEngine

SYMBOLS = [s.value for s in DerivSymbol]
STREAM_STATUSES = [s.value for s in StreamConnectionStatus]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("status", STREAM_STATUSES)
def test_quality_engine_matrix(symbol, status):
    engine = MarketQualityEngine()
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

    assessment = engine.evaluate_quality(
        symbol=symbol,
        stream_state=stream,
        recent_gaps=[],
        safety_status=SafetyGateStatus.HEALTHY,
        replay_integrity_passed=True,
    )

    assert assessment.symbol == symbol
    assert assessment.assessment_id.startswith("MQA_")
    assert isinstance(assessment.overall_quality, QualityState)

    if status in ("DISCONNECTED", "TERMINATED"):
        assert assessment.overall_quality == QualityState.INVALID
