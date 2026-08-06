"""
Project GOAT v0.9 — Dedicated Tests for Knowledge Report Generator
"""

import json
import pytest

from goat.knowledge.core.canonical import (
    compute_knowledge_graph_id,
    compute_knowledge_relationship_id,
    compute_knowledge_summary_id,
    compute_relationship_validation_id,
    compute_scientific_path_id,
)
from goat.knowledge.core.enums import (
    PathValidity,
    RelationshipType,
    ValidationStatus,
)
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeRelationship,
    KnowledgeSummary,
    RelationshipValidation,
    ScientificPath,
)
from goat.knowledge.reporting.reports import KnowledgeReportGenerator
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_knowledge_reporting_generator(index_type: SyntheticIndexType) -> None:
    reporter = KnowledgeReportGenerator()

    rel_id, r_hash = compute_knowledge_relationship_id("KND_SRC", "KND_TGT", "GENERATES_EVIDENCE")
    rel = KnowledgeRelationship(
        relationship_id=rel_id,
        source_node_id="KND_SRC",
        target_node_id="KND_TGT",
        relationship_type=RelationshipType.GENERATES_EVIDENCE,
        weight=1.0,
        timestamp="2026-01-01T00:00:00Z",
        metadata={"sym": index_type.value},
        canonical_hash=r_hash,
    )

    g_id, g_hash = compute_knowledge_graph_id("Graph_1", ["KND_SRC", "KND_TGT"], [rel_id])
    graph = KnowledgeGraph(
        graph_id=g_id,
        graph_name="Graph_1",
        node_ids=["KND_SRC", "KND_TGT"],
        relationship_ids=[rel_id],
        created_at="2026-01-01T00:00:00Z",
        metadata={},
        canonical_hash=g_hash,
    )

    p_id, p_hash = compute_scientific_path_id("KND_SRC", "KND_TGT", ["KND_SRC", "KND_TGT"])
    path = ScientificPath(
        path_id=p_id,
        source_node_id="KND_SRC",
        target_node_id="KND_TGT",
        node_chain=["KND_SRC", "KND_TGT"],
        relationship_chain=[rel_id],
        validity=PathValidity.VALID_SCIENTIFIC_CHAIN,
        path_length=1,
        metadata={},
        canonical_hash=p_hash,
    )

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

    s_id, s_hash = compute_knowledge_summary_id("2026-01-01T00:00:00Z", 2, 1)
    summary = KnowledgeSummary(
        summary_id=s_id,
        timestamp="2026-01-01T00:00:00Z",
        total_nodes=2,
        total_relationships=1,
        total_graphs=1,
        total_paths_analyzed=1,
        node_type_counts={"HYPOTHESIS": 1, "EVIDENCE": 1},
        relationship_type_counts={"GENERATES_EVIDENCE": 1},
        metadata={},
        canonical_hash=s_hash,
    )

    rel_rep = reporter.generate_relationship_report(rel)
    graph_rep = reporter.generate_graph_report(graph)
    trace_rep = reporter.generate_traceability_report(path)
    val_rep = reporter.generate_validation_report(val)
    exec_rep = reporter.generate_executive_report(summary)

    assert "# SCIENTIFIC KNOWLEDGE RELATIONSHIP REPORT" in rel_rep
    assert "# SCIENTIFIC KNOWLEDGE GRAPH REPORT" in graph_rep
    assert "# SCIENTIFIC TRACEABILITY PATH REPORT" in trace_rep
    assert "# KNOWLEDGE GRAPH VALIDATION AUDIT REPORT" in val_rep
    assert "# EDGE KNOWLEDGE GRAPH EXECUTIVE SUMMARY REPORT" in exec_rep

    json_str = reporter.export_canonical_json(graph)
    data = json.loads(json_str)
    assert data["graph_id"] == graph.graph_id
    assert data["canonical_hash"] == graph.canonical_hash
