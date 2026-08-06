"""
Project GOAT v0.7 — Test Suite for Integration Reporting Engine

Coverage:
- KnowledgeIntegrationReport (Markdown & JSON)
- ConflictReport (Markdown & JSON)
- KnowledgeGraphReport (Markdown & JSON)
- EvidenceMergeReport (Markdown & JSON)
- KnowledgeEvolutionReport (Markdown & JSON)
"""

from goat.integration.core.canonical import (
    compute_conflict_id,
    compute_evidence_merge_id,
    compute_integrated_knowledge_id,
)
from goat.integration.core.enums import ConflictSeverity, ConflictType
from goat.integration.core.models import ConflictRecord, IntegratedKnowledge
from goat.integration.evidence.models import EvidenceMergeRecord
from goat.integration.reporting.reports import (
    ConflictReport,
    EvidenceMergeReport,
    KnowledgeEvolutionReport,
    KnowledgeGraphReport,
    KnowledgeIntegrationReport,
)
from goat.integration.versioning import KnowledgeStateVersion


def test_knowledge_integration_report_rendering():
    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(
        knowledge_id=ik_id,
        participating_validations=["VAL_1"],
        participating_hypotheses=["HYP_1"],
        participating_experiments=["EXP_1"],
        overall_confidence=0.88,
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=ik_hash,
    )

    report = KnowledgeIntegrationReport(
        report_id="REP_INT_001",
        timestamp="2026-07-30T00:00:00Z",
        integrated_knowledge=ik,
        node_count=10,
        edge_count=12,
        conflict_count=1,
    )

    md = report.to_markdown()
    assert "# Scientific Knowledge Integration Report" in md
    assert ik_id in md
    assert "**Nodes**: 10" in md

    json_str = report.to_json()
    assert '"report_id":"REP_INT_001"' in json_str


def test_conflict_report_rendering():
    c_id, c_hash = compute_conflict_id("VAL_1", "VAL_2", "CONTRADICTED")
    record = ConflictRecord(
        conflict_id=c_id,
        validation_a="VAL_1",
        validation_b="VAL_2",
        conflict_type=ConflictType.CONTRADICTED,
        severity=ConflictSeverity.HIGH,
        explanation="Opposite findings",
        canonical_hash=c_hash,
    )

    report = ConflictReport(
        report_id="REP_CFL_001",
        timestamp="2026-07-30T00:00:00Z",
        conflicts=[record],
    )

    md = report.to_markdown()
    assert "# Scientific Conflict Report" in md
    assert c_id in md


def test_knowledge_graph_report_rendering():
    report = KnowledgeGraphReport(
        report_id="REP_GRP_001",
        timestamp="2026-07-30T00:00:00Z",
        total_nodes=5,
        total_edges=4,
        node_types_breakdown={"VALIDATION": 3, "HYPOTHESIS": 2},
        relationship_types_breakdown={"SUPPORTS": 4},
    )

    md = report.to_markdown()
    assert "# Scientific Knowledge Graph Report" in md
    assert "**VALIDATION**: 3" in md


def test_evidence_merge_report_rendering():
    ik_id, _ = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    m_id, m_hash = compute_evidence_merge_id(["E1"], ik_id)
    rec = EvidenceMergeRecord(
        merge_id=m_id,
        source_evidence_ids=["E1"],
        target_knowledge_id=ik_id,
        accumulated_confidence=0.85,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=m_hash,
    )

    report = EvidenceMergeReport(
        report_id="REP_EMG_001",
        timestamp="2026-07-30T00:00:00Z",
        merge_record=rec,
    )

    md = report.to_markdown()
    assert "# Evidence Merge Report" in md
    assert m_id in md


def test_knowledge_evolution_report_rendering():
    ik_id, ik_hash = compute_integrated_knowledge_id(["VAL_1"], ["HYP_1"], ["EXP_1"])
    ik = IntegratedKnowledge(knowledge_id=ik_id, creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=ik_hash)

    version = KnowledgeStateVersion(
        version_id="KVR_0000000000000001",
        knowledge_id=ik_id,
        version_number=1,
        state_hash="HASH_STATE_1",
        timestamp="2026-07-30T00:00:00Z",
        graph_state={"nodes": [], "edges": []},
        integrated_knowledge=ik,
    )

    report = KnowledgeEvolutionReport(
        report_id="REP_EVO_001",
        timestamp="2026-07-30T00:00:00Z",
        knowledge_id=ik_id,
        versions=[version],
    )

    md = report.to_markdown()
    assert "# Knowledge Evolution Report" in md
    assert "KVR_0000000000000001" in md
