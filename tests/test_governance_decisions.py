"""
Project GOAT v0.9 — Dedicated Unit Tests for Edge Governance Decision Engine
"""

import pytest

from goat.governance.core.canonical import compute_edge_id
from goat.governance.core.enums import GovernanceDecisionOutcome, GovernanceReason
from goat.governance.core.models import EdgeCandidate
from goat.governance.governance.engine import EdgeGovernanceEngine
from goat.governance.promotion.engine import EdgePromotionEngine
from goat.governance.retirement.engine import EdgeRetirementEngine


@pytest.fixture
def gov_engine():
    return EdgeGovernanceEngine()


@pytest.fixture
def sample_candidate():
    edg_id, hash_val = compute_edge_id("HYP_1234567890ABCDEF", "Decision Candidate Edge")
    return EdgeCandidate(
        edge_id=edg_id,
        title="Decision Candidate Edge",
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=hash_val,
    )


def test_make_governance_decision_promote(gov_engine: EdgeGovernanceEngine, sample_candidate: EdgeCandidate):
    prom_engine = EdgePromotionEngine()
    ret_engine = EdgeRetirementEngine()

    pra = prom_engine.evaluate_promotion(candidate=sample_candidate, live_validation_decision="PROMOTION_RECOMMENDED")
    rta = ret_engine.evaluate_retirement(candidate=sample_candidate)

    decision = gov_engine.make_governance_decision(
        candidate=sample_candidate,
        promotion_assessment=pra,
        retirement_assessment=rta,
    )

    assert decision.decision_id.startswith("GOV_")
    assert decision.decision == GovernanceDecisionOutcome.PROMOTE
    assert decision.reason == GovernanceReason.LIVE_CONFIRMATION


def test_make_governance_decision_retire(gov_engine: EdgeGovernanceEngine, sample_candidate: EdgeCandidate):
    prom_engine = EdgePromotionEngine()
    ret_engine = EdgeRetirementEngine()

    pra = prom_engine.evaluate_promotion(candidate=sample_candidate)
    rta = ret_engine.evaluate_retirement(candidate=sample_candidate, structural_shift_detected=True)

    decision = gov_engine.make_governance_decision(
        candidate=sample_candidate,
        promotion_assessment=pra,
        retirement_assessment=rta,
    )

    assert decision.decision == GovernanceDecisionOutcome.RETIRE
    assert decision.reason == GovernanceReason.STRUCTURAL_SHIFT
