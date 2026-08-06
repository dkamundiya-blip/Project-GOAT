"""
Project GOAT v0.9 — Dedicated Unit Tests for Edge Retirement Engine
"""

import pytest

from goat.governance.core.canonical import compute_edge_id
from goat.governance.core.models import EdgeCandidate
from goat.governance.retirement.engine import EdgeRetirementEngine


@pytest.fixture
def retirement_engine():
    return EdgeRetirementEngine()


@pytest.fixture
def sample_candidate():
    edg_id, hash_val = compute_edge_id("HYP_1234567890ABCDEF", "Retirement Candidate Edge")
    return EdgeCandidate(
        edge_id=edg_id,
        title="Retirement Candidate Edge",
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=hash_val,
    )


def test_evaluate_retirement_clean(retirement_engine: EdgeRetirementEngine, sample_candidate: EdgeCandidate):
    assessment = retirement_engine.evaluate_retirement(candidate=sample_candidate)

    assert assessment.assessment_id.startswith("RTA_")
    assert assessment.is_retirement_recommended is False
    assert retirement_engine.get_assessment(assessment.assessment_id) is not None


@pytest.mark.parametrize(
    "deg, decline, shift, amd1",
    [
        (0.60, 0.0, False, False),
        (0.0, 0.40, False, False),
        (0.0, 0.0, True, False),
        (0.0, 0.0, False, True),
    ],
)
def test_evaluate_retirement_triggers(
    retirement_engine: EdgeRetirementEngine,
    sample_candidate: EdgeCandidate,
    deg: float,
    decline: float,
    shift: bool,
    amd1: bool,
):
    assessment = retirement_engine.evaluate_retirement(
        candidate=sample_candidate,
        expectancy_degradation=deg,
        confidence_decline=decline,
        structural_shift_detected=shift,
        amendment_001_violation=amd1,
    )

    assert assessment.is_retirement_recommended is True
