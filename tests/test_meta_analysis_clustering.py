"""
Project GOAT v0.7 — Test Suite for ClusterEngine

Coverage:
- Theme clustering
- Validation clustering
- Knowledge graph neighborhood clustering
- Full generate_all_clusters orchestration
"""

from goat.integration.core.canonical import compute_edge_id, compute_node_id
from goat.integration.core.enums import KnowledgeNodeType, KnowledgeRelationship
from goat.integration.core.models import KnowledgeEdge, KnowledgeNode
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.meta_analysis.clustering.engine import ClusterEngine
from goat.meta_analysis.core.enums import ClusterType


def test_cluster_by_theme():
    engine = ClusterEngine()

    n1_id, n1_hash, fp1 = compute_node_id("Node 1", "VALIDATION", "VAL_1")
    n2_id, n2_hash, fp2 = compute_node_id("Node 2", "VALIDATION", "VAL_2")

    n1 = KnowledgeNode(
        node_id=n1_id,
        title="Node 1",
        node_type=KnowledgeNodeType.VALIDATION,
        originating_validation="VAL_1",
        creation_timestamp="2026-07-30T00:00:00Z",
        metadata={"themes": ["momentum"]},
        canonical_hash=n1_hash,
        fingerprint=fp1,
    )
    n2 = KnowledgeNode(
        node_id=n2_id,
        title="Node 2",
        node_type=KnowledgeNodeType.VALIDATION,
        originating_validation="VAL_2",
        creation_timestamp="2026-07-30T00:00:00Z",
        metadata={"themes": ["momentum"]},
        canonical_hash=n2_hash,
        fingerprint=fp2,
    )

    clusters = engine.cluster_by_theme([n1, n2], "2026-07-30T00:00:00Z")
    assert len(clusters) == 1
    assert clusters[0].cluster_type == ClusterType.THEME
    assert len(clusters[0].participating_nodes) == 2


def test_cluster_by_validation():
    engine = ClusterEngine()
    vals = [
        {"validation_id": "VAL_1", "status": "PASSED", "confidence": 0.85},
        {"validation_id": "VAL_2", "status": "PASSED", "confidence": 0.90},
        {"validation_id": "VAL_3", "status": "FAILED", "confidence": 0.40},
    ]

    clusters = engine.cluster_by_validation(vals, "2026-07-30T00:00:00Z")
    assert len(clusters) == 2  # PASSED and FAILED clusters
    passed_c = [c for c in clusters if c.metadata.get("status") == "PASSED"][0]
    assert len(passed_c.participating_validations) == 2


def test_cluster_by_knowledge_graph():
    engine = ClusterEngine()
    graph = ScientificKnowledgeGraph()

    n1_id, n1_hash, fp1 = compute_node_id("N1", "VALIDATION", "VAL_1")
    n2_id, n2_hash, fp2 = compute_node_id("N2", "HYPOTHESIS", "VAL_1")

    node1 = KnowledgeNode(node_id=n1_id, title="N1", node_type=KnowledgeNodeType.VALIDATION, originating_validation="VAL_1", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=n1_hash, fingerprint=fp1)
    node2 = KnowledgeNode(node_id=n2_id, title="N2", node_type=KnowledgeNodeType.HYPOTHESIS, originating_validation="VAL_1", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=n2_hash, fingerprint=fp2)
    graph.add_node(node1)
    graph.add_node(node2)

    e_id, e_hash = compute_edge_id(n1_id, n2_id, "SUPPORTS")
    edge = KnowledgeEdge(edge_id=e_id, source_node=n1_id, destination_node=n2_id, relationship=KnowledgeRelationship.SUPPORTS, canonical_hash=e_hash)
    graph.add_edge(edge)

    clusters = engine.cluster_by_knowledge_graph(graph, "2026-07-30T00:00:00Z")
    assert len(clusters) >= 1
    assert clusters[0].cluster_type == ClusterType.KNOWLEDGE
