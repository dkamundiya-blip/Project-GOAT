"""
Project GOAT v0.9 — Dedicated Tests for Knowledge Graph Traversal Engine
"""

import pytest

from goat.knowledge.core.enums import NodeType, PathValidity
from goat.knowledge.graph.engine import KnowledgeGraphEngine
from goat.knowledge.relationships.engine import RelationshipEngine
from goat.knowledge.traversal.engine import TraversalEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_graph_traversal_path_finding(index_type: SyntheticIndexType) -> None:
    g_engine = KnowledgeGraphEngine()
    r_engine = RelationshipEngine()
    t_engine = TraversalEngine()

    n1 = g_engine.create_node(NodeType.HYPOTHESIS, f"H_{index_type.value}", "Hypothesis")
    n2 = g_engine.create_node(NodeType.EVIDENCE, f"E_{index_type.value}", "Evidence")
    n3 = g_engine.create_node(NodeType.DISCOVERED_EDGE, f"D_{index_type.value}", "Edge")

    nodes = [n1, n2, n3]
    rels = r_engine.link_scientific_chain(nodes)

    paths = t_engine.find_paths(nodes, rels, n1.node_id, n3.node_id)
    assert len(paths) == 1
    path = paths[0]
    assert path.path_id.startswith("PTH_")
    assert path.source_node_id == n1.node_id
    assert path.target_node_id == n3.node_id
    assert path.path_length == 2
    assert path.validity == PathValidity.VALID_SCIENTIFIC_CHAIN


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_graph_traversal_ancestors_descendants(index_type: SyntheticIndexType) -> None:
    g_engine = KnowledgeGraphEngine()
    r_engine = RelationshipEngine()
    t_engine = TraversalEngine()

    n1 = g_engine.create_node(NodeType.HYPOTHESIS, f"H_{index_type.value}", "H")
    n2 = g_engine.create_node(NodeType.EVIDENCE, f"E_{index_type.value}", "E")
    n3 = g_engine.create_node(NodeType.EXPERIMENT, f"X_{index_type.value}", "X")

    nodes = [n1, n2, n3]
    rels = r_engine.link_scientific_chain(nodes)

    ancestors = t_engine.get_ancestors(nodes, rels, n3.node_id)
    assert len(ancestors) == 2
    ancestor_ids = {a.node_id for a in ancestors}
    assert n1.node_id in ancestor_ids
    assert n2.node_id in ancestor_ids

    descendants = t_engine.get_descendants(nodes, rels, n1.node_id)
    assert len(descendants) == 2
    descendant_ids = {d.node_id for d in descendants}
    assert n2.node_id in descendant_ids
    assert n3.node_id in descendant_ids
