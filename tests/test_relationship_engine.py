"""
Project GOAT v0.9 — Dedicated Tests for Scientific Relationship Engine
"""

import pytest

from goat.knowledge.core.enums import NodeType, RelationshipType
from goat.knowledge.graph.engine import KnowledgeGraphEngine
from goat.knowledge.relationships.engine import RelationshipEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
REL_TYPES = list(RelationshipType)
WEIGHTS = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("r_type", REL_TYPES)
@pytest.mark.parametrize("w_val", WEIGHTS[:4])
def test_relationship_engine_create_relationship_matrix(
    index_type: SyntheticIndexType, r_type: RelationshipType, w_val: float
) -> None:
    rel_engine = RelationshipEngine()

    src_id = f"KND_{index_type.value}_SRC"
    tgt_id = f"KND_{index_type.value}_TGT"

    rel = rel_engine.create_relationship(
        source_node_id=src_id,
        target_node_id=tgt_id,
        relationship_type=r_type,
        weight=w_val,
    )

    assert rel.relationship_id.startswith("REL_")
    assert rel.source_node_id == src_id
    assert rel.target_node_id == tgt_id
    assert rel.relationship_type == r_type
    assert rel.weight == w_val


@pytest.mark.parametrize("index_type", INDICES)
def test_relationship_engine_scientific_chain(index_type: SyntheticIndexType) -> None:
    g_engine = KnowledgeGraphEngine()
    r_engine = RelationshipEngine()

    nodes = [
        g_engine.create_node(NodeType.HYPOTHESIS, f"HYP_{index_type.value}", "Hypothesis"),
        g_engine.create_node(NodeType.EVIDENCE, f"EVD_{index_type.value}", "Evidence"),
        g_engine.create_node(NodeType.EXPERIMENT, f"EXP_{index_type.value}", "Experiment"),
        g_engine.create_node(NodeType.STATISTICAL_EVALUATION, f"EVA_{index_type.value}", "Eval"),
        g_engine.create_node(NodeType.LIVE_VALIDATION, f"VAL_{index_type.value}", "Live"),
        g_engine.create_node(NodeType.GOVERNANCE_DECISION, f"GOV_{index_type.value}", "Gov"),
        g_engine.create_node(NodeType.DISCOVERED_EDGE, f"EDG_{index_type.value}", "Edge"),
        g_engine.create_node(NodeType.ARCHIVE, f"ARC_{index_type.value}", "Archive"),
    ]

    rels = r_engine.link_scientific_chain(nodes)
    assert len(rels) == 7
    assert rels[0].relationship_type == RelationshipType.GENERATES_EVIDENCE
    assert rels[1].relationship_type == RelationshipType.CONDUCTS_EXPERIMENT
    assert rels[2].relationship_type == RelationshipType.EVALUATES_STATISTICS
    assert rels[3].relationship_type == RelationshipType.VALIDATES_LIVE
    assert rels[4].relationship_type == RelationshipType.DECIDES_GOVERNANCE
    assert rels[5].relationship_type == RelationshipType.DISCOVERS_EDGE
    assert rels[6].relationship_type == RelationshipType.ARCHIVES_ARTIFACT
