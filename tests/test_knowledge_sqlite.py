"""
Project GOAT v0.9 — Dedicated Tests for Knowledge SQLite Repositories
"""

import sqlite3
import pytest

from goat.knowledge.core.canonical import (
    compute_knowledge_graph_id,
    compute_knowledge_node_id,
    compute_knowledge_relationship_id,
    compute_knowledge_summary_id,
    compute_relationship_validation_id,
    compute_scientific_path_id,
)
from goat.knowledge.core.enums import (
    NodeType,
    PathValidity,
    RelationshipType,
    ValidationStatus,
)
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
    KnowledgeSummary,
    RelationshipValidation,
    ScientificPath,
)
from goat.knowledge.persistence.sqlite import KnowledgePersistenceContext
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_sqlite_repository_roundtrips(index_type: SyntheticIndexType) -> None:
    db = KnowledgePersistenceContext(":memory:")

    # Check pragma
    cursor = db.conn.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1

    n1_id, n1_hash = compute_knowledge_node_id("HYPOTHESIS", f"HYP_{index_type.value}", "H")
    n1 = KnowledgeNode(
        node_id=n1_id,
        node_type=NodeType.HYPOTHESIS,
        entity_id=f"HYP_{index_type.value}",
        label="H",
        timestamp="2026-01-01T00:00:00Z",
        attributes={},
        canonical_hash=n1_hash,
    )
    db.nodes.save(n1)

    n2_id, n2_hash = compute_knowledge_node_id("EVIDENCE", f"EVD_{index_type.value}", "E")
    n2 = KnowledgeNode(
        node_id=n2_id,
        node_type=NodeType.EVIDENCE,
        entity_id=f"EVD_{index_type.value}",
        label="E",
        timestamp="2026-01-01T00:00:00Z",
        attributes={},
        canonical_hash=n2_hash,
    )
    db.nodes.save(n2)

    rel_id, rel_hash = compute_knowledge_relationship_id(n1_id, n2_id, "GENERATES_EVIDENCE")
    rel = KnowledgeRelationship(
        relationship_id=rel_id,
        source_node_id=n1_id,
        target_node_id=n2_id,
        relationship_type=RelationshipType.GENERATES_EVIDENCE,
        weight=1.0,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=rel_hash,
    )
    db.relationships.save(rel)

    g_id, g_hash = compute_knowledge_graph_id("G1", [n1_id, n2_id], [rel_id])
    graph = KnowledgeGraph(
        graph_id=g_id,
        graph_name="G1",
        node_ids=[n1_id, n2_id],
        relationship_ids=[rel_id],
        created_at="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=g_hash,
    )
    db.graphs.save(graph)

    p_id, p_hash = compute_scientific_path_id(n1_id, n2_id, [n1_id, n2_id])
    path = ScientificPath(
        path_id=p_id,
        source_node_id=n1_id,
        target_node_id=n2_id,
        node_chain=[n1_id, n2_id],
        relationship_chain=[rel_id],
        validity=PathValidity.VALID_SCIENTIFIC_CHAIN,
        path_length=1,
        metadata={},
        canonical_hash=p_hash,
    )
    db.traversals.save(path)

    v_id, v_hash = compute_relationship_validation_id(g_id, "VALID", "2026-01-01T00:00:00Z")
    val = RelationshipValidation(
        validation_id=v_id,
        graph_id=g_id,
        status=ValidationStatus.VALID,
        is_valid=True,
        broken_chain_count=0,
        orphan_node_count=0,
        cycle_count=0,
        duplicate_count=0,
        violations=[],
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=v_hash,
    )
    db.validations.save(val)

    s_id, s_hash = compute_knowledge_summary_id("2026-01-01T00:00:00Z", 2, 1)
    summary = KnowledgeSummary(
        summary_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        total_nodes=2,
        total_relationships=1,
        total_graphs=1,
        total_paths_analyzed=1,
        node_type_counts={"HYPOTHESIS": 1},
        relationship_type_counts={"GENERATES_EVIDENCE": 1},
        metadata={},
        canonical_hash=s_hash,
    )
    db.summaries.save(summary)

    # Retrieval verifications
    fetched_n = db.nodes.get_by_id(n1_id)
    assert fetched_n is not None
    assert fetched_n.node_id == n1_id
    assert fetched_n.canonical_hash == n1_hash

    fetched_r = db.relationships.get_by_id(rel_id)
    assert fetched_r is not None
    assert fetched_r.relationship_id == rel_id

    fetched_g = db.graphs.get_by_id(g_id)
    assert fetched_g is not None
    assert fetched_g.graph_id == g_id

    db.close()


def test_sqlite_foreign_key_enforcement() -> None:
    db = KnowledgePersistenceContext(":memory:")

    # Saving relationship with non-existent nodes raises IntegrityError
    rel = KnowledgeRelationship(
        relationship_id="REL_BOGUS",
        source_node_id="KND_BOGUS_1",
        target_node_id="KND_BOGUS_2",
        relationship_type=RelationshipType.GENERATES_EVIDENCE,
        weight=1.0,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash="HASH",
    )

    with pytest.raises(sqlite3.IntegrityError):
        db.relationships.save(rel)

    db.close()
