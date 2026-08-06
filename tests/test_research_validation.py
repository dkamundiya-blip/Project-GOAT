"""
Project GOAT v0.9 — Dedicated Unit Tests for Hypothesis Validation Engine
"""

import pytest
from pydantic import ValidationError

from goat.research.core.canonical import compute_hypothesis_id
from goat.research.core.models import ScientificHypothesis
from goat.research.validation.engine import HypothesisValidationEngine


@pytest.fixture
def validation_engine():
    return HypothesisValidationEngine()


@pytest.fixture
def valid_hypothesis():
    hyp_id, canonical_hash = compute_hypothesis_id(
        title="Valid Test Hypothesis",
        null_hypothesis="H0: Random distribution in synthetic price stream.",
        alternative_hypothesis="H1: Structural volatility expansion following low volatility compression.",
        author="TEST_QUANT",
    )
    return ScientificHypothesis(
        hypothesis_id=hyp_id,
        title="Valid Test Hypothesis",
        research_question="Does volatility compression predict directional expansion?",
        null_hypothesis="H0: Random distribution in synthetic price stream.",
        alternative_hypothesis="H1: Structural volatility expansion following low volatility compression.",
        expected_behaviour="Price moves outside 2.0 std dev channel upon expansion.",
        independent_variables=["volatility_std", "compression_ratio"],
        dependent_variables=["expansion_magnitude"],
        assumptions=["Continuous liquidity", "Normal execution"],
        risk_statement="Tail risk in macro gap.",
        success_criteria=["p < 0.01", "samples >= 500"],
        failure_criteria=["p >= 0.05"],
        author="TEST_QUANT",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )


def test_validation_engine_valid_hypothesis(validation_engine, valid_hypothesis):
    result = validation_engine.validate_hypothesis(valid_hypothesis)
    assert result.is_valid is True
    assert len(result.validation_errors) == 0
    assert result.hypothesis_id == valid_hypothesis.hypothesis_id
    assert result.validation_id.startswith("HVL_")


def test_field_integrity_title_too_short():
    with pytest.raises(ValidationError):
        ScientificHypothesis(
            hypothesis_id="HYP_1234567890ABCDEF",
            title="Ab",
            research_question="Valid Question?",
            null_hypothesis="H0: Null hypothesis statement.",
            alternative_hypothesis="H1: Alt hypothesis statement.",
            expected_behaviour="Valid expected behaviour.",
            created_timestamp="2026-08-04T12:00:00Z",
            updated_timestamp="2026-08-04T12:00:00Z",
        )


def test_field_integrity_rq_too_short():
    with pytest.raises(ValidationError):
        ScientificHypothesis(
            hypothesis_id="HYP_1234567890ABCDEF",
            title="Valid Title",
            research_question="Abcd",
            null_hypothesis="H0: Null hypothesis statement.",
            alternative_hypothesis="H1: Alt hypothesis statement.",
            expected_behaviour="Valid expected behaviour.",
            created_timestamp="2026-08-04T12:00:00Z",
            updated_timestamp="2026-08-04T12:00:00Z",
        )


@pytest.mark.parametrize(
    "forbidden_word",
    [
        "discretionary feeling",
        "intuitive gut",
        "magic indicator",
        "guaranteed profit",
    ],
)
def test_constitution_compliance_forbidden_terms(validation_engine, valid_hypothesis, forbidden_word: str):
    hyp_dict = valid_hypothesis.model_dump()
    hyp_dict["expected_behaviour"] = f"Uses {forbidden_word} to evaluate market."
    hyp = ScientificHypothesis(**hyp_dict)

    result = validation_engine.validate_hypothesis(hyp)
    assert result.is_valid is False
    assert any("violates scientific explainability" in e for e in result.validation_errors)


@pytest.mark.parametrize("i", range(1, 20))
def test_uniqueness_validation(validation_engine, valid_hypothesis, i: int):
    duplicate_hyp = ScientificHypothesis(**valid_hypothesis.model_dump())
    result = validation_engine.validate_hypothesis(valid_hypothesis, existing_hypotheses=[duplicate_hyp])
    assert result.is_valid is False
    assert any("Duplicate hypothesis" in e for e in result.validation_errors)


@pytest.mark.parametrize("num_criteria", range(0, 10))
def test_protocol_compliance_criteria_checks(validation_engine, valid_hypothesis, num_criteria: int):
    hyp_dict = valid_hypothesis.model_dump()
    if num_criteria == 0:
        hyp_dict["success_criteria"] = []
        hyp_dict["failure_criteria"] = []
        hyp = ScientificHypothesis(**hyp_dict)
        result = validation_engine.validate_hypothesis(hyp)
        assert result.is_valid is False
    else:
        hyp_dict["success_criteria"] = [f"Criterion {k}" for k in range(num_criteria)]
        hyp = ScientificHypothesis(**hyp_dict)
        result = validation_engine.validate_hypothesis(hyp)
        assert result.is_valid is True
