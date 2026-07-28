"""
Project GOAT v0.6 — Validation Lifecycle State Machine

Enforces legal state transitions, prerequisite checks, and terminal state locks for candidate edge validation.
"""

from __future__ import annotations

from typing import ClassVar

from goat.research.edge.validation.exceptions import ValidationStateError
from goat.research.edge.validation.models import (
    StageDecision,
    ValidationLifecycleState,
    ValidationStage,
)


class ValidationStateMachine:
    """State machine governing CandidateEdge validation lifecycle transitions."""

    LEGAL_TRANSITIONS: ClassVar[dict[ValidationLifecycleState, set[ValidationLifecycleState]]] = {
        ValidationLifecycleState.REGISTERED: {
            ValidationLifecycleState.DISCOVERY_VALIDATION,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.DISCOVERY_VALIDATION: {
            ValidationLifecycleState.RETENTION_VALIDATION,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.RETENTION_VALIDATION: {
            ValidationLifecycleState.TEMPORAL_STABILITY,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.TEMPORAL_STABILITY: {
            ValidationLifecycleState.PARAMETER_ROBUSTNESS,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.PARAMETER_ROBUSTNESS: {
            ValidationLifecycleState.FALSIFICATION,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.FALSIFICATION: {
            ValidationLifecycleState.CROSS_CONTEXT_REPLICATION,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.CROSS_CONTEXT_REPLICATION: {
            ValidationLifecycleState.CONFIRMATORY_READY,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.CONFIRMATORY_READY: {
            ValidationLifecycleState.CONFIRMATORY_VALIDATION,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.CONFIRMATORY_VALIDATION: {
            ValidationLifecycleState.VALIDATED,
            ValidationLifecycleState.REJECTED,
        },
        ValidationLifecycleState.VALIDATED: set(),
        ValidationLifecycleState.REJECTED: set(),
    }

    STAGE_TO_PREREQUISITE_STATE: ClassVar[dict[ValidationStage, ValidationLifecycleState]] = {
        ValidationStage.STAGE_A_DISCOVERY: ValidationLifecycleState.REGISTERED,
        ValidationStage.STAGE_B_RETENTION: ValidationLifecycleState.DISCOVERY_VALIDATION,
        ValidationStage.STAGE_C_TEMPORAL: ValidationLifecycleState.RETENTION_VALIDATION,
        ValidationStage.STAGE_D_ROBUSTNESS: ValidationLifecycleState.TEMPORAL_STABILITY,
        ValidationStage.STAGE_E_FALSIFICATION: ValidationLifecycleState.PARAMETER_ROBUSTNESS,
        ValidationStage.STAGE_F_REPLICATION: ValidationLifecycleState.FALSIFICATION,
        ValidationStage.STAGE_G_HOLDOUT: ValidationLifecycleState.CONFIRMATORY_READY,
    }

    def __init__(self, initial_state: ValidationLifecycleState = ValidationLifecycleState.REGISTERED) -> None:
        self._state = initial_state

    @property
    def current_state(self) -> ValidationLifecycleState:
        return self._state

    def transition_to(self, target_state: ValidationLifecycleState) -> ValidationLifecycleState:
        """Attempt to transition to target_state. Raises ValidationStateError if illegal."""
        if self._state in (ValidationLifecycleState.VALIDATED, ValidationLifecycleState.REJECTED):
            raise ValidationStateError(
                f"Cannot transition out of terminal state '{self._state.value}' to '{target_state.value}'"
            )

        allowed = self.LEGAL_TRANSITIONS.get(self._state, set())
        if target_state not in allowed:
            raise ValidationStateError(
                f"Illegal state transition from '{self._state.value}' to '{target_state.value}'"
            )

        self._state = target_state
        return self._state

    def verify_stage_prerequisite(self, stage: ValidationStage) -> None:
        """Verify current state is legal prerequisite for evaluating stage."""
        prereq = self.STAGE_TO_PREREQUISITE_STATE.get(stage)
        if prereq and self._state != prereq:
            raise ValidationStateError(
                f"Cannot execute '{stage.value}' from state '{self._state.value}'; required prerequisite is '{prereq.value}'"
            )

    def handle_stage_decision(
        self, stage: ValidationStage, decision: StageDecision
    ) -> ValidationLifecycleState:
        """Advance state machine based on stage decision."""
        if decision == StageDecision.PASS:
            if stage == ValidationStage.STAGE_A_DISCOVERY:
                return self.transition_to(ValidationLifecycleState.DISCOVERY_VALIDATION)
            elif stage == ValidationStage.STAGE_B_RETENTION:
                return self.transition_to(ValidationLifecycleState.RETENTION_VALIDATION)
            elif stage == ValidationStage.STAGE_C_TEMPORAL:
                return self.transition_to(ValidationLifecycleState.TEMPORAL_STABILITY)
            elif stage == ValidationStage.STAGE_D_ROBUSTNESS:
                return self.transition_to(ValidationLifecycleState.PARAMETER_ROBUSTNESS)
            elif stage == ValidationStage.STAGE_E_FALSIFICATION:
                return self.transition_to(ValidationLifecycleState.FALSIFICATION)
            elif stage == ValidationStage.STAGE_F_REPLICATION:
                self.transition_to(ValidationLifecycleState.CROSS_CONTEXT_REPLICATION)
                return self.transition_to(ValidationLifecycleState.CONFIRMATORY_READY)
            elif stage == ValidationStage.STAGE_G_HOLDOUT:
                self.transition_to(ValidationLifecycleState.CONFIRMATORY_VALIDATION)
                return self.transition_to(ValidationLifecycleState.VALIDATED)
            else:
                raise ValidationStateError(f"Unknown stage '{stage}'")

        elif decision in (StageDecision.FAIL, StageDecision.INSUFFICIENT_EVIDENCE):
            return self.transition_to(ValidationLifecycleState.REJECTED)

        elif decision == StageDecision.NOT_RUN:
            raise ValidationStateError("Cannot advance state machine on NOT_RUN decision")

        else:
            raise ValidationStateError(f"Unhandled StageDecision '{decision}'")
