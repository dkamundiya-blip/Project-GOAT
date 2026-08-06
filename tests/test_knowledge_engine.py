"""
Project GOAT v0.9 — Dedicated Tests for Master Knowledge Engine
"""

import pytest

from goat.knowledge.core.enums import NodeType, RelationshipType, ValidationStatus
from goat.knowledge.engine import MasterKnowledgeEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_master_knowledge_engine_workflow(index_type: SyntheticIndexType) -> None:
    engine = MasterKnowledgeEngine(":memory:")

    n1 = engine.add_node(NodeType.HYPOTHESIS, f"HYP_{index_type.value}", "Hypothesis")
    n2 = engine.add_node(NodeType.EVIDENCE, f"EVD_{index_type.value}", "Evidence")

    rel = engine.add_relationship(n1.node_id, n2.node_id, RelationshipType.GENERATES_EVIDENCE)

    graph = engine.build_graph(f"Graph_{index_type.value}")
    assert graph.graph_id.startswith("KGR_")

    paths = engine.traverse_paths(n1.node_id, n2.node_id)
    assert len(paths) == 1

    validation = engine.validate_graph(graph.graph_id)
    assert validation.status == ValidationStatus.VALID

    summary = engine.generate_executive_summary()
    assert summary.summary_id.startswith("KSM_")
    assert summary.total_nodes >= 2
    assert summary.total_relationships >= 1

    engine.close()


def test_master_knowledge_multi_symbol() -> None:
    engine = MasterKnowledgeEngine(":memory:")
    symbols = ["VOLATILITY_10", "BOOM_1000", "CRASH_500", "JUMP_75", "STEP_INDEX"]

    for sym in symbols:
        h = engine.add_node(NodeType.HYPOTHESIS, f"HYP_{sym}", f"Hypothesis {sym}")
        e = engine.add_node(NodeType.EVIDENCE, f"EVD_{sym}", f"Evidence {sym}")
        engine.add_relationship(h.node_id, e.node_id, RelationshipType.GENERATES_EVIDENCE)

    graph = engine.build_graph("MultiSymbolGraph")
    assert len(graph.node_ids) == 10
    assert len(graph.relationship_ids) == 5

    summary = engine.generate_executive_summary()
    assert summary.total_nodes == 10
    assert summary.total_relationships == 5

    engine.close()
