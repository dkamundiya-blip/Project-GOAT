"""
Project GOAT v0.9 — Dedicated Tests for Knowledge Graph Creation Engine
"""

import pytest

from goat.knowledge.core.enums import NodeType
from goat.knowledge.graph.engine import KnowledgeGraphEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
NODE_TYPES = list(NodeType)
LABEL_SUFFIXES = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("n_type", NODE_TYPES)
@pytest.mark.parametrize("suffix", LABEL_SUFFIXES[:3])
def test_knowledge_graph_engine_create_nodes_matrix(
    index_type: SyntheticIndexType, n_type: NodeType, suffix: str
) -> None:
    engine = KnowledgeGraphEngine()
    node = engine.create_node(
        node_type=n_type,
        entity_id=f"ENTITY_{index_type.value}_{suffix}",
        label=f"Node {index_type.value} {suffix}",
        timestamp_str="2026-01-01T00:00:00Z",
    )

    assert node.node_id.startswith("KND_")
    assert node.node_type == n_type
    assert node.entity_id == f"ENTITY_{index_type.value}_{suffix}"


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("size", [2, 5, 10, 20])
def test_knowledge_graph_engine_assemble_graph(
    index_type: SyntheticIndexType, size: int
) -> None:
    engine = KnowledgeGraphEngine()
    nodes = [
        engine.create_node(NodeType.HYPOTHESIS, f"HYP_{index_type.value}_{i}", f"Hypothesis {i}")
        for i in range(size)
    ]

    graph = engine.assemble_graph(
        graph_name=f"Graph_{index_type.value}_{size}",
        nodes=nodes,
        relationships=[],
        created_at_str="2026-01-01T00:00:00Z",
    )

    assert graph.graph_id.startswith("KGR_")
    assert len(graph.node_ids) == size
