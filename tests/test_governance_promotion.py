"""
Project GOAT v0.9 — Dedicated Unit Tests for Edge Promotion Engine
"""

import pytest

from goat.governance.core.canonical import compute_edge_id
from goat.governance.core.models import EdgeCandidate
from goat.governance.promotion.engine import EdgePromotionEngine


@pytest.fixture
def promotion_engine():
    return EdgePromotionEngine()


@pytest.fixture
def sample_candidate():
    edg_id, hash_val = compute_edge_id("HYP_1234567890ABCDEF", "Sample Candidate Edge")
    return EdgeCandidate(
        edge_id=edg_id,
        title="Sample Candidate Edge",
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        evidence_ids=["EVR_1234567890ABCDEF"],
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=hash_val,
    )


def test_evaluate_promotion_all_passed(promotion_engine: EdgePromotionEngine, sample_candidate: EdgeCandidate):
    assessment = promotion_engine.evaluate_promotion(
        candidate=sample_candidate,
        hypothesis_valid=True,
        evidence_valid=True,
        experiment_valid=True,
        statistics_decision="SUPPORTED",
        live_validation_decision="PROMOTION_RECOMMENDED",
        constitution_compliant=True,
        research_protocol_compliant=True,
    )

    assert assessment.assessment_id.startswith("PRA_")
    assert assessment.is_promotable is True
    assert promotion_engine.get_assessment(assessment.assessment_id) is not None


@pytest.mark.parametrize(
    "hyp, ev, exp, stats, live, const, prsp",
    [
        (False, True, True, "SUPPORTED", "PROMOTION_RECOMMENDED", True, True),
        (True, False, True, "SUPPORTED", "PROMOTION_RECOMMENDED", True, True),
        (True, True, False, "SUPPORTED", "PROMOTION_RECOMMENDED", True, True),
        (True, True, True, "REJECTED", "PROMOTION_RECOMMENDED", True, True),
        (True, True, True, "SUPPORTED", "FAILED", True, True),
        (True, True, True, "SUPPORTED", "PROMOTION_RECOMMENDED", False, True),
        (True, True, True, "SUPPORTED", "PROMOTION_RECOMMENDED", True, False),
    ],
)
def test_evaluate_promotion_rejections(
    promotion_engine: EdgePromotionEngine,
    sample_candidate: EdgeCandidate,
    hyp: bool,
    ev: bool,
    exp: bool,
    stats: str,
    live: str,
    const: bool,
    prsp: bool,
):
    assessment = promotion_engine.evaluate_promotion(
        candidate=sample_candidate,
        hypothesis_valid=hyp,
        evidence_valid=ev,
        experiment_valid=exp,
        statistics_decision=stats,
        live_validation_decision=live,
        constitution_compliant=const,
        research_protocol_compliant=prsp,
    )

    assert assessment.is_promotable is False
