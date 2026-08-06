"""
Project GOAT v0.7 — Step 5.7 Scientific Hypothesis Validation Engine Test Suite
"""

from __future__ import annotations

import pytest

from goat.validation import (
    DecisionType,
    ScientificHypothesis,
    ScientificHypothesisValidationEngine,
    ValidationEngineError,
    ValidationRun,
    ValidationState,
    ValidationThresholds,
)


@pytest.mark.parametrize("idx", list(range(15)))
def test_engine_hypothesis_registration_parametrized(idx: int):
    """Verify hypothesis registration across multiple inputs."""
    engine = ScientificHypothesisValidationEngine()
    hyp = engine.register_hypothesis(
        title=f"Edge Strategy {idx}",
        description=f"Description for strategy {idx}",
        originating_experiment=f"EXP_{idx}",
        originating_study=f"STD_{idx}",
    )
    assert isinstance(hyp, ScientificHypothesis)
    assert hyp.hypothesis_id.startswith("HYP_")
    assert hyp.title == f"Edge Strategy {idx}"
    assert hyp.validation_state == ValidationState.PENDING


def test_engine_duplicate_hypothesis_rejection():
    """Verify engine rejects duplicate hypothesis registration."""
    engine = ScientificHypothesisValidationEngine()
    engine.register_hypothesis(title="Unique Title", originating_experiment="EXP_1")
    with pytest.raises(ValidationEngineError):
        engine.register_hypothesis(title="Unique Title", originating_experiment="EXP_1")


def test_engine_empty_title_rejection():
    """Verify engine rejects empty hypothesis title."""
    engine = ScientificHypothesisValidationEngine()
    with pytest.raises(ValidationEngineError):
        engine.register_hypothesis(title="   ")


@pytest.mark.parametrize("etype", ["experiment", "study", "consensus", "execution"])
def test_engine_evidence_submission_types_parametrized(etype: str):
    """Verify evidence submission for all 4 evidence types."""
    engine = ScientificHypothesisValidationEngine()
    hyp = engine.register_hypothesis(title="Multi-type Evidence Hyp", originating_experiment="EXP_1")

    ev = engine.submit_evidence(
        hypothesis_id=hyp.hypothesis_id,
        evidence_type=etype,
        experiment_reference="EXP_1",
        study_reference="STD_1",
        consensus_reference="CNS_1",
        execution_reference="SES_1",
        confidence=0.8,
        supports=True,
    )
    assert ev.evidence_id.startswith("VEV_")
    assert ev.evidence_type == etype


def test_engine_unregistered_hypothesis_evidence():
    """Verify submit_evidence raises error for unregistered hypothesis."""
    engine = ScientificHypothesisValidationEngine()
    with pytest.raises(ValidationEngineError):
        engine.submit_evidence(hypothesis_id="HYP_UNREGISTERED", evidence_type="experiment")


def test_engine_invalid_evidence_type():
    """Verify submit_evidence raises error for invalid evidence type."""
    engine = ScientificHypothesisValidationEngine()
    hyp = engine.register_hypothesis(title="Hyp", originating_experiment="EXP_1")
    with pytest.raises(ValidationEngineError):
        engine.submit_evidence(hypothesis_id=hyp.hypothesis_id, evidence_type="invalid_type")


@pytest.mark.parametrize("idx", list(range(10)))
def test_engine_full_validation_pipeline_accepted_parametrized(idx: int):
    """Verify complete validation pipeline execution producing ACCEPTED decision across runs."""
    engine = ScientificHypothesisValidationEngine()
    hyp = engine.register_hypothesis(title=f"Breakout Momentum {idx}", originating_experiment=f"EXP_{idx}")

    engine.submit_evidence(hyp.hypothesis_id, "experiment", experiment_reference=f"EXP_{idx}", confidence=0.9, weight=2.0, supports=True)
    engine.submit_evidence(hyp.hypothesis_id, "study", study_reference=f"STD_{idx}", confidence=0.85, weight=2.0, supports=True)
    engine.submit_evidence(hyp.hypothesis_id, "consensus", consensus_reference=f"CNS_{idx}", confidence=0.95, weight=2.5, supports=True)
    engine.submit_evidence(hyp.hypothesis_id, "execution", execution_reference=f"SES_{idx}", confidence=0.8, weight=2.0, supports=True)

    run = engine.run_validation(
        hypothesis_id=hyp.hypothesis_id,
        replication_count=3,
        cross_context_count=3,
        consistent_periods=5,
        total_periods=5,
    )

    assert isinstance(run, ValidationRun)
    assert run.validation_id.startswith("VRN_")
    assert run.validation_decision == "accepted"
    assert run.validation_state == ValidationState.DECIDED
    assert engine.verify_integrity(run.validation_id) is True


def test_engine_full_validation_pipeline_rejected():
    """Verify complete validation pipeline execution producing REJECTED decision."""
    engine = ScientificHypothesisValidationEngine()
    hyp = engine.register_hypothesis(title="Flawed Strategy", originating_experiment="EXP_2")

    engine.submit_evidence(hyp.hypothesis_id, "experiment", experiment_reference="EXP_2", confidence=0.2, weight=1.0, supports=False)
    engine.submit_evidence(hyp.hypothesis_id, "study", study_reference="STD_2", confidence=0.1, weight=1.0, supports=False)
    engine.submit_evidence(hyp.hypothesis_id, "execution", execution_reference="SES_2", confidence=0.15, weight=1.0, supports=False)

    run = engine.run_validation(hypothesis_id=hyp.hypothesis_id)
    assert run.validation_decision == "rejected"


def test_engine_full_validation_pipeline_needs_more_data():
    """Verify validation run producing NEEDS_MORE_DATA when evidence count < min_evidence_count."""
    thresholds = ValidationThresholds(min_evidence_count=5)
    engine = ScientificHypothesisValidationEngine(thresholds)
    hyp = engine.register_hypothesis(title="New Hypothesis", originating_experiment="EXP_3")

    engine.submit_evidence(hyp.hypothesis_id, "experiment", experiment_reference="EXP_3", confidence=0.9, supports=True)
    engine.submit_evidence(hyp.hypothesis_id, "study", study_reference="STD_3", confidence=0.9, supports=True)

    run = engine.run_validation(hypothesis_id=hyp.hypothesis_id)
    assert run.validation_decision == "needs_more_data"


def test_engine_validation_replay():
    """Verify replay_validation reproduces identical run, evidence, and decision."""
    engine = ScientificHypothesisValidationEngine()
    hyp = engine.register_hypothesis(title="Replay Test", originating_experiment="EXP_4")
    engine.submit_evidence(hyp.hypothesis_id, "experiment", experiment_reference="EXP_4", confidence=0.9, supports=True)
    engine.submit_evidence(hyp.hypothesis_id, "study", study_reference="STD_4", confidence=0.8, supports=True)
    engine.submit_evidence(hyp.hypothesis_id, "consensus", consensus_reference="CNS_4", confidence=0.9, supports=True)

    run = engine.run_validation(hyp.hypothesis_id)
    replayed_run, replayed_evidence, replayed_decision = engine.replay_validation(run.validation_id)

    assert replayed_run.validation_id == run.validation_id
    assert replayed_run.replay_hash == run.replay_hash
    assert len(replayed_evidence) == 3
    assert replayed_decision.decision_id == run.decision_id
