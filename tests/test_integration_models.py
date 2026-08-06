"""
Project GOAT v0.7 — Test Suite for Integration Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (KnowledgeNode, KnowledgeEdge, IntegratedKnowledge, ConflictRecord)
- Extra fields forbidden
- Deterministic ID generators & canonical hashes
- Fingerprint generation
- Serialization fidelity
"""

import pytest
from pydantic import ValidationError

from goat.integration.core.canonical import (
    compute_conflict_id,
    compute_edge_id,
    compute_evidence_merge_id,
    compute_integrated_knowledge_id,
    compute_node_fingerprint,
    compute_node_id,
    compute_version_id,
    serialize_canonical_json,
)
from goat.integration.core.enums import (
    ConflictSeverity,
    ConflictType,
    KnowledgeNodeType,
    KnowledgeRelationship,
)
from goat.integration.core.models import (
    ConflictRecord,
    IntegratedKnowledge,
    KnowledgeEdge,
    KnowledgeNode,
)


# --- ID & Canonical Hashing Tests ---

def test_node_id_determinism():
    id1, hash1, fp1 = compute_node_id("Title A", "HYPOTHESIS", "VAL_001")
    id2, hash2, fp2 = compute_node_id("Title A", "HYPOTHESIS", "VAL_001")
    assert id1 == id2
    assert hash1 == hash2
    assert fp1 == fp2
    assert id1.startswith("KND_")
    assert len(id1) == 20
    assert fp1.startswith("NDFP_")


def test_node_id_sensitivity():
    id1, _, _ = compute_node_id("Title A", "HYPOTHESIS", "VAL_001")
    id2, _, _ = compute_node_id("Title B", "HYPOTHESIS", "VAL_001")
    assert id1 != id2


def test_edge_id_determinism():
    id1, hash1 = compute_edge_id("KND_1111111111111111", "KND_2222222222222222", "SUPPORTS")
    id2, hash2 = compute_edge_id("KND_1111111111111111", "KND_2222222222222222", "SUPPORTS")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("KED_")


def test_integrated_knowledge_id_determinism():
    id1, hash1 = compute_integrated_knowledge_id(["VAL_1", "VAL_2"], ["HYP_1"], ["EXP_1"])
    id2, hash2 = compute_integrated_knowledge_id(["VAL_2", "VAL_1"], ["HYP_1"], ["EXP_1"])
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("IKN_")


def test_conflict_id_determinism():
    id1, hash1 = compute_conflict_id("VAL_A", "VAL_B", "CONTRADICTED")
    id2, hash2 = compute_conflict_id("VAL_B", "VAL_A", "CONTRADICTED")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CFL_")


def test_evidence_merge_id_determinism():
    id1, hash1 = compute_evidence_merge_id(["E1", "E2"], "IKN_1234567890ABCDEF")
    id2, hash2 = compute_evidence_merge_id(["E2", "E1"], "IKN_1234567890ABCDEF")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EMG_")


def test_version_id_determinism():
    id1, hash1 = compute_version_id("IKN_1234567890ABCDEF", "HASH_STATE_1", 1)
    id2, hash2 = compute_version_id("IKN_1234567890ABCDEF", "HASH_STATE_1", 1)
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("KVR_")


def test_serialize_canonical_json():
    data = {"b": 2, "a": 1, "enum": KnowledgeNodeType.HYPOTHESIS}
    json_str = serialize_canonical_json(data)
    assert json_str == '{"a":1,"b":2,"enum":"HYPOTHESIS"}'


# --- KnowledgeNode Tests ---

def test_knowledge_node_instantiation():
    node_id, hash_val, fp = compute_node_id("Node Title", "VALIDATION", "VAL_100")
    node = KnowledgeNode(
        node_id=node_id,
        title="Node Title",
        node_type=KnowledgeNodeType.VALIDATION,
        description="Test node",
        originating_validation="VAL_100",
        creation_timestamp="2026-07-30T00:00:00Z",
        metadata={"key": "val"},
        canonical_hash=hash_val,
        fingerprint=fp,
    )
    assert node.node_id == node_id
    assert node.node_type == KnowledgeNodeType.VALIDATION


def test_knowledge_node_immutability():
    node_id, hash_val, fp = compute_node_id("Node Title", "VALIDATION", "VAL_100")
    node = KnowledgeNode(
        node_id=node_id,
        title="Node Title",
        node_type=KnowledgeNodeType.VALIDATION,
        description="Test node",
        originating_validation="VAL_100",
        creation_timestamp="2026-07-30T00:00:00Z",
        metadata={},
        canonical_hash=hash_val,
        fingerprint=fp,
    )
    with pytest.raises((TypeError, ValidationError)):
        node.title = "New Title"  # Frozen check


