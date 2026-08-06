"""
Project GOAT v0.9 — Dedicated Unit Tests for Validation Eligibility Engine
"""

import pytest

from goat.live_validation.core.enums import ValidationStatus
from goat.live_validation.eligibility.engine import ValidationEligibilityEngine


@pytest.fixture
def eligibility_engine():
    return ValidationEligibilityEngine()


@pytest.mark.parametrize("idx", range(1, 15))
def test_evaluate_eligibility_supported_success(eligibility_engine: ValidationEligibilityEngine, idx: int):
    hyp_id = f"HYP_{idx:016X}"
    ste_id = f"STE_{idx:016X}"
    exp_id = f"EXP_{idx:016X}"

    candidate = eligibility_engine.evaluate_eligibility(
        hypothesis_id=hyp_id,
        evaluation_id=ste_id,
        experiment_id=exp_id,
        statistical_decision="SUPPORTED",
        evidence_ids=[f"EVR_{idx:016X}"],
    )

    assert candidate.candidate_id.startswith("LVC_")
    assert candidate.hypothesis_id == hyp_id
    assert candidate.status == ValidationStatus.ELIGIBLE
    assert candidate.eligibility_score == 1.0
    assert eligibility_engine.get_candidate(candidate.candidate_id) is not None


@pytest.mark.parametrize("decision", ["INCONCLUSIVE", "REJECTED", "REQUIRES_MORE_DATA", "FAILED"])
def test_evaluate_eligibility_non_supported_rejection(eligibility_engine: ValidationEligibilityEngine, decision: str):
    with pytest.raises(ValueError):
        eligibility_engine.evaluate_eligibility(
            hypothesis_id="HYP_1234567890ABCDEF",
            evaluation_id="STE_1234567890ABCDEF",
            experiment_id="EXP_1234567890ABCDEF",
            statistical_decision=decision,
            evidence_ids=["EVR_1234567890ABCDEF"],
        )


def test_evaluate_eligibility_duplicate_active_hypothesis_rejection(eligibility_engine: ValidationEligibilityEngine):
    hyp_id = "HYP_1234567890ABCDEF"

    eligibility_engine.evaluate_eligibility(
        hypothesis_id=hyp_id,
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        statistical_decision="SUPPORTED",
        evidence_ids=["EVR_1234567890ABCDEF"],
    )

    with pytest.raises(ValueError):
        eligibility_engine.evaluate_eligibility(
            hypothesis_id=hyp_id,
            evaluation_id="STE_9999999999ABCDEF",
            experiment_id="EXP_9999999999ABCDEF",
            statistical_decision="SUPPORTED",
            evidence_ids=["EVR_9999999999ABCDEF"],
        )
