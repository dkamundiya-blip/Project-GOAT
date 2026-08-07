"""
Unit tests for ResearchQueryEngine answering deterministic research questions.
"""

from goat.ai_reasoning.knowledge_graph.engine import ResearchKnowledgeGraph
from goat.ai_reasoning.query.engine import ResearchQueryEngine
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
)
from goat.edge_discovery.persistence.in_memory import InMemoryEdgeRepository


def test_research_query_engine():
    repo = InMemoryEdgeRepository()
    kg = ResearchKnowledgeGraph()

    e1 = DiscoveredEdge(
        edge_id="EDG_0000000000000001",
        version="6.0.0",
        hypothesis_id="HYP_0000000000000001",
        feature_combination=["trend_strength"],
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
        composite_score=0.90,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={"HIGH_VOLATILITY": {"sample_size": 50, "expected_value": 0.006, "sharpe_ratio": 2.8}},
        walk_forward_metrics={"degradation_ratio": 0.9},
        checksum="CHK",
        metadata={},
        canonical_hash="HASH",
    )
    repo.save_edge(e1)
    kg.ingest_discovered_edge(e1)

    query_engine = ResearchQueryEngine(knowledge_graph=kg, edge_repository=repo)

    # 1. Why ranked first?
    rank_res = query_engine.why_is_edge_ranked_first()
    assert rank_res["edge_id"] == "EDG_0000000000000001"
    assert rank_res["rank"] == 1
    assert len(rank_res["reasons"]) > 0

    # 2. Which market strongest edge?
    mkt_res = query_engine.which_market_strongest_edge()
    assert mkt_res["symbol"] == "BOOM_1000"
    assert mkt_res["edge_id"] == "EDG_0000000000000001"

    # 3. High Volatility Edges
    vol_edges = query_engine.show_edges_valid_during_regime("HIGH_VOLATILITY")
    assert len(vol_edges) == 1
    assert vol_edges[0]["edge_id"] == "EDG_0000000000000001"

    # 4. Boom 1000 Edges
    boom_edges = query_engine.find_edges_for_symbol("BOOM_1000")
    assert len(boom_edges) == 1
    assert boom_edges[0]["edge_id"] == "EDG_0000000000000001"

    # 5. Failed hypothesis breakdown
    failed_res = query_engine.explain_why_hypothesis_failed("HYP_9999999999999999")
    assert failed_res["status"] == "REJECTED"
    assert len(failed_res["failure_reasons"]) > 0
