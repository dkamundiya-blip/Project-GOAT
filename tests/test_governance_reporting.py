"""
Project GOAT v0.9 — Dedicated Unit Tests for Governance Reporting Generators
"""

import json
import pytest

from goat.governance.core.canonical import compute_summary_id
from goat.governance.core.enums import EdgeStatus, GovernanceDecisionOutcome, GovernanceReason
from goat.governance.core.models import (
    GovernanceAudit,
    GovernanceDecision,
    GovernanceSummary,
    PromotionAssessment,
    RetirementAssessment,
)
from goat.governance.reporting.reports import (
    generate_audit_report,
    generate_executive_report,
    generate_governance_decision_report,
    generate_json_report,
    generate_promotion_report,
    generate_retirement_report,
)


def test_generate_promotion_report():
    pra = PromotionAssessment(
        assessment_id="PRA_1234567890ABCDEF",
        edge_id="EDG_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        is_hypothesis_passed=True,
        is_evidence_complete=True,
        is_experiment_complete=True,
        is_statistics_complete=True,
        is_live_validation_complete=True,
        is_constitution_satisfied=True,
        is_research_protocol_satisfied=True,
        is_promotable=True,
        assessment_notes="Promotable edge.",
        timestamp="2026-08-04T12:00:00Z",
    )

    report = generate_promotion_report(pra)
    assert "# EDGE PROMOTION ASSESSMENT REPORT" in report
    assert pra.assessment_id in report


def test_generate_retirement_report():
    rta = RetirementAssessment(
        assessment_id="RTA_1234567890ABCDEF",
        edge_id="EDG_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        expectancy_degradation=0.6,
        confidence_decline=0.4,
        structural_shift_detected=True,
        amendment_001_violation=False,
        is_retirement_recommended=True,
        assessment_notes="Retirement recommended.",
        timestamp="2026-08-04T12:00:00Z",
    )

    report = generate_retirement_report(rta)
    assert "# EDGE RETIREMENT ASSESSMENT REPORT" in report
    assert rta.assessment_id in report


def test_generate_governance_decision_report():
    dec = GovernanceDecision(
        decision_id="GOV_1234567890ABCDEF",
        edge_id="EDG_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        decision=GovernanceDecisionOutcome.PROMOTE,
        reason=GovernanceReason.LIVE_CONFIRMATION,
        rationale="Detailed test rationale for decision.",
        timestamp="2026-08-04T12:00:00Z",
    )

    report = generate_governance_decision_report(dec)
    assert "# CONSTITUTIONAL GOVERNANCE DECISION REPORT" in report
    assert dec.decision_id in report


def test_generate_audit_report():
    aud = GovernanceAudit(
        audit_id="AUD_1234567890ABCDEF",
        decision_id="GOV_1234567890ABCDEF",
        edge_id="EDG_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        evidence_ids=["EVR_1234567890ABCDEF"],
        experiment_id="EXP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        is_explainable=True,
        is_replayable=True,
        timestamp="2026-08-04T12:00:00Z",
    )

    report = generate_audit_report(aud)
    assert "# GOVERNANCE AUDIT TRAIL REPORT" in report
    assert aud.audit_id in report


def test_generate_json_report():
    dec = GovernanceDecision(
        decision_id="GOV_1234567890ABCDEF",
        edge_id="EDG_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        decision=GovernanceDecisionOutcome.PROMOTE,
        reason=GovernanceReason.LIVE_CONFIRMATION,
        rationale="Detailed test rationale for decision.",
        timestamp="2026-08-04T12:00:00Z",
    )

    json_str = generate_json_report(dec)
    data = json.loads(json_str)
    assert data["decision_id"] == dec.decision_id


@pytest.mark.parametrize("edge_count", range(1, 10))
def test_generate_executive_report(edge_count: int):
    decisions = [
        GovernanceDecision(
            decision_id=f"GOV_{i:016X}",
            edge_id=f"EDG_{i:016X}",
            hypothesis_id=f"HYP_{i:016X}",
            decision=GovernanceDecisionOutcome.PROMOTE,
            reason=GovernanceReason.LIVE_CONFIRMATION,
            rationale="Test decision rationale.",
            timestamp="2026-08-04T12:00:00Z",
        )
        for i in range(edge_count)
    ]

    gsm_id, gsm_hash = compute_summary_id(total_edges=edge_count, total_decisions=edge_count)
    summary = GovernanceSummary(
        summary_id=gsm_id,
        total_edges=edge_count,
        total_decisions=edge_count,
        status_counts={"APPROVED": edge_count},
        decision_counts={"PROMOTE": edge_count},
        reason_counts={"LIVE_CONFIRMATION": edge_count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=gsm_hash,
    )

    report = generate_executive_report(summary, decisions)
    assert "# PROJECT GOAT — EDGE GOVERNANCE EXECUTIVE REPORT" in report
    assert f"Total Edges**: `{edge_count}`" in report
