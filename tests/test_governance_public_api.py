"""
Project GOAT v0.9 — Comprehensive Governance Public API & Canonical Hash Integrity Tests
"""

import pytest

import goat.governance as governance
from goat.governance import (
    AuditRepository,
    EdgeCandidate,
    EdgeGovernanceEngine,
    EdgePromotionEngine,
    EdgeRepository,
    EdgeRetirementEngine,
    EdgeStatus,
    GovernanceAudit,
    GovernanceAuditEngine,
    GovernanceDecision,
    GovernanceDecisionOutcome,
    GovernancePersistenceContext,
    GovernanceReason,
    GovernanceRepository,
    GovernanceSummary,
    MasterGovernanceEngine,
    PromotionAssessment,
    PromotionRepository,
    RetirementAssessment,
    RetirementRepository,
    SummaryRepository,
    compute_canonical_sha256,
    compute_edge_id,
    compute_governance_audit_id,
    compute_governance_decision_id,
    compute_promotion_assessment_id,
    compute_retirement_assessment_id,
    compute_summary_id,
    generate_audit_report,
    generate_executive_report,
    generate_governance_decision_report,
    generate_json_report,
    generate_promotion_report,
    generate_retirement_report,
    init_governance_db,
    serialize_canonical_json,
)


def test_public_api_exports():
    expected_exports = [
        "AuditRepository",
        "EdgeCandidate",
        "EdgeGovernanceEngine",
        "EdgePromotionEngine",
        "EdgeRepository",
        "EdgeRetirementEngine",
        "EdgeStatus",
        "GovernanceAudit",
        "GovernanceAuditEngine",
        "GovernanceDecision",
        "GovernanceDecisionOutcome",
        "GovernancePersistenceContext",
        "GovernanceReason",
        "GovernanceRepository",
        "GovernanceSummary",
        "MasterGovernanceEngine",
        "PromotionAssessment",
        "PromotionRepository",
        "RetirementAssessment",
        "RetirementRepository",
        "SummaryRepository",
        "compute_canonical_sha256",
        "compute_edge_id",
        "compute_governance_audit_id",
        "compute_governance_decision_id",
        "compute_promotion_assessment_id",
        "compute_retirement_assessment_id",
        "compute_summary_id",
        "generate_audit_report",
        "generate_executive_report",
        "generate_governance_decision_report",
        "generate_json_report",
        "generate_promotion_report",
        "generate_retirement_report",
        "init_governance_db",
        "serialize_canonical_json",
    ]

    for export_name in expected_exports:
        assert hasattr(governance, export_name)
        assert export_name in governance.__all__

    assert len(governance.__all__) == len(expected_exports)


@pytest.mark.parametrize("i", range(1, 1501))
def test_edge_id_determinism_large(i: int):
    hyp_id = f"HYP_{i:016X}"
    title = f"Title #{i}"

    id1, hash1 = compute_edge_id(hypothesis_id=hyp_id, title=title)
    id2, hash2 = compute_edge_id(hypothesis_id=hyp_id, title=title)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EDG_")
    assert len(id1) == 20
    assert len(hash1) == 64


@pytest.mark.parametrize("p", range(1, 1501))
def test_promotion_id_determinism_large(p: int):
    edg_id = f"EDG_{p:016X}"
    hyp_id = f"HYP_{p:016X}"

    id1, hash1 = compute_promotion_assessment_id(edge_id=edg_id, hypothesis_id=hyp_id)
    id2, hash2 = compute_promotion_assessment_id(edge_id=edg_id, hypothesis_id=hyp_id)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("PRA_")
    assert len(id1) == 20


@pytest.mark.parametrize("r", range(1, 1501))
def test_retirement_id_determinism_large(r: int):
    edg_id = f"EDG_{r:016X}"
    hyp_id = f"HYP_{r:016X}"

    id1, hash1 = compute_retirement_assessment_id(edge_id=edg_id, hypothesis_id=hyp_id)
    id2, hash2 = compute_retirement_assessment_id(edge_id=edg_id, hypothesis_id=hyp_id)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RTA_")
    assert len(id1) == 20


@pytest.mark.parametrize("d", range(1, 1501))
def test_decision_id_determinism_large(d: int):
    edg_id = f"EDG_{d:016X}"

    id1, hash1 = compute_governance_decision_id(edge_id=edg_id, decision="PROMOTE", reason="LIVE_CONFIRMATION")
    id2, hash2 = compute_governance_decision_id(edge_id=edg_id, decision="PROMOTE", reason="LIVE_CONFIRMATION")

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("GOV_")
    assert len(id1) == 20


@pytest.mark.parametrize("a", range(1, 1501))
def test_audit_id_determinism_large(a: int):
    gov_id = f"GOV_{a:016X}"
    ts = f"2026-08-04T12:{a % 60:02d}:00Z"

    id1, hash1 = compute_governance_audit_id(decision_id=gov_id, action="PROMOTE", timestamp=ts)
    id2, hash2 = compute_governance_audit_id(decision_id=gov_id, action="PROMOTE", timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("AUD_")
    assert len(id1) == 20


@pytest.mark.parametrize("u", range(1, 1501))
def test_summary_id_determinism_large(u: int):
    ts = f"2026-08-04T12:{u % 60:02d}:00Z"

    id1, hash1 = compute_summary_id(total_edges=u, total_decisions=u, timestamp=ts)
    id2, hash2 = compute_summary_id(total_edges=u, total_decisions=u, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("GSM_")
    assert len(id1) == 20
