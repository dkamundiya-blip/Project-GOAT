"""
Project GOAT v0.6 — Validation State Machine Unit Tests
"""

import pytest

from goat.research.edge.validation.exceptions import ValidationStateError
from goat.research.edge.validation.models import (
    StageDecision,
    ValidationLifecycleState,
    ValidationStage,
)
from goat.research.edge.validation.state import ValidationStateMachine


def test_validation_state_machine_legal_progression():
    sm = ValidationStateMachine(ValidationLifecycleState.REGISTERED)
    assert sm.current_state == ValidationLifecycleState.REGISTERED

    sm.verify_stage_prerequisite(ValidationStage.STAGE_A_DISCOVERY)
    sm.handle_stage_decision(ValidationStage.STAGE_A_DISCOVERY, StageDecision.PASS)
    assert sm.current_state == ValidationLifecycleState.DISCOVERY_VALIDATION

    sm.verify_stage_prerequisite(ValidationStage.STAGE_B_RETENTION)
    sm.handle_stage_decision(ValidationStage.STAGE_B_RETENTION, StageDecision.PASS)
    assert sm.current_state == ValidationLifecycleState.RETENTION_VALIDATION

    sm.verify_stage_prerequisite(ValidationStage.STAGE_C_TEMPORAL)
    sm.handle_stage_decision(ValidationStage.STAGE_C_TEMPORAL, StageDecision.PASS)
    assert sm.current_state == ValidationLifecycleState.TEMPORAL_STABILITY

    sm.verify_stage_prerequisite(ValidationStage.STAGE_D_ROBUSTNESS)
    sm.handle_stage_decision(ValidationStage.STAGE_D_ROBUSTNESS, StageDecision.PASS)
    assert sm.current_state == ValidationLifecycleState.PARAMETER_ROBUSTNESS

    sm.verify_stage_prerequisite(ValidationStage.STAGE_E_FALSIFICATION)
    sm.handle_stage_decision(ValidationStage.STAGE_E_FALSIFICATION, StageDecision.PASS)
    assert sm.current_state == ValidationLifecycleState.FALSIFICATION

    sm.verify_stage_prerequisite(ValidationStage.STAGE_F_REPLICATION)
    sm.handle_stage_decision(ValidationStage.STAGE_F_REPLICATION, StageDecision.PASS)
    assert sm.current_state == ValidationLifecycleState.CONFIRMATORY_READY

    sm.verify_stage_prerequisite(ValidationStage.STAGE_G_HOLDOUT)
    sm.handle_stage_decision(ValidationStage.STAGE_G_HOLDOUT, StageDecision.PASS)
    assert sm.current_state == ValidationLifecycleState.VALIDATED


def test_validation_state_machine_rejection_on_fail():
    sm = ValidationStateMachine(ValidationLifecycleState.REGISTERED)
    sm.handle_stage_decision(ValidationStage.STAGE_A_DISCOVERY, StageDecision.FAIL)
    assert sm.current_state == ValidationLifecycleState.REJECTED

    # Attempt transition out of terminal REJECTED state must fail
    with pytest.raises(ValidationStateError):
        sm.transition_to(ValidationLifecycleState.DISCOVERY_VALIDATION)


def test_validation_state_machine_illegal_jump():
    sm = ValidationStateMachine(ValidationLifecycleState.REGISTERED)
    with pytest.raises(ValidationStateError):
        sm.transition_to(ValidationLifecycleState.VALIDATED)


def test_stage_prerequisite_bypass_rejected():
    sm = ValidationStateMachine(ValidationLifecycleState.REGISTERED)
    with pytest.raises(ValidationStateError):
        sm.verify_stage_prerequisite(ValidationStage.STAGE_G_HOLDOUT)
