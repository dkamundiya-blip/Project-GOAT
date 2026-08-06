"""
Project GOAT v0.7 — Step 5.7 Decisions Subsystem Test Suite
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from goat.validation.core import DecisionType
from goat.validation.decisions import (
    DecisionGenerator,
    ValidationDecision,
    ValidationRuleEngine,
    ValidationThresholds,
    compute_decision_id,
)
from goat.validation.statistics import ValidationScores


@pytest.mark.parametrize("idx", list(range(10)))
def test_decision_id_determinism_parametrized(idx: int):
    """Verify deterministic decision ID and hash generation across inputs."""
    did1, hash1 = compute_decision_id(f"VRN_{idx}", "accepted", "2026-01-01T00:00:00Z")
    did2, hash2 = compute_decision_id(f"VRN_{idx}", "accepted", "2026-01-01T00:00:00Z")

    assert did1.startswith("VDC_")
    assert len(did1) == 20
    assert len(hash1) == 64
    assert did1 == did2
    assert hash1 == hash2


def test_validation_decision_model_immutability():
    """Verify ValidationDecision model immutability."""
    did, dhash = compute_decision_id("VRN_1", "accepted", "2026-01-01T00:00:00Z")

    dec = ValidationDecision(
        decision_id=did,
        decision_hash=dhash,
        validation_run_id="VRN_1",
        decision_type=DecisionType.ACCEPTED,
        timestamp="2026-01-01T00:00:00Z",
    )

    assert dec.decision_type == DecisionType.ACCEPTED

    with pytest.raises(ValidationError):
        dec.decision_type = DecisionType.REJECTED


@pytest.mark.parametrize("count,expected_type", [
    (0, DecisionType.INVALID_HYPOTHESIS),
    (1, DecisionType.NEEDS_MORE_DATA),
    (2, DecisionType.NEEDS_MORE_DATA),
])
def test_rule_engine_low_evidence_count_parametrized(count: int, expected_type: DecisionType):
    """Verify Rule Engine decision types for low evidence counts."""
    rule_engine = ValidationRuleEngine(ValidationThresholds(min_evidence_count=3))
    scores = ValidationScores()
    res = rule_engine.evaluate(scores, evidence_count=count)
    assert res["decision_type"] == expected_type


@pytest.mark.parametrize("overall_conf,passed_count,expected_type", [
    (0.85, 5, DecisionType.ACCEPTED),
    (0.15, 1, DecisionType.REJECTED),
    (0.50, 3, DecisionType.INCONCLUSIVE),
])
def test_rule_engine_confidence_outcomes_parametrized(overall_conf: float, passed_count: int, expected_type: DecisionType):
    """Verify Rule Engine decision outcomes based on confidence and threshold passes."""
    rule_engine = ValidationRuleEngine()
    scores = ValidationScores(
        confidence_score=overall_conf,
        evidence_score=overall_conf,
        agreement_score=overall_conf,
        reproducibility_score=overall_conf,
        robustness_score=overall_conf,
        stability_score=overall_conf,
        validation_score=overall_conf,
        overall_confidence=overall_conf,
    )
    summary = {"overall": {"weighted_confidence": overall_conf}}

    res = rule_engine.evaluate(scores, evidence_count=5, evidence_summary=summary)
    assert res["decision_type"] == expected_type


def test_decision_generator():
    """Verify DecisionGenerator creates deterministic ValidationDecision."""
    generator = DecisionGenerator()
    scores = ValidationScores(overall_confidence=0.8)
    rule_result = {
        "decision_type": DecisionType.ACCEPTED,
        "reasoning": "Passed all thresholds",
        "threshold_results": {"confidence": {"passed": True}},
    }

    decision = generator.generate_decision(
        validation_run_id="VRN_100",
        scores=scores,
        rule_result=rule_result,
        evidence_ids=["VEV_1", "VEV_2"],
    )

    assert isinstance(decision, ValidationDecision)
    assert decision.decision_id.startswith("VDC_")
    assert decision.validation_run_id == "VRN_100"
    assert decision.decision_type == DecisionType.ACCEPTED
    assert decision.evidence_used == ["VEV_1", "VEV_2"]
