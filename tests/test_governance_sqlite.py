"""
Project GOAT v0.9 — Dedicated Unit Tests for Governance SQLite Persistence
"""

import pytest

from goat.governance.core.canonical import (
    compute_edge_id,
    compute_governance_audit_id,
    compute_governance_decision_id,
    compute_promotion_assessment_id,
    compute_retirement_assessment_id,
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
    PromotionAssessment,
    RetirementAssessment,
)
from goat.governance.persistence.sqlite import GovernancePersistenceContext


@pytest.fixture
def persistence_ctx():
    ctx = GovernancePersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.mark.parametrize("idx", range(1, 15))
def test_edge_repository_roundtrip(persistence_ctx: GovernancePersistenceContext, idx: int):
    hyp_id = f"HYP_{idx:016X}"
    edg_id, canonical_hash = compute_edge_id(hypothesis_id=hyp_id, title=f"Edge #{idx}")

    cand = EdgeCandidate(
        edge_id=edg_id,
        title=f"Edge #{idx}",
        hypothesis_id=hyp_id,
        evaluation_id=f"STE_{idx:016X}",
        experiment_id=f"EXP_{idx:016X}",
        validation_session_id=f"VSN_{idx:016X}",
        evidence_ids=[f"EVR_{idx:016X}"],
        status=EdgeStatus.APPROVED,
        created_timestamp="2026-08-04T12:00:00Z",
        metadata={"idx": idx},
        canonical_hash=canonical_hash,
    )

    persistence_ctx.edges.save(cand)
    fetched = persistence_ctx.edges.get_by_id(edg_id)

    assert fetched is not None
    assert fetched.edge_id == cand.edge_id
    assert fetched.status == EdgeStatus.APPROVED
    assert fetched.canonical_hash == cand.canonical_hash


@pytest.mark.parametrize("idx", range(1, 10))
def test_promotion_repository_roundtrip(persistence_ctx: GovernancePersistenceContext, idx: int):
    edg_id = f"EDG_{idx:016X}"
    hyp_id = f"HYP_{idx:016X}"
    pra_id, pra_hash = compute_promotion_assessment_id(edge_id=edg_id, hypothesis_id=hyp_id)

    pra = PromotionAssessment(
        assessment_id=pra_id,
        edge_id=edg_id,
        hypothesis_id=hyp_id,
        is_hypothesis_passed=True,
        is_evidence_complete=True,
        is_experiment_complete=True,
        is_statistics_complete=True,
        is_live_validation_complete=True,
        is_constitution_satisfied=True,
        is_research_protocol_satisfied=True,
        is_promotable=True,
        assessment_notes=f"Promotion note #{idx}",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=pra_hash,
    )

    persistence_ctx.promotions.save(pra)
    fetched = persistence_ctx.promotions.get_by_id(pra_id)

    assert fetched is not None
    assert fetched.assessment_id == pra_id
    assert fetched.is_promotable is True


@pytest.mark.parametrize("idx", range(1, 10))
def test_retirement_repository_roundtrip(persistence_ctx: GovernancePersistenceContext, idx: int):
    edg_id = f"EDG_{idx:016X}"
    hyp_id = f"HYP_{idx:016X}"
    rta_id, rta_hash = compute_retirement_assessment_id(edge_id=edg_id, hypothesis_id=hyp_id)

    rta = RetirementAssessment(
        assessment_id=rta_id,
        edge_id=edg_id,
        hypothesis_id=hyp_id,
        expectancy_degradation=0.1 * idx,
        confidence_decline=0.05 * idx,
        structural_shift_detected=False,
        amendment_001_violation=False,
        is_retirement_recommended=False,
        assessment_notes=f"Retirement note #{idx}",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=rta_hash,
    )

    persistence_ctx.retirements.save(rta)
    fetched = persistence_ctx.retirements.get_by_id(rta_id)

    assert fetched is not None
    assert fetched.assessment_id == rta_id
    assert fetched.expectancy_degradation == 0.1 * idx


@pytest.mark.parametrize("idx", range(1, 10))
def test_decision_repository_roundtrip(persistence_ctx: GovernancePersistenceContext, idx: int):
    edg_id = f"EDG_{idx:016X}"
    gov_id, gov_hash = compute_governance_decision_id(
        edge_id=edg_id,
        decision="PROMOTE",
        reason="LIVE_CONFIRMATION",
    )

    dec = GovernanceDecision(
        decision_id=gov_id,
        edge_id=edg_id,
        hypothesis_id=f"HYP_{idx:016X}",
        decision=GovernanceDecisionOutcome.PROMOTE,
        reason=GovernanceReason.LIVE_CONFIRMATION,
        rationale=f"Rationale statement #{idx}",
        authorizer="BOARD",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=gov_hash,
    )

    persistence_ctx.decisions.save(dec)
    fetched = persistence_ctx.decisions.get_by_id(gov_id)

    assert fetched is not None
    assert fetched.decision_id == gov_id
    assert fetched.decision == GovernanceDecisionOutcome.PROMOTE
