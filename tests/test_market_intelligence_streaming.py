"""
Project GOAT Phase 4 — Streaming Simulation & Performance Benchmark Tests
"""

import time
import pytest

from goat.market_intelligence import MarketIntelligenceEngine


def test_streaming_simulation_10k_ticks():
    """Simulate 10,000 high-frequency streaming ticks and measure throughput performance."""
    engine = MarketIntelligenceEngine()

    counts = {"ticks": 0, "stats": 0, "events": 0}

    engine.subscribe_ticks(lambda _: counts.update({"ticks": counts["ticks"] + 1}))
    engine.subscribe_statistics(lambda _: counts.update({"stats": counts["stats"] + 1}))
    engine.subscribe_events(lambda _: counts.update({"events": counts["events"] + 1}))

    start_time = time.perf_counter()

    base_price = 1000.0
    for i in range(1, 10001):
        # Sine wave price simulation with occasional spikes
        price = base_price + (i % 50) * 0.1
        if i % 1000 == 0:
            price += 50.0  # Trigger spike event every 1000 ticks

        raw = {
            "symbol": "VOLATILITY_100",
            "quote": price,
            "bid": price - 0.1,
            "ask": price + 0.1,
            "epoch": 1786017600 + (i // 10),
            "sequence_number": i,
            "source": "WEBSOCKET_BENCHMARK",
        }
        res = engine.process_raw_tick(raw, arrival_latency_ms=5.0)
        assert res is not None

    elapsed = time.perf_counter() - start_time
    ticks_per_sec = 10000 / elapsed if elapsed > 0 else 0.0

    print(f"\n[Performance Benchmark] Processed 10,000 ticks in {elapsed:.3f}s ({ticks_per_sec:.1f} ticks/sec)")

    assert counts["ticks"] == 10000
    assert counts["stats"] == 10000
    assert elapsed < 12.0  # Must process 10,000 ticks in under 12 seconds (>= 833 ticks/sec)
