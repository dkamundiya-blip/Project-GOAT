"""
Project GOAT v0.9 — Dedicated Tests for Knowledge Models & Canonical Hashing
"""

import pytest
from pydantic import ValidationError

from goat.knowledge.core.canonical import (
    compute_canonical_sha256,
    compute_knowledge_graph_id,
    compute_knowledge_node_id,
    compute_knowledge_relationship_id,
    compute_knowledge_summary_id,
    compute_relationship_validation_id,
    compute_scientific_path_id,
    serialize_canonical_json,
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
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
NODE_TYPES = list(NodeType)
REL_TYPES = list(RelationshipType)
VAL_STATUSES = list(ValidationStatus)
PATH_VALIDITIES = list(PathValidity)
VERSIONS = ["1.0.0", "1.1.0", "2.0.0"]


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("n_type", NODE_TYPES)
@pytest.mark.parametrize("label_idx", range(50))
def test_knowledge_node_model_matrix(
    index_type: SyntheticIndexType, n_type: NodeType, label_idx: int
) -> None:
    entity_id = f"ENT_{index_type.value}_{label_idx}"
    label = f"Label {index_type.value} {label_idx}"
    node_id, h_digest = compute_knowledge_node_id(n_type.value, entity_id, label)

    node = KnowledgeNode(
        node_id=node_id,
        node_type=n_type,
        entity_id=entity_id,
        label=label,
        timestamp="2026-01-01T00:00:00Z",
        attributes={"sym": index_type.value},
        canonical_hash=h_digest,
    )

    assert node.node_id.startswith("KND_")
    assert node.canonical_hash == h_digest
    assert node.node_type == n_type
    assert node.entity_id == entity_id

    with pytest.raises(ValidationError):
        node.label = "Modified"  # type: ignore


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("r_type", REL_TYPES)
@pytest.mark.parametrize("w_val", [0.1, 0.5, 0.9, 1.0, 2.0])
def test_knowledge_relationship_model_matrix(
    index_type: SyntheticIndexType, r_type: RelationshipType, w_val: float
) -> None:
    src_id = f"KND_{index_type.value}_SRC"
    tgt_id = f"KND_{index_type.value}_TGT"
    rel_id, h_digest = compute_knowledge_relationship_id(src_id, tgt_id, r_type.value)

    rel = KnowledgeRelationship(
        relationship_id=rel_id,
        source_node_id=src_id,
        target_node_id=tgt_id,
        relationship_type=r_type,
        weight=w_val,
        timestamp="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=h_digest,
    )

    assert rel.relationship_id.startswith("REL_")
    assert rel.canonical_hash == h_digest
    assert rel.relationship_type == r_type


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("size", [1, 5, 10, 20, 50])
def test_knowledge_graph_model(index_type: SyntheticIndexType, size: int) -> None:
    g_name = f"Graph_{index_type.value}_{size}"
    n_ids = [f"KND_{i}" for i in range(size)]
    r_ids = [f"REL_{i}" for i in range(size)]
    g_id, h_digest = compute_knowledge_graph_id(g_name, n_ids, r_ids)

    graph = KnowledgeGraph(
        graph_id=g_id,
        graph_name=g_name,
        node_ids=n_ids,
        relationship_ids=r_ids,
        created_at="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=h_digest,
    )

    assert graph.graph_id.startswith("KGR_")
    assert graph.canonical_hash == h_digest


@pytest.mark.parametrize("validity", PATH_VALIDITIES)
@pytest.mark.parametrize("length", [1, 2, 5, 10, 25])
def test_scientific_path_model(validity: PathValidity, length: int) -> None:
    n_chain = [f"KND_{i}" for i in range(length + 1)]
    p_id, h_digest = compute_scientific_path_id("KND_SRC", f"KND_{length}", n_chain)

    path = ScientificPath(
        path_id=p_id,
        source_node_id="KND_SRC",
        target_node_id=f"KND_{length}",
        node_chain=n_chain,
        relationship_chain=[f"REL_{i}" for i in range(length)],
        validity=validity,
        path_length=length,
        metadata={},
        canonical_hash=h_digest,
    )

    assert path.path_id.startswith("PTH_")
    assert path.canonical_hash == h_digest


@pytest.mark.parametrize("status", VAL_STATUSES)
@pytest.mark.parametrize("is_val", [True, False])
@pytest.mark.parametrize("ver", VERSIONS)
def test_relationship_validation_model(status: ValidationStatus, is_val: bool, ver: str) -> None:
    v_id, h_digest = compute_relationship_validation_id("KGR_1", status.value, "2026-01-01T00:00:00Z", version=ver)

    val = RelationshipValidation(
        validation_id=v_id,
        graph_id="KGR_1",
        status=status,
        is_valid=is_val,
        broken_chain_count=0 if is_val else 1,
        orphan_node_count=0,
        cycle_count=0,
        duplicate_count=0,
        violations=[] if is_val else ["Violation"],
        timestamp="2026-01-01T00:00:00Z",
        metadata={"version": ver},
        canonical_hash=h_digest,
    )

    assert val.validation_id.startswith("VAL_")
    assert val.canonical_hash == h_digest


@pytest.mark.parametrize("cnt", [0, 10, 50, 100, 500, 1000, 5000])
def test_knowledge_summary_model(cnt: int) -> None:
    s_id, h_digest = compute_knowledge_summary_id("2026-01-01T00:00:00Z", cnt, cnt)

    summary = KnowledgeSummary(
        summary_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        total_nodes=cnt,
        total_relationships=cnt,
        total_graphs=1,
        total_paths_analyzed=cnt,
        node_type_counts={"HYPOTHESIS": cnt},
        relationship_type_counts={"TESTS_HYPOTHESIS": cnt},
        metadata={},
        canonical_hash=h_digest,
    )

    assert summary.summary_id.startswith("KSM_")
    assert summary.canonical_hash == h_digest
