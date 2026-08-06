"""
Project GOAT v0.7 — Test Suite for Scientific Knowledge Graph Engine

Coverage:
- Node management (add, lookup, duplicate checks, errors)
- Edge management (add, lookup, remove, orphan checks, duplicate errors)
- Evidence lookup across nodes & edges
- Relationship queries (outgoing, incoming, both)
- Neighborhood queries with hop depth limits
- Deterministic traversal (BFS and DFS)
- Canonical JSON serialization & deserialization
- Event replay (add node/edge, remove edge)
"""

import pytest

from goat.integration.core.canonical import compute_edge_id, compute_node_id
from goat.integration.core.enums import KnowledgeNodeType, KnowledgeRelationship
from goat.integration.core.models import KnowledgeEdge, KnowledgeNode
from goat.integration.graph.engine import ScientificKnowledgeGraph


def create_sample_node(node_name: str, n_type: str = "HYPOTHESIS") -> KnowledgeNode:
    n_id, n_hash, fp = compute_node_id(node_name, n_type, f"VAL_{node_name}")
    return KnowledgeNode(
        node_id=n_id,
        title=node_name,
        node_type=KnowledgeNodeType(n_type),
        description=f"Description for {node_name}",
        originating_validation=f"VAL_{node_name}",
        creation_timestamp="2026-07-30T00:00:00Z",
        metadata={"evidence_ids": [f"EV_{node_name}"]},
        canonical_hash=n_hash,
        fingerprint=fp,
    )


def create_sample_edge(src: KnowledgeNode, dst: KnowledgeNode, rel: str = "SUPPORTS") -> KnowledgeEdge:
    e_id, e_hash = compute_edge_id(src.node_id, dst.node_id, rel)
    return KnowledgeEdge(
        edge_id=e_id,
        source_node=src.node_id,
        destination_node=dst.node_id,
        relationship=KnowledgeRelationship(rel),
        confidence=0.9,
        supporting_evidence=[f"EV_{src.title}_{dst.title}"],
        canonical_hash=e_hash,
    )


def test_graph_add_and_lookup_node():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    graph.add_node(n1)

    assert graph.lookup_node(n1.node_id) == n1
    assert len(graph.get_nodes()) == 1


def test_graph_add_duplicate_node_identical():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    graph.add_node(n1)
    graph.add_node(n1)  # Idempotent re-add
    assert len(graph.get_nodes()) == 1


def test_graph_add_duplicate_node_conflicting():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    graph.add_node(n1)

    # Conflicting node with same ID but different title
    n1_conflict = KnowledgeNode(
        node_id=n1.node_id,
        title="Different Title",
        node_type=n1.node_type,
        originating_validation=n1.originating_validation,
        creation_timestamp=n1.creation_timestamp,
    )
    with pytest.raises(ValueError):
        graph.add_node(n1_conflict)


def test_graph_add_edge_missing_nodes():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    edge = create_sample_edge(n1, n2)

    with pytest.raises(KeyError):
        graph.add_edge(edge)


def test_graph_add_and_lookup_edge():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    graph.add_node(n1)
    graph.add_node(n2)

    edge = create_sample_edge(n1, n2)
    graph.add_edge(edge)

    assert graph.lookup_edge(edge.edge_id) == edge
    assert len(graph.get_edges()) == 1


def test_graph_remove_edge():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    graph.add_node(n1)
    graph.add_node(n2)

    edge = create_sample_edge(n1, n2)
    graph.add_edge(edge)

    assert graph.remove_edge(edge.edge_id) is True
    assert graph.lookup_edge(edge.edge_id) is None
    assert graph.remove_edge(edge.edge_id) is False


def test_graph_lookup_evidence():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    graph.add_node(n1)
    graph.add_node(n2)
    edge = create_sample_edge(n1, n2)
    graph.add_edge(edge)

    evidence_n1 = graph.lookup_evidence(n1.node_id)
    assert f"EV_{n1.title}" in evidence_n1
    assert n1.originating_validation in evidence_n1

    evidence_edge = graph.lookup_evidence(edge.edge_id)
    assert f"EV_{n1.title}_{n2.title}" in evidence_edge


def test_graph_lookup_relationships():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    n3 = create_sample_node("Node 3")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    e12 = create_sample_edge(n1, n2, "SUPPORTS")
    e31 = create_sample_edge(n3, n1, "EXTENDS")
    graph.add_edge(e12)
    graph.add_edge(e31)

    out_n1 = graph.lookup_relationships(n1.node_id, direction="outgoing")
    assert out_n1 == [e12]

    in_n1 = graph.lookup_relationships(n1.node_id, direction="incoming")
    assert in_n1 == [e31]

    both_n1 = graph.lookup_relationships(n1.node_id, direction="both")
    assert len(both_n1) == 2


def test_graph_neighborhood_queries():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    n3 = create_sample_node("Node 3")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    e12 = create_sample_edge(n1, n2)
    e23 = create_sample_edge(n2, n3)
    graph.add_edge(e12)
    graph.add_edge(e23)

    neigh_d1 = graph.neighborhood_queries(n1.node_id, depth=1)
    assert len(neigh_d1["nodes"]) == 2
    assert len(neigh_d1["edges"]) == 1

    neigh_d2 = graph.neighborhood_queries(n1.node_id, depth=2)
    assert len(neigh_d2["nodes"]) == 3
    assert len(neigh_d2["edges"]) == 2


def test_graph_traversal_bfs_dfs():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    n3 = create_sample_node("Node 3")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    e12 = create_sample_edge(n1, n2)
    e13 = create_sample_edge(n1, n3)
    graph.add_edge(e12)
    graph.add_edge(e13)

    bfs_order = graph.traversal(n1.node_id, max_depth=5, mode="bfs")
    assert bfs_order[0] == n1.node_id
    assert len(bfs_order) == 3

    dfs_order = graph.traversal(n1.node_id, max_depth=5, mode="dfs")
    assert dfs_order[0] == n1.node_id
    assert len(dfs_order) == 3


def test_graph_serialization_round_trip():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    graph.add_node(n1)
    graph.add_node(n2)
    edge = create_sample_edge(n1, n2)
    graph.add_edge(edge)

    json_str = graph.serialize()
    restored = ScientificKnowledgeGraph.deserialize(json_str)

    assert restored.get_nodes() == graph.get_nodes()
    assert restored.get_edges() == graph.get_edges()


def test_graph_event_replay():
    graph = ScientificKnowledgeGraph()
    n1 = create_sample_node("Node 1")
    n2 = create_sample_node("Node 2")
    edge = create_sample_edge(n1, n2)

    events = [
        {"event_type": "ADD_NODE", "payload": n1.dict()},
        {"event_type": "ADD_NODE", "payload": n2.dict()},
        {"event_type": "ADD_EDGE", "payload": edge.dict()},
        {"event_type": "REMOVE_EDGE", "payload": {"edge_id": edge.edge_id}},
    ]

    graph.replay_events(events)

    assert len(graph.get_nodes()) == 2
    assert len(graph.get_edges()) == 0
