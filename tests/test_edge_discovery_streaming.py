"""
Project GOAT Phase 6 — High-Throughput Simulation & Performance Benchmark Tests
"""

import time
import pytest

from goat.edge_discovery import MasterEdgeDiscoveryEngine
from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id


def test_edge_discovery_performance_benchmark():
    """Simulate discovery search across 5,000 feature observations and benchmark throughput."""
    engine = MasterEdgeDiscoveryEngine()

    fvs: list[FeatureVector] = []
    returns: list[float] = []

    for i in range(1, 5001):
        ts = f"2026-08-07T12:00:00Z"
        t_val = 0.9 if i % 3 == 0 else 0.1
        ret = 0.003 if i % 3 == 0 else -0.001

        v_id, c_hash = compute_feature_vector_id(
            "VOLATILITY_100",
            "1m",
            ts,
            {"trend_strength": t_val, "z_score": 1.5, "volatility_expansion": 2.0},
        )
        fv = FeatureVector(
            vector_id=v_id,
            symbol="VOLATILITY_100",
            timeframe="1m",
            timestamp=ts,
            version="5.0.0",
            features={"trend_strength": t_val, "z_score": 1.5, "volatility_expansion": 2.0},
            checksum="CHK",
            metadata={},
            canonical_hash=c_hash,
        )
        fvs.append(fv)
        returns.append(ret)

    start_time = time.perf_counter()

    edges = engine.discover_edges(
        symbol="VOLATILITY_100",
        timeframe="1m",
        feature_vectors=fvs,
        forward_returns=returns,
        min_pvalue=0.05,
        min_sample_size=10,
    )

    elapsed = time.perf_counter() - start_time
    obs_per_sec = 5000 / elapsed if elapsed > 0 else 0.0

    print(f"\n[Edge Discovery Benchmark] Evaluated 5,000 observations across hypothesis space in {elapsed:.3f}s ({obs_per_sec:.1f} obs/sec)")

    assert len(edges) > 0
    assert elapsed < 45.0  # Must complete observation search in under 45 seconds
