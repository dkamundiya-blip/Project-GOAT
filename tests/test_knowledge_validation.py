"""
Project GOAT v0.9 — Dedicated Tests for Knowledge Validation Engine
"""

import pytest

from goat.knowledge.core.enums import NodeType, RelationshipType, ValidationStatus
from goat.knowledge.graph.engine import KnowledgeGraphEngine
from goat.knowledge.relationships.engine import RelationshipEngine
from goat.knowledge.validation.engine import ValidationEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_validation_engine_valid_graph(index_type: SyntheticIndexType) -> None:
    g_engine = KnowledgeGraphEngine()
    r_engine = RelationshipEngine()
    v_engine = ValidationEngine()

    n1 = g_engine.create_node(NodeType.HYPOTHESIS, f"H_{index_type.value}", "Hypothesis")
    n2 = g_engine.create_node(NodeType.EVIDENCE, f"E_{index_type.value}", "Evidence")

    nodes = [n1, n2]
    rels = r_engine.link_scientific_chain(nodes)

    val = v_engine.validate_graph("KGR_1", nodes, rels)
    assert val.validation_id.startswith("VAL_")
    assert val.status == ValidationStatus.VALID
    assert val.is_valid is True
    assert len(val.violations) == 0


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_validation_engine_orphan_nodes(index_type: SyntheticIndexType) -> None:
    g_engine = KnowledgeGraphEngine()
    v_engine = ValidationEngine()

    orphan = g_engine.create_node(NodeType.HYPOTHESIS, f"H_{index_type.value}", "Orphan")
    val = v_engine.validate_graph("KGR_1", [orphan], [])

    assert val.status == ValidationStatus.ORPHAN_NODE
    assert val.is_valid is False
    assert val.orphan_node_count == 1


@pytest.mark.parametrize("index_type", INDICES[:5])
def test_validation_engine_duplicate_relationships(index_type: SyntheticIndexType) -> None:
    g_engine = KnowledgeGraphEngine()
    r_engine = RelationshipEngine()
    v_engine = ValidationEngine()

    n1 = g_engine.create_node(NodeType.HYPOTHESIS, f"H_{index_type.value}", "H")
    n2 = g_engine.create_node(NodeType.EVIDENCE, f"E_{index_type.value}", "E")

    r1 = r_engine.create_relationship(n1.node_id, n2.node_id, RelationshipType.GENERATES_EVIDENCE)
    r2 = r_engine.create_relationship(n1.node_id, n2.node_id, RelationshipType.GENERATES_EVIDENCE)

    val = v_engine.validate_graph("KGR_1", [n1, n2], [r1, r2])
    assert val.status == ValidationStatus.DUPLICATE_RELATIONSHIP
    assert val.is_valid is False
    assert val.duplicate_count == 1