def test_knowledge_node_extra_forbidden():
    node_id, hash_val, fp = compute_node_id("Node Title", "VALIDATION", "VAL_100")
    with pytest.raises(ValidationError):
        KnowledgeNode(
            node_id=node_id,
            title="Node Title",
            node_type=KnowledgeNodeType.VALIDATION,
            description="Test node",
            originating_validation="VAL_100",
            creation_timestamp="2026-07-30T00:00:00Z",
            extra_field="invalid",
        )


def test_knowledge_node_invalid_id_pattern():
    with pytest.raises(ValidationError):
        KnowledgeNode(
            node_id="INVALID_PREFIX_123",
            title="Title",
            node_type=KnowledgeNodeType.VALIDATION,
            originating_validation="VAL_1",
            creation_timestamp="2026-07-30T00:00:00Z",
        )


# --- KnowledgeEdge Tests ---

def test_knowledge_edge_instantiation():
    e_id, e_hash = compute_edge_id("KND_1111111111111111", "KND_2222222222222222", "SUPPORTS")
    edge = KnowledgeEdge(
        edge_id=e_id,
        source_node="KND_1111111111111111",
        destination_node="KND_2222222222222222",
        relationship=KnowledgeRelationship.SUPPORTS,
        confidence=0.95,
        supporting_evidence=["EV_1"],
        canonical_hash=e_hash,
    )
    assert edge.edge_id == e_id
    assert edge.confidence == 0.95


def test_knowledge_edge_immutability():
    e_id, e_hash = compute_edge_id("KND_1111111111111111", "KND_2222222222222222", "SUPPORTS")
    edge = KnowledgeEdge(
        edge_id=e_id,
        source_node="KND_1111111111111111",
        destination_node="KND_2222222222222222",
        relationship=KnowledgeRelationship.SUPPORTS,
    )
    with pytest.raises((TypeError, ValidationError)):
        edge.confidence = 0.5


def test_knowledge_edge_invalid_id_pattern():
    with pytest.raises(ValidationError):
        KnowledgeEdge(
            edge_id="WRONG_ID",
            source_node="KND_1111111111111111",
            destination_node="KND_2222222222222222",
            relationship=KnowledgeRelationship.SUPPORTS,
        )


# --- IntegratedKnowledge Tests ---

def test_integrated_knowledge_instantiation():
    ik_id, ik_hash = compute_integrated_knowledge_id(["V1"], ["H1"], ["E1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["V1"],
        participating_hypotheses=["H1"],
        participating_experiments=["E1"],
        overall_confidence=0.88,
        reproducibility=0.92,
        consensus_strength=0.95,
        conflict_score=0.0,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )
    assert ik.knowledge_id == ik_id
    assert ik.overall_confidence == 0.88


def test_integrated_knowledge_immutability():
    ik_id, ik_hash = compute_integrated_knowledge_id(["V1"], ["H1"], ["E1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        creation_timestamp="2026-07-30T00:00:00Z",
    )
    with pytest.raises((TypeError, ValidationError)):
        ik.overall_confidence = 0.99


# --- ConflictRecord Tests ---

def test_conflict_record_instantiation():
    c_id, c_hash = compute_conflict_id("V1", "V2", "CONTRADICTED")
    record = ConflictRecord(
        conflict_id=c_id,
        validation_a="V1",
        validation_b="V2",
        conflict_type=ConflictType.CONTRADICTED,
        severity=ConflictSeverity.HIGH,
        explanation="Opposite validation outcomes.",
        supporting_evidence=["E1", "E2"],
        canonical_hash=c_hash,
        timestamp="2026-07-30T00:00:00Z",
    )
    assert record.conflict_id == c_id
    assert record.severity == ConflictSeverity.HIGH


def test_conflict_record_immutability():
    c_id, _ = compute_conflict_id("V1", "V2", "CONTRADICTED")
    record = ConflictRecord(
        conflict_id=c_id,
        validation_a="V1",
        validation_b="V2",
        conflict_type=ConflictType.CONTRADICTED,
        explanation="Explanation",
    )
    with pytest.raises((TypeError, ValidationError)):
        record.explanation = "Modified explanation"
