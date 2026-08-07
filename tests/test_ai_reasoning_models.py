"""
Unit tests for Phase 7 AI Research & Reasoning domain models, Pydantic immutability, and canonical SHA-256 digests.
"""

import pytest
from pydantic import ValidationError

from goat.ai_reasoning.models import (
    EdgeType,
    EvidenceBundle,
    EvidenceRecord,
    EvidenceType,
    ExplanationLevel,
    NodeType,
    ReasoningConclusion,
    ResearchGraphEdge,
    ResearchGraphNode,
    ResearchReport,
    compute_conclusion_id,
    compute_edge_id,
    compute_evidence_bundle_id,
    compute_evidence_record_id,
    compute_node_id,
    compute_report_id,
)


def test_research_graph_node_model():
    n_id, n_hash = compute_node_id(NodeType.FEATURE, "trend_strength")
    assert n_id.startswith("RKN_")

    node = ResearchGraphNode(
        node_id=n_id,
        node_type=NodeType.FEATURE,
        name="trend_strength",
        properties={"category": "trend"},
        canonical_hash=n_hash,
    )
    assert node.node_id == n_id
    assert node.node_type == NodeType.FEATURE

    with pytest.raises(ValidationError):
        node.name = "new_name"


def test_research_graph_edge_model():
    s_id, _ = compute_node_id(NodeType.EDGE, "EDG_1234567890ABCDEF")
    t_id, _ = compute_node_id(NodeType.FEATURE, "trend_strength")
    e_id, e_hash = compute_edge_id(s_id, t_id, EdgeType.DERIVED_FROM)
    assert e_id.startswith("RKE_")

    edge = ResearchGraphEdge(
        edge_id=e_id,
        source_id=s_id,
        target_id=t_id,
        edge_type=EdgeType.DERIVED_FROM,
        canonical_hash=e_hash,
    )
    assert edge.edge_id == e_id
    assert edge.edge_type == EdgeType.DERIVED_FROM


def test_evidence_models():
    claim = "Expected Value per trade is positive"
    r_id, r_hash = compute_evidence_record_id(claim, "expected_value", 0.005)
    assert r_id.startswith("EVR_")

    record = EvidenceRecord(
        record_id=r_id,
        evidence_type=EvidenceType.STATISTICAL_METRIC,
        claim=claim,
        metric_name="expected_value",
        metric_value=0.005,
        threshold_value=0.0,
        is_supporting=True,
        canonical_hash=r_hash,
    )

    b_id, b_hash = compute_evidence_bundle_id("EDG_1234567890ABCDEF", [record])
    assert b_id.startswith("EVB_")

    bundle = EvidenceBundle(
        bundle_id=b_id,
        target_id="EDG_1234567890ABCDEF",
        target_type="EDGE",
        records=[record],
        sample_size=100,
        overall_confidence=1.0,
        canonical_hash=b_hash,
    )
    assert bundle.bundle_id == b_id
    assert len(bundle.records) == 1


def test_report_and_conclusion_models():
    c_id, _ = compute_conclusion_id("Edge is ACTIVE", "ACTIVE")
    assert c_id.startswith("CON_")

    conclusion = ReasoningConclusion(
        conclusion_id=c_id,
        claim="Edge is ACTIVE",
        status_verdict="ACTIVE",
        reasoning_steps=["Sharpe > 1.0", "EV > 0.0"],
        supporting_evidence_ids=["EVR_1234567890ABCDEF"],
        confidence_score=1.0,
    )

    r_id, r_hash = compute_report_id("Test Report", "2026-08-07T12:00:00Z", "EDG_1234567890ABCDEF")
    assert r_id.startswith("REP_")

    rec_id, rec_hash = compute_evidence_record_id("Claim", "ev", 0.01)
    b_id, b_hash = compute_evidence_bundle_id("EDG_1234567890ABCDEF", [])

    bundle = EvidenceBundle(
        bundle_id=b_id,
        target_id="EDG_1234567890ABCDEF",
        target_type="EDGE",
        records=[],
        sample_size=50,
        overall_confidence=0.9,
        canonical_hash=b_hash,
    )

    report = ResearchReport(
        report_id=r_id,
        title="Test Report",
        timestamp="2026-08-07T12:00:00Z",
        explanation_level=ExplanationLevel.PROFESSIONAL_QUANT,
        executive_summary="Exec Summary",
        conclusions=[conclusion],
        evidence_bundle=bundle,
        supporting_statistics={"ev": 0.01},
        risk_factors=["Risk"],
        limitations=["Limitation"],
        recommended_next_steps=["Step"],
        checksum="CHK",
        metadata={},
        canonical_hash=r_hash,
    )
    assert report.report_id == r_id
    assert report.explanation_level == ExplanationLevel.PROFESSIONAL_QUANT
