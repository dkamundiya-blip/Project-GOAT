"""
Project GOAT Phase 4 — Unit Tests for Tick Recorder
"""

from goat.market_intelligence.persistence import InMemoryTickRepository
from goat.market_intelligence.recorder import TickRecorder


def test_tick_recorder_raw_payload_recording():
    repo = InMemoryTickRepository()
    recorder = TickRecorder(repository=repo)

    raw_payload = {
        "symbol": "R_100",  # Will normalize to VOLATILITY_100
        "quote": 4532.50,
        "bid": 4532.30,
        "ask": 4532.70,
        "epoch": 1786017600,
        "source": "DERIV_WS",
    }

    recorded = recorder.record_raw_tick(raw_payload, arrival_latency_ms=14.2)
    assert recorded.symbol == "VOLATILITY_100"
    assert recorded.mid_price == 4532.50
    assert recorded.spread == 0.40
    assert recorded.sequence_number == 1
    assert recorded.source == "DERIV_WS"
    assert recorded.latency_ms == 14.2

    # Verify repository storage
    assert repo.count("VOLATILITY_100") == 1
    latest = repo.get_latest_tick("VOLATILITY_100")
    assert latest.tick_id == recorded.tick_id
