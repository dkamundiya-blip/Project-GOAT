"""
Project GOAT Phase 6 — Integration Tests for Master Edge Discovery Engine Pipeline
"""

import sqlite3
import pytest

from goat.edge_discovery import DiscoveredEdge, MasterEdgeDiscoveryEngine
from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id


def test_master_edge_discovery_engine_pipeline():
    conn = sqlite3.connect(":memory:")
    engine = MasterEdgeDiscoveryEngine(db_path=conn)

    received_edges: list[DiscoveredEdge] = []
    engine.subscribe_discovered_edges(lambda e: received_edges.append(e))

    # Generate 50 historical feature vectors with strong trend_strength -> positive return correlation
    fvs: list[FeatureVector] = []
    returns: list[float] = []

    for i in range(1, 51):
        ts = f"2026-08-07T12:{i:02d}:00Z"
        trend_val = 0.85 if i % 2 == 0 else 0.20
        ret_val = 0.004 if i % 2 == 0 else -0.001

        v_id, c_hash = compute_feature_vector_id(
            "VOLATILITY_100",
            "1m",
            ts,
            {"trend_strength": trend_val, "z_score": 1.2, "roc": 0.02},
        )
        fv = FeatureVector(
            vector_id=v_id,
            symbol="VOLATILITY_100",
            timeframe="1m",
            timestamp=ts,
            version="5.0.0",
            features={"trend_strength": trend_val, "z_score": 1.2, "roc": 0.02},
            checksum="CHK",
            metadata={},
            canonical_hash=c_hash,
        )
        fvs.append(fv)
        returns.append(ret_val)

    discovered = engine.discover_edges(
        symbol="VOLATILITY_100",
        timeframe="1m",
        feature_vectors=fvs,
        forward_returns=returns,
        min_pvalue=0.05,
        min_sample_size=5,
    )

    assert len(discovered) > 0
    top_edge = discovered[0]
    assert top_edge.edge_id.startswith("EDG_")
    assert top_edge.p_value <= 0.05
    assert top_edge.metrics.expected_value > 0.0
    assert top_edge.composite_score > 0.0

    # Query SQLite Edge Repository
    db_edge = engine.repository.get_edge(top_edge.edge_id)
    assert db_edge is not None
    assert db_edge.edge_id == top_edge.edge_id
    assert engine.repository.count() >= 1

    # Export Research Dataset
    dataset = engine.export_research_dataset(
        experiment_name="INTEGRATION_TEST_EXP",
        symbols=["VOLATILITY_100"],
        timeframes=["1m"],
        raw_inputs_count=100,
        feature_vectors=fvs,
        edges=discovered,
    )
    assert dataset.dataset_id.startswith("EXP_")
    assert dataset.edges_count == len(discovered)
