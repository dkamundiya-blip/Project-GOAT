"""
Project GOAT v0.7 — Signal Lifecycle State Machine Engine

Manages deterministic signal state transitions:
CREATED -> VALIDATED -> READY_FOR_DELIVERY -> DELIVERED -> ACKNOWLEDGED -> EXPIRED / ARCHIVED / INVALIDATED
"""

from __future__ import annotations

from typing import Any

from goat.signals.core.canonical import (
    compute_canonical_sha256,
    compute_lifecycle_event_id,
)
from goat.signals.core.enums import SignalLifecycleState
from goat.signals.core.models import SignalLifecycleEvent, TradingSignal


class SignalLifecycleEngine:
    """Engine managing deterministic trading signal state machine transitions."""

    # Allowed state transition map
    ALLOWED_TRANSITIONS: dict[SignalLifecycleState, set[SignalLifecycleState]] = {
        SignalLifecycleState.CREATED: {
            SignalLifecycleState.VALIDATED,
            SignalLifecycleState.INVALIDATED,
        },
        SignalLifecycleState.VALIDATED: {
            SignalLifecycleState.READY_FOR_DELIVERY,
            SignalLifecycleState.INVALIDATED,
        },
        SignalLifecycleState.READY_FOR_DELIVERY: {
            SignalLifecycleState.DELIVERED,
            SignalLifecycleState.EXPIRED,
            SignalLifecycleState.INVALIDATED,
        },
        SignalLifecycleState.DELIVERED: {
            SignalLifecycleState.ACKNOWLEDGED,
            SignalLifecycleState.EXPIRED,
            SignalLifecycleState.INVALIDATED,
        },
        SignalLifecycleState.ACKNOWLEDGED: {
            SignalLifecycleState.ARCHIVED,
            SignalLifecycleState.EXPIRED,
        },
        # Terminal states have no outward transitions
        SignalLifecycleState.EXPIRED: set(),
        SignalLifecycleState.ARCHIVED: set(),
        SignalLifecycleState.INVALIDATED: set(),
    }

    def transition_state(
        self,
        signal: TradingSignal,
        new_state: SignalLifecycleState,
        timestamp: str,
        reason: str = "",
    ) -> tuple[TradingSignal, SignalLifecycleEvent]:
        """Transition signal to a new lifecycle state deterministically.

        Args:
            signal: Current TradingSignal model.
            new_state: Target SignalLifecycleState enum.
            timestamp: ISO 8601 UTC timestamp string.
            reason: Transition explanation string.

        Returns:
            Tuple of (updated_TradingSignal, SignalLifecycleEvent).

        Raises:
            ValueError: If the requested state transition is illegal.
        """
        current_state = signal.lifecycle_state
        allowed = self.ALLOWED_TRANSITIONS.get(current_state, set())

        if new_state not in allowed:
            raise ValueError(
                f"Illegal signal lifecycle transition: '{current_state.value}' -> '{new_state.value}'. "
                f"Allowed target states: {[s.value for s in allowed]}."
            )

        event_id, event_hash = compute_lifecycle_event_id(
            signal.signal_id,
            current_state.value,
            new_state.value,
            timestamp,
        )

        event = SignalLifecycleEvent(
            lifecycle_event_id=event_id,
            signal_id=signal.signal_id,
            previous_state=current_state,
            current_state=new_state,
            event_timestamp=timestamp,
            triggering_reason=reason or f"State transition from '{current_state.value}' to '{new_state.value}'.",
            metadata={"previous_state": current_state.value, "new_state": new_state.value},
            canonical_hash=event_hash,
        )

        # Update signal with new state (re-creating frozen model)
        updated_dict = signal.dict()
        updated_dict["lifecycle_state"] = new_state
        updated_signal = TradingSignal(**updated_dict)

        return updated_signal, event
