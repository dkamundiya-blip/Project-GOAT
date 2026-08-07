"""
Project GOAT Phase 6 — Unit Tests for Research Dataset Builder
"""

from goat.edge_discovery.dataset import ResearchDatasetBuilder
from goat.edge_discovery.models import DiscoveredEdge, EdgePerformanceMetrics, EdgeStatus, compute_edge_id
from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id


def test_research_dataset_builder():
    builder = ResearchDatasetBuilder()

    v_id, c_hash = compute_feature_vector_id("VOLATILITY_100", "1m", "2026-08-07T12:00:00Z", {"trend_direction": 1.0})
    fv = FeatureVector(
        vector_id=v_id,
        symbol="VOLATILITY_100",
        timeframe="1m",
        timestamp="2026-08-07T12:00:00Z",
        version="5.0.0",
        features={"trend_direction": 1.0},
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )

    metrics = EdgePerformanceMetrics(
        sample_size=10,
        win_rate=0.6,
        loss_rate=0.4,
        expected_value=0.001,
        average_return=0.001,
        median_return=0.001,
        max_gain=0.01,
        max_loss=-0.005,
        profit_factor=1.5,
        sharpe_ratio=1.8,
        sortino_ratio=2.0,
        calmar_ratio=2.5,
        max_drawdown=0.04,
        recovery_factor=3.0,
        trade_frequency=4.0,
        holding_period=5.0,
    )
    e_id, eh_hash = compute_edge_id("HYP_1", ["f1"], ["VOLATILITY_100"], ["1m"])
    edge = DiscoveredEdge(
        edge_id=e_id,
        version="6.0.0",
        hypothesis_id="HYP_1",
        feature_combination=["f1"],
        supported_symbols=["VOLATILITY_100"],
        supported_timeframes=["1m"],
        metrics=metrics,
        p_value=0.01,
        confidence_interval_low=0.0005,
        confidence_interval_high=0.0015,
        effect_size=0.6,
        composite_score=0.8,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash=eh_hash,
    )

    dataset = builder.build_dataset(
        experiment_name="EXP_QUANT_01",
        symbols=["VOLATILITY_100"],
        timeframes=["1m"],
        raw_inputs_count=100,
        feature_vectors=[fv],
        discovered_edges=[edge],
    )

    assert dataset.dataset_id.startswith("EXP_")
    assert dataset.experiment_name == "EXP_QUANT_01"
    assert dataset.edges_count == 1
    assert dataset.feature_vectors_count == 1
    assert "validation_summary" in dataset.model_dump()
