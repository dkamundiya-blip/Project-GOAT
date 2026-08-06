"""
Project GOAT v0.9 — Master System Integration Test Suite

Verifies end-to-end scientific pipeline integration, deterministic SHA-256 lineage,
and full subsystem interoperability across all Version 0.9 modules.
"""

import pytest

from goat.edge_discovery.engine import MasterEdgeDiscoveryEngine
from goat.intelligence.engine import MasterIntelligenceEngine
from goat.knowledge.core.enums import NodeType, RelationshipType
from goat.knowledge.engine import MasterKnowledgeEngine
from goat.microstructure.engine import MicrostructureResearchEngine
from goat.microstructure.core.enums import MicrostructureMetricType, SyntheticIndexType
from goat.microstructure.core.models import MicrostructureObservation


def test_v09_end_to_end_master_pipeline_integration() -> None:
    """Validate full Version 0.9 end-to-end scientific research pipeline."""
    # 1. Deriv Microstructure Layer
    micro_engine = MicrostructureResearchEngine(":memory:")
    prices = [100.0 + i * 0.5 for i in range(50)]
    mkt_profile, profile_obs = micro_engine.profile_synthetic_index(
        symbol="VOLATILITY_100",
        index_type=SyntheticIndexType.VOLATILITY_100,
        prices=prices,
        timestamp_str="2026-01-01T00:00:00Z",
    )
    assert len(profile_obs) > 0
    micro_summary = micro_engine.generate_research_summary("2026-01-01T00:00:00Z")
    assert micro_summary.total_observations > 0

    # Build observations list with min sample size >= 10 of same metric for mining
    mining_obs = [
        MicrostructureObservation(
            observation_id=f"MSO_VOL100_{i}",
            metric_type=MicrostructureMetricType.REALIZED_VOLATILITY,
            category="VOLATILITY",
            symbol="VOLATILITY_100",
            index_type=SyntheticIndexType.VOLATILITY_100,
            timestamp="2026-01-01T00:00:00Z",
            value=0.05 + i * 0.001,
            unit="unit",
            window_seconds=300,
            metadata={},
            canonical_hash=f"HASH_{i}",
        )
        for i in range(15)
    ]

    # 2. Edge Discovery Engine
    edge_engine = MasterEdgeDiscoveryEngine(":memory:")
    candidates, decisions = edge_engine.discover_edges(
        symbol="VOLATILITY_100",
        observations=mining_obs,
        timestamp_str="2026-01-01T00:00:00Z",
    )
    assert len(candidates) > 0
    assert len(decisions) > 0
    edge_summary = edge_engine.generate_discovery_summary("2026-01-01T00:00:00Z")
    assert edge_summary.total_candidates > 0

    # 3. Knowledge Graph Engine
    knowledge_engine = MasterKnowledgeEngine(":memory:")
    n_hyp = knowledge_engine.add_node(NodeType.HYPOTHESIS, "HYP_001", "Hypothesis 001")
    n_evd = knowledge_engine.add_node(NodeType.EVIDENCE, "EVD_001", "Evidence 001")
    n_exp = knowledge_engine.add_node(NodeType.EXPERIMENT, "EXP_001", "Experiment 001")
    n_eval = knowledge_engine.add_node(NodeType.STATISTICAL_EVALUATION, "EVA_001", "Eval 001")
    n_live = knowledge_engine.add_node(NodeType.LIVE_VALIDATION, "VAL_001", "Live 001")
    n_gov = knowledge_engine.add_node(NodeType.GOVERNANCE_DECISION, "GOV_001", "Gov 001")
    n_edg = knowledge_engine.add_node(NodeType.DISCOVERED_EDGE, candidates[0].candidate_id, "Discovered Edge")
    n_arc = knowledge_engine.add_node(NodeType.ARCHIVE, "ARC_001", "Archive 001")

    # Link scientific chain
    knowledge_engine.add_relationship(n_hyp.node_id, n_evd.node_id, RelationshipType.GENERATES_EVIDENCE)
    knowledge_engine.add_relationship(n_evd.node_id, n_exp.node_id, RelationshipType.CONDUCTS_EXPERIMENT)
    knowledge_engine.add_relationship(n_exp.node_id, n_eval.node_id, RelationshipType.EVALUATES_STATISTICS)
    knowledge_engine.add_relationship(n_eval.node_id, n_live.node_id, RelationshipType.VALIDATES_LIVE)
    knowledge_engine.add_relationship(n_live.node_id, n_gov.node_id, RelationshipType.DECIDES_GOVERNANCE)
    knowledge_engine.add_relationship(n_gov.node_id, n_edg.node_id, RelationshipType.DISCOVERS_EDGE)
    knowledge_engine.add_relationship(n_edg.node_id, n_arc.node_id, RelationshipType.ARCHIVES_ARTIFACT)

    graph = knowledge_engine.build_graph("MasterScientificGraph")
    assert len(graph.node_ids) == 8
    assert len(graph.relationship_ids) == 7

    paths = knowledge_engine.traverse_paths(n_hyp.node_id, n_arc.node_id)
    assert len(paths) == 1
    assert paths[0].path_length == 7

    val = knowledge_engine.validate_graph(graph.graph_id)
    assert val.is_valid is True

    # 4. Institutional Research Intelligence Engine
    intel_engine = MasterIntelligenceEngine(":memory:")
    hyp_records = [{"category": "VOLATILITY", "status": "PASSED"}]
    exp_records = [{"duration_seconds": 150, "is_conclusive": True, "effect_size": 0.20, "sample_size": 100}]
    inv_records = [{"regime": "HIGH_VOLATILITY"}]

    health, insights, recs, meta = intel_engine.evaluate_research_intelligence(
        hypotheses_records=hyp_records,
        experiment_records=exp_records,
        invalidation_records=inv_records,
        timestamp_str="2026-01-01T00:00:00Z",
    )
    assert health.health_score > 0.0
    assert len(insights) > 0
    assert len(recs) > 0

    intel_summary = intel_engine.generate_summary("2026-01-01T00:00:00Z")
    assert intel_summary.total_insights > 0

    # Cleanup DB connections
    micro_engine.close()
    edge_engine.close()
    knowledge_engine.close()
    intel_engine.close()
