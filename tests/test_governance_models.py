"""
Project GOAT v0.9 — Dedicated Unit Tests for Governance Domain Models
"""

import pytest
from pydantic import ValidationError

from goat.governance.core.canonical import (
    compute_canonical_sha256,
    compute_edge_id,
    compute_governance_audit_id,
    compute_governance_decision_id,
    compute_promotion_assessment_id,
    compute_retirement_assessment_id,
    compute_summary_id,
    serialize_canonical_json,
)
from goat.governance.core.enums import (
    EdgeStatus,
    GovernanceDecisionOutcome,
    GovernanceReason,
)
from goat.governance.core.models import (
    EdgeCandidate,
    GovernanceAudit,
    GovernanceDecision,
    GovernanceSummary,
    PromotionAssessment,
    RetirementAssessment,
)


@pytest.mark.parametrize("status", list(EdgeStatus))
def test_edge_candidate_model(status: EdgeStatus):
    hyp_id = "HYP_1234567890ABCDEF"
    ste_id = "STE_1234567890ABCDEF"
    exp_id = "EXP_1234567890ABCDEF"
    vsn_id = "VSN_1234567890ABCDEF"

    edg_id, canonical_hash = compute_edge_id(
        hypothesis_id=hyp_id,
        title="Test Edge Candidate",
    )

    candidate = EdgeCandidate(
        edge_id=edg_id,
        title="Test Edge Candidate",
        hypothesis_id=hyp_id,
        evaluation_id=ste_id,
        experiment_id=exp_id,
        validation_session_id=vsn_id,
        evidence_ids=["EVR_1234567890ABCDEF"],
        status=status,
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    assert candidate.edge_id == edg_id
    assert candidate.hypothesis_id == hyp_id
    assert candidate.status == status
    assert candidate.canonical_hash == canonical_hash


@pytest.mark.parametrize("invalid_id", ["INVALID_ID", "EDG_SHORT", "123_EDG"])
def test_edge_candidate_invalid_id_pattern(invalid_id: str):
    with pytest.raises(ValidationError):
        EdgeCandidate(
            edge_id=invalid_id,
            title="Invalid",
            hypothesis_id="HYP_1234567890ABCDEF",
            evaluation_id="STE_1234567890ABCDEF",
            experiment_id="EXP_1234567890ABCDEF",
            validation_session_id="VSN_1234567890ABCDEF",
            created_timestamp="2026-08-04T12:00:00Z",
        )


def test_edge_candidate_immutability():
    edg_id, canonical_hash = compute_edge_id(
        hypothesis_id="HYP_1234567890ABCDEF",
        title="Immutable Edge",
    )
    candidate = EdgeCandidate(
        edge_id=edg_id,
        title="Immutable Edge",
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    with pytest.raises(ValidationError):
        candidate.status = EdgeStatus.ACTIVE  # Frozen check


@pytest.mark.parametrize("is_promotable", [True, False])
def test_promotion_assessment_model(is_promotable: bool):
    edg_id = "EDG_1234567890ABCDEF"
    hyp_id = "HYP_1234567890ABCDEF"
    pra_id, pra_hash = compute_promotion_assessment_id(
        edge_id=edg_id,
        hypothesis_id=hyp_id,
    )

    pra = PromotionAssessment(
        assessment_id=pra_id,
        edge_id=edg_id,
        hypothesis_id=hyp_id,
        is_hypothesis_passed=is_promotable,
        is_evidence_complete=is_promotable,
        is_experiment_complete=is_promotable,
        is_statistics_complete=is_promotable,
        is_live_validation_complete=is_promotable,
        is_constitution_satisfied=True,
        is_research_protocol_satisfied=True,
        is_promotable=is_promotable,
        assessment_notes="Notes statement.",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=pra_hash,
    )

    assert pra.assessment_id == pra_id
    assert pra.is_promotable == is_promotable


@pytest.mark.parametrize("is_retired", [True, False])
def test_retirement_assessment_model(is_retired: bool):
    edg_id = "EDG_1234567890ABCDEF"
    hyp_id = "HYP_1234567890ABCDEF"
    rta_id, rta_hash = compute_retirement_assessment_id(
        edge_id=edg_id,
        hypothesis_id=hyp_id,
    )

    rta = RetirementAssessment(
        assessment_id=rta_id,
        edge_id=edg_id,
        hypothesis_id=hyp_id,
        expectancy_degradation=0.6 if is_retired else 0.1,
        confidence_decline=0.4 if is_retired else 0.05,
        structural_shift_detected=is_retired,
        amendment_001_violation=False,
        is_retirement_recommended=is_retired,
        assessment_notes="Retirement evaluation statement.",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=rta_hash,
    )

    assert rta.assessment_id == rta_id
    assert rta.is_retirement_recommended == is_retired


@pytest.mark.parametrize("decision", list(GovernanceDecisionOutcome))
@pytest.mark.parametrize("reason", list(GovernanceReason))
def test_governance_decision_model(decision: GovernanceDecisionOutcome, reason: GovernanceReason):
    edg_id = "EDG_1234567890ABCDEF"
    gov_id, gov_hash = compute_governance_decision_id(
        edge_id=edg_id,
        decision=decision.value,
        reason=reason.value,
    )

    gov_dec = GovernanceDecision(
        decision_id=gov_id,
        edge_id=edg_id,
        hypothesis_id="HYP_1234567890ABCDEF",
        decision=decision,
        reason=reason,
        rationale="Detailed binding rationale statement for test.",
        authorizer="BOARD",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=gov_hash,
    )

    assert gov_dec.decision_id == gov_id
    assert gov_dec.decision == decision
    assert gov_dec.reason == reason


def test_governance_audit_model():
    gov_id = "GOV_1234567890ABCDEF"
    aud_id, aud_hash = compute_governance_audit_id(
        decision_id=gov_id,
        action="PROMOTE",
        timestamp="2026-08-04T12:00:00Z",
    )

    audit = GovernanceAudit(
        audit_id=aud_id,
        decision_id=gov_id,
        edge_id="EDG_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        evidence_ids=["EVR_1234567890ABCDEF"],
        experiment_id="EXP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        is_explainable=True,
        is_replayable=True,
        operator="AUDIT_ENGINE",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=aud_hash,
    )

    assert audit.audit_id == aud_id
    assert audit.decision_id == gov_id
