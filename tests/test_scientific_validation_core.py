"""
Project GOAT v0.7 — Step 5.7 Core Validation Subsystem Test Suite
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from goat.validation.core import (
    DecisionType,
    ScientificHypothesis,
    ValidationContext,
    ValidationRun,
    ValidationState,
    compute_hypothesis_fingerprint,
    compute_hypothesis_id,
    compute_run_fingerprint,
    compute_run_id,
)


@pytest.mark.parametrize("state,expected", [
    (ValidationState.PENDING, "pending"),
    (ValidationState.COLLECTING_EVIDENCE, "collecting_evidence"),
    (ValidationState.EVALUATING, "evaluating"),
    (ValidationState.DECIDED, "decided"),
    (ValidationState.ARCHIVED, "archived"),
])
def test_validation_state_enum_parameterized(state: ValidationState, expected: str):
    """Verify ValidationState enum values via parametrization."""
    assert state.value == expected


@pytest.mark.parametrize("decision,expected", [
    (DecisionType.ACCEPTED, "accepted"),
    (DecisionType.REJECTED, "rejected"),
    (DecisionType.INCONCLUSIVE, "inconclusive"),
    (DecisionType.NEEDS_MORE_DATA, "needs_more_data"),
    (DecisionType.INVALID_HYPOTHESIS, "invalid_hypothesis"),
])
def test_decision_type_enum_parameterized(decision: DecisionType, expected: str):
    """Verify DecisionType enum values via parametrization."""
    assert decision.value == expected


@pytest.mark.parametrize("idx", list(range(10)))
def test_hypothesis_fingerprint_determinism_parametrized(idx: int):
    """Verify deterministic hypothesis fingerprint generation across multiple inputs."""
    title = f"Hypothesis_{idx}"
    exp = f"EXP_{idx}"
    std = f"STD_{idx}"
    fp1 = compute_hypothesis_fingerprint(title, exp, std, "1.0.0")
    fp2 = compute_hypothesis_fingerprint(title, exp, std, "1.0.0")
    assert fp1 == fp2
    assert fp1.startswith("HYPFP_")
    assert len(fp1) == 70


@pytest.mark.parametrize("idx", list(range(10)))
def test_hypothesis_id_determinism_parametrized(idx: int):
    """Verify deterministic hypothesis ID and hash computation across multiple inputs."""
    fp = compute_hypothesis_fingerprint(f"Title_{idx}", f"EXP_{idx}", f"STD_{idx}")
    hyp_id1, hash1 = compute_hypothesis_id(fp, "1.0.0")
    hyp_id2, hash2 = compute_hypothesis_id(fp, "1.0.0")

    assert hyp_id1.startswith("HYP_")
    assert len(hyp_id1) == 20
    assert len(hash1) == 64
    assert hyp_id1 == hyp_id2
    assert hash1 == hash2


def test_scientific_hypothesis_model_immutability():
    """Verify ScientificHypothesis model immutability and schema validation."""
    fp = compute_hypothesis_fingerprint("Test Title", "EXP_1", "STD_1")
    hyp_id, canon_hash = compute_hypothesis_id(fp)

    hyp = ScientificHypothesis(
        hypothesis_id=hyp_id,
        canonical_hash=canon_hash,
        scientific_fingerprint=fp,
        title="Test Title",
        creation_time="2026-01-01T00:00:00Z",
    )

    assert hyp.hypothesis_id == hyp_id
    assert hyp.title == "Test Title"
    assert hyp.validation_state == ValidationState.PENDING

    with pytest.raises(ValidationError):
        hyp.title = "New Title"


def test_scientific_hypothesis_extra_forbid():
    """Verify ScientificHypothesis rejects extra fields."""
    fp = compute_hypothesis_fingerprint("Test Title", "EXP_1", "STD_1")
    hyp_id, canon_hash = compute_hypothesis_id(fp)

    with pytest.raises(ValidationError):
        ScientificHypothesis(
            hypothesis_id=hyp_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fp,
            title="Test Title",
            creation_time="2026-01-01T00:00:00Z",
            extra_unallowed_field="invalid",
        )


def test_scientific_hypothesis_invalid_id_pattern():
    """Verify ScientificHypothesis enforces regex pattern on hypothesis_id."""
    with pytest.raises(ValidationError):
        ScientificHypothesis(
            hypothesis_id="INVALID_ID",
            canonical_hash="0" * 64,
            scientific_fingerprint="HYPFP_" + "0" * 64,
            title="Test Title",
            creation_time="2026-01-01T00:00:00Z",
        )


@pytest.mark.parametrize("idx", list(range(10)))
def test_run_fingerprint_determinism_parametrized(idx: int):
    """Verify deterministic run fingerprint generation across multiple inputs."""
    fp1 = compute_run_fingerprint(f"HYP_{idx:016d}", [f"VEV_{idx}"], "1.0.0")
    fp2 = compute_run_fingerprint(f"HYP_{idx:016d}", [f"VEV_{idx}"], "1.0.0")
    assert fp1 == fp2
    assert fp1.startswith("VRNFP_")
    assert len(fp1) == 70


@pytest.mark.parametrize("idx", list(range(10)))
def test_run_id_determinism_parametrized(idx: int):
    """Verify deterministic run ID and hash computation across multiple inputs."""
    fp = compute_run_fingerprint(f"HYP_{idx:016d}", [f"VEV_{idx}"])
    run_id1, hash1 = compute_run_id(fp)
    run_id2, hash2 = compute_run_id(fp)

    assert run_id1.startswith("VRN_")
    assert len(run_id1) == 20
    assert len(hash1) == 64
    assert run_id1 == run_id2
    assert hash1 == hash2


def test_validation_run_model_immutability():
    """Verify ValidationRun model immutability."""
    fp = compute_run_fingerprint("HYP_1234567890ABCDEF", ["VEV_1"])
    run_id, canon_hash = compute_run_id(fp)

    run = ValidationRun(
        validation_id=run_id,
        canonical_hash=canon_hash,
        scientific_fingerprint=fp,
        hypothesis_id="HYP_1234567890ABCDEF",
        creation_timestamp="2026-01-01T00:00:00Z",
    )

    assert run.validation_id == run_id
    assert run.validation_state == ValidationState.PENDING

    with pytest.raises(ValidationError):
        run.validation_state = ValidationState.DECIDED


def test_validation_context_model():
    """Verify ValidationContext initialization and immutability."""
    ctx = ValidationContext(
        hypothesis_ids=["HYP_1"],
        validation_run_ids=["VRN_1"],
        metadata={"user": "tester"},
    )
    assert ctx.hypothesis_ids == ["HYP_1"]
    assert ctx.metadata["user"] == "tester"

    with pytest.raises(ValidationError):
        ctx.hypothesis_ids = ["HYP_2"]
