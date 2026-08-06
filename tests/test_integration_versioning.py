"""
Project GOAT v0.7 — Test Suite for Knowledge Evolution & Versioning Engine

Coverage:
- Version snapshot creation (KnowledgeStateVersion)
- Sequential version numbering
- Parent version tracking
- Version retrieval and listing
- Forward and backward state replay
- Evolution history serialization
"""

import pytest

from goat.integration.core.canonical import compute_integrated_knowledge_id, compute_node_id
from goat.integration.core.enums import KnowledgeNodeType
from goat.integration.core.models import IntegratedKnowledge, KnowledgeNode
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.integration.versioning import KnowledgeEvolutionEngine, KnowledgeStateVersion


def test_evolution_version_creation():
    engine = KnowledgeEvolutionEngine()
    graph = ScientificKnowledgeGraph()

    n_id, n_hash, fp = compute_node_id("Node Title", "VALIDATION", "VAL_1")
    node = KnowledgeNode(
        node_id=n_id,
        title="Node Title",
        node_type=KnowledgeNodeType.VALIDATION,
        originating_validation="VAL_1",
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=n_hash,
        fingerprint=fp,
    )
    graph.add_node(node)

    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["VAL_1"],
        participating_hypotheses=["HYP_1"],
        participating_experiments=["EXP_1"],
        overall_confidence=0.85,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )

    v1 = engine.create_version(ik, graph, "2026-07-30T00:00:00Z")

    assert v1.version_id.startswith("KVR_")
    assert v1.version_number == 1
    assert v1.knowledge_id == ik_id
    assert v1.parent_version_id == ""


def test_evolution_version_chaining():
    engine = KnowledgeEvolutionEngine()
    graph = ScientificKnowledgeGraph()

    n_id, n_hash, fp = compute_node_id("Node Title", "VALIDATION", "VAL_1")
    node = KnowledgeNode(
        node_id=n_id,
        title="Node Title",
        node_type=KnowledgeNodeType.VALIDATION,
        originating_validation="VAL_1",
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=n_hash,
        fingerprint=fp,
    )
    graph.add_node(node)

    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["VAL_1"],
        participating_hypotheses=["HYP_1"],
        participating_experiments=["EXP_1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )

    v1 = engine.create_version(ik, graph, "2026-07-30T00:00:00Z")
    v2 = engine.create_version(ik, graph, "2026-07-30T01:00:00Z", parent_version_id=v1.version_id)

    assert v2.version_number == 2
    assert v2.parent_version_id == v1.version_id

    versions = engine.list_versions_for_knowledge(ik_id)
    assert len(versions) == 2
    assert versions[0] == v1
    assert versions[1] == v2


def test_evolution_state_replay():
    engine = KnowledgeEvolutionEngine()
    graph = ScientificKnowledgeGraph()

    n_id, n_hash, fp = compute_node_id("Node Title", "VALIDATION", "VAL_1")
    node = KnowledgeNode(
        node_id=n_id,
        title="Node Title",
        node_type=KnowledgeNodeType.VALIDATION,
        originating_validation="VAL_1",
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=n_hash,
        fingerprint=fp,
    )
    graph.add_node(node)

    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["VAL_1"],
        participating_hypotheses=["HYP_1"],
        participating_experiments=["EXP_1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )

    v1 = engine.create_version(ik, graph, "2026-07-30T00:00:00Z")
    replayed_ik, replayed_graph = engine.replay_version(v1.version_id)

    assert replayed_ik == ik
    assert replayed_graph.get_nodes() == graph.get_nodes()


def test_evolution_invalid_replay():
    engine = KnowledgeEvolutionEngine()
    with pytest.raises(KeyError):
        engine.replay_version("KVR_NONEXISTENT")
