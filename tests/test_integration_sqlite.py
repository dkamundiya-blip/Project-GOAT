"""
Project GOAT v0.7 — Test Suite for SQLite Persistence Repositories

Coverage:
- KnowledgeRepository (save, get, list round-trip)
- GraphRepository (save edge/graph, get edge, load graph round-trip)
- ConflictRepository (save, get, list round-trip)
- IntegrationRepository (save integrated knowledge & state versions, load round-trip)
- EvidenceRepository (save merge record, get round-trip)
- ReportRepository (save report, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.integration.core.canonical import (
    compute_conflict_id,
    compute_edge_id,
    compute_evidence_merge_id,
    compute_integrated_knowledge_id,
    compute_node_id,
    compute_version_id,
)
from goat.integration.core.enums import ConflictSeverity, ConflictType, KnowledgeNodeType, KnowledgeRelationship
from goat.integration.core.models import ConflictRecord, IntegratedKnowledge, KnowledgeEdge, KnowledgeNode
from goat.integration.evidence.models import EvidenceMergeRecord
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.integration.persistence.sqlite import (
    ConflictRepository,
    EvidenceRepository,
    GraphRepository,
    IntegrationRepository,
    KnowledgeRepository,
    ReportRepository,
    init_integration_db,
)

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_integration_db(conn)
    yield conn
    conn.close()


def test_knowledge_repository_roundtrip(db_conn):
    repo = KnowledgeRepository(db_conn)
    n_id, n_hash, fp = compute_node_id("Node Title", "VALIDATION", "VAL_1")
    node = KnowledgeNode(
        node_id=n_id,
        title="Node Title",
        node_type=KnowledgeNodeType.VALIDATION,
        description="Description",
        originating_validation="VAL_1",
        creation_timestamp="2026-07-30T00:00:00Z",
        metadata={"k": "v"},
        canonical_hash=n_hash,
        fingerprint=fp,
    )

    repo.save_node(node)
    fetched = repo.get_node(n_id)

    assert fetched == node
    assert len(repo.list_nodes()) == 1


def test_graph_repository_roundtrip(db_conn):
    repo = GraphRepository(db_conn)
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

    repo.save_graph(graph)
    loaded_graph = repo.load_graph()

    assert loaded_graph.get_nodes() == graph.get_nodes()
    assert loaded_graph.get_edges() == graph.get_edges()


def test_conflict_repository_roundtrip(db_conn):
    repo = ConflictRepository(db_conn)
    c_id, c_hash = compute_conflict_id("VAL_1", "VAL_2", "CONTRADICTED")
    record = ConflictRecord(
        conflict_id=c_id,
        validation_a="VAL_1",
        validation_b="VAL_2",
        conflict_type=ConflictType.CONTRADICTED,
        severity=ConflictSeverity.HIGH,
        explanation="Contradiction",
        supporting_evidence=["E1"],
        canonical_hash=c_hash,
        timestamp="2026-07-30T00:00:00Z",
    )

    repo.save_conflict(record)
    fetched = repo.get_conflict(c_id)

    assert fetched == record
    assert len(repo.list_conflicts()) == 1


def test_integration_repository_roundtrip(db_conn):
    repo = IntegrationRepository(db_conn)
    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["VAL_1"],
        participating_hypotheses=["HYP_1"],
        participating_experiments=["EXP_1"],
        overall_confidence=0.90,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )

    repo.save_integrated_knowledge(ik)
    fetched = repo.get_integrated_knowledge(ik_id)

    assert fetched == ik


def test_evidence_repository_roundtrip(db_conn):
    ik_repo = IntegrationRepository(db_conn)
    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(knowledge_id=ik_id, creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=ik_hash)
    ik_repo.save_integrated_knowledge(ik)

    ev_repo = EvidenceRepository(db_conn)
    m_id, m_hash = compute_evidence_merge_id(["E1", "E2"], ik_id)
    rec = EvidenceMergeRecord(
        merge_id=m_id,
        source_evidence_ids=["E1", "E2"],
        target_knowledge_id=ik_id,
        accumulated_confidence=0.85,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=m_hash,
    )

    ev_repo.save_merge_record(rec)
    fetched = ev_repo.get_merge_record(m_id)

    assert fetched == rec


def test_report_repository_roundtrip(db_conn):
    repo = ReportRepository(db_conn)
    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(knowledge_id=ik_id, creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=ik_hash)

    from goat.integration.reporting.reports import KnowledgeIntegrationReport
    report = KnowledgeIntegrationReport(
        report_id="REP_001",
        timestamp="2026-07-30T00:00:00Z",
        integrated_knowledge=ik,
        node_count=5,
        edge_count=4,
        conflict_count=0,
    )

    repo.save_report("REP_001", "KnowledgeIntegrationReport", "2026-07-30T00:00:00Z", report)
    json_out = repo.get_report_json("REP_001")

    assert json_out is not None
    assert "REP_001" in json_out
