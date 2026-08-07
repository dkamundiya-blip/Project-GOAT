"""
Unit tests for ResearchKnowledgeGraph functionality.
"""

from goat.ai_reasoning.knowledge_graph.engine import ResearchKnowledgeGraph
from goat.ai_reasoning.models import EdgeType, NodeType
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
    compute_edge_id,
)


def test_knowledge_graph_node_and_edge_operations():
    kg = ResearchKnowledgeGraph()

    e_edge = DiscoveredEdge(
        edge_id="EDG_0000000000000001",
        version="6.0.0",
        hypothesis_id="HYP_0000000000000001",
        feature_combination=["trend_strength", "volatility_expansion"],
        supported_symbols=["BOOM_1000"],
        supported_timeframes=["1m"],
        metrics=EdgePerformanceMetrics(
            sample_size=100,
            win_rate=0.6,
            loss_rate=0.4,
            expected_value=0.005,
            average_return=0.005,
            median_return=0.004,
            max_gain=0.02,
            max_loss=0.01,
            profit_factor=2.0,
            sharpe_ratio=2.5,
            sortino_ratio=3.0,
            calmar_ratio=4.0,
            max_drawdown=0.05,
            recovery_factor=5.0,
            trade_frequency=10.0,
            holding_period=5.0,
        ),
        p_value=0.01,
        confidence_interval_low=0.002,
        confidence_interval_high=0.008,
        effect_size=0.8,
        composite_score=0.85,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={"HIGH_VOLATILITY": {"sample_size": 50, "expected_value": 0.006}},
        walk_forward_metrics={"degradation_ratio": 0.9},
        checksum="CHK",
        metadata={},
        canonical_hash="HASH",
    )

    node = kg.ingest_discovered_edge(e_edge)
    assert node is not None
    assert kg.node_count() > 0
    assert kg.edge_count() > 0

    feature_nodes = kg.find_nodes_by_type(NodeType.FEATURE)
    assert len(feature_nodes) == 2

    symbol_nodes = kg.find_nodes_by_type(NodeType.SYMBOL)
    assert len(symbol_nodes) == 1
    assert symbol_nodes[0].name == "BOOM_1000"

    regime_nodes = kg.find_nodes_by_type(NodeType.REGIME)
    assert len(regime_nodes) == 1
    assert regime_nodes[0].name == "HIGH_VOLATILITY"

    neighbors = kg.query_neighbors(node.node_id, edge_type=EdgeType.DERIVED_FROM)
    assert len(neighbors) == 2
