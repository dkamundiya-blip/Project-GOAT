"""
Project GOAT v0.8 — Trade Tracking Engine

Manages deterministic trade lifecycle state machine transitions, validates illegal moves,
maintains state timestamps, and links execution intents, portfolio positions, and broker executions.
"""

from __future__ import annotations

from typing import Any

from goat.lifecycle.core.canonical import compute_lifecycle_transition_id, compute_trade_lifecycle_id, compute_trade_state_id
from goat.lifecycle.core.enums import TradeState
from goat.lifecycle.core.models import LifecycleTransition, TradeLifecycle, TradeStateRecord

VALID_TRANSITIONS: dict[TradeState, set[TradeState]] = {
    TradeState.CREATED: {TradeState.SUBMITTED, TradeState.CANCELLED, TradeState.REJECTED, TradeState.FAILED},
    TradeState.SUBMITTED: {
        TradeState.ACKNOWLEDGED,
        TradeState.PARTIALLY_FILLED,
        TradeState.FILLED,
        TradeState.REJECTED,
        TradeState.CANCELLED,
        TradeState.FAILED,
    },
    TradeState.ACKNOWLEDGED: {
        TradeState.PARTIALLY_FILLED,
        TradeState.FILLED,
        TradeState.OPEN,
        TradeState.REJECTED,
        TradeState.CANCELLED,
        TradeState.FAILED,
    },
    TradeState.PARTIALLY_FILLED: {
        TradeState.PARTIALLY_FILLED,
        TradeState.FILLED,
        TradeState.OPEN,
        TradeState.CANCELLED,
        TradeState.FAILED,
    },
    TradeState.FILLED: {TradeState.OPEN, TradeState.PARTIALLY_CLOSED, TradeState.CLOSED, TradeState.FAILED},
    TradeState.OPEN: {
        TradeState.MODIFIED,
        TradeState.SL_UPDATED,
        TradeState.TP_UPDATED,
        TradeState.TRAILING_UPDATED,
        TradeState.PARTIALLY_CLOSED,
        TradeState.CLOSED,
        TradeState.FAILED,
    },
    TradeState.MODIFIED: {
        TradeState.OPEN,
        TradeState.SL_UPDATED,
        TradeState.TP_UPDATED,
        TradeState.TRAILING_UPDATED,
        TradeState.PARTIALLY_CLOSED,
        TradeState.CLOSED,
        TradeState.FAILED,
    },
    TradeState.SL_UPDATED: {
        TradeState.OPEN,
        TradeState.MODIFIED,
        TradeState.SL_UPDATED,
        TradeState.TP_UPDATED,
        TradeState.TRAILING_UPDATED,
        TradeState.PARTIALLY_CLOSED,
        TradeState.CLOSED,
        TradeState.FAILED,
    },
    TradeState.TP_UPDATED: {
        TradeState.OPEN,
        TradeState.MODIFIED,
        TradeState.SL_UPDATED,
        TradeState.TP_UPDATED,
        TradeState.TRAILING_UPDATED,
        TradeState.PARTIALLY_CLOSED,
        TradeState.CLOSED,
        TradeState.FAILED,
    },
    TradeState.TRAILING_UPDATED: {
        TradeState.OPEN,
        TradeState.MODIFIED,
        TradeState.SL_UPDATED,
        TradeState.TP_UPDATED,
        TradeState.TRAILING_UPDATED,
        TradeState.PARTIALLY_CLOSED,
        TradeState.CLOSED,
        TradeState.FAILED,
    },
    TradeState.PARTIALLY_CLOSED: {
        TradeState.OPEN,
        TradeState.MODIFIED,
        TradeState.SL_UPDATED,
        TradeState.TP_UPDATED,
        TradeState.TRAILING_UPDATED,
        TradeState.PARTIALLY_CLOSED,
        TradeState.CLOSED,
        TradeState.FAILED,
    },
    TradeState.CLOSED: set(),
    TradeState.CANCELLED: set(),
    TradeState.REJECTED: set(),
    TradeState.FAILED: set(),
}


class TradeTrackingEngine:
    """Engine tracking trade lifecycle state transitions and maintaining immutable transition history."""

    def __init__(self):
        self._lifecycles: dict[str, TradeLifecycle] = {}  # lifecycle_id -> TradeLifecycle
        self._transitions: dict[str, list[LifecycleTransition]] = {}  # lifecycle_id -> list of transitions
        self._state_records: dict[str, list[TradeStateRecord]] = {}

    def create_lifecycle(
        self,
        intent_id: str,
        symbol: str,
        side: str,
        quantity: float,
        created_at: str,
        metadata: dict[str, Any] | None = None,
    ) -> TradeLifecycle:
        """Create a new TradeLifecycle instance starting in CREATED state."""
        if quantity <= 0.0:
            raise ValueError(f"Quantity must be strictly positive (> 0.0), got {quantity}")

        side_upper = str(side).strip().upper()
        sym_upper = str(symbol).strip().upper()
        meta = metadata or {}

        trl_id, trl_hash = compute_trade_lifecycle_id(
            intent_id=intent_id,
            symbol=sym_upper,
            side=side_upper,
            created_at=created_at,
        )

        lifecycle = TradeLifecycle(
            lifecycle_id=trl_id,
            intent_id=str(intent_id).strip(),
            symbol=sym_upper,
            side=side_upper,
            quantity=float(quantity),
            current_state=TradeState.CREATED,
            previous_state=None,
            created_at=created_at,
            updated_at=created_at,
            metadata=meta,
            canonical_hash=trl_hash,
        )

        self._lifecycles[trl_id] = lifecycle
        self._transitions[trl_id] = []
        self._state_records[trl_id] = []

        # Record initial state
        tst_id, tst_hash = compute_trade_state_id(trl_id, TradeState.CREATED.value, created_at)
        st_rec = TradeStateRecord(
            state_id=tst_id,
            lifecycle_id=trl_id,
            state=TradeState.CREATED,
            timestamp=created_at,
            canonical_hash=tst_hash,
        )
        self._state_records[trl_id].append(st_rec)

        return lifecycle

    def validate_transition(self, current_state: TradeState, target_state: TradeState) -> bool:
        """Validate if transition from current_state to target_state is legal."""
        allowed = VALID_TRANSITIONS.get(current_state, set())
        return target_state in allowed

    def transition_state(
        self,
        lifecycle_id: str,
        new_state: TradeState | str,
        timestamp: str,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> tuple[TradeLifecycle, LifecycleTransition]:
        """Perform deterministic state transition with strict validation rules."""
        lifecycle = self._lifecycles.get(lifecycle_id)
        if lifecycle is None:
            raise KeyError(f"Trade Lifecycle ID {lifecycle_id} not found.")

        target_enum = TradeState(str(new_state).upper()) if not isinstance(new_state, TradeState) else new_state
        current_enum = lifecycle.current_state

        if not self.validate_transition(current_enum, target_enum):
            raise ValueError(f"Illegal state transition from {current_enum.value} to {target_enum.value} for lifecycle {lifecycle_id}")

        meta = metadata or {}
        is_terminal = target_enum in {TradeState.CLOSED, TradeState.CANCELLED, TradeState.REJECTED, TradeState.FAILED}
        closed_ts = timestamp if is_terminal else lifecycle.closed_at

        # Build updated TradeLifecycle model
        updated_lifecycle = TradeLifecycle(
            lifecycle_id=lifecycle.lifecycle_id,
            intent_id=lifecycle.intent_id,
            symbol=lifecycle.symbol,
            side=lifecycle.side,
            quantity=lifecycle.quantity,
            position_id=lifecycle.position_id,
            broker_execution_id=lifecycle.broker_execution_id,
            current_state=target_enum,
            previous_state=current_enum,
            created_at=lifecycle.created_at,
            updated_at=timestamp,
            closed_at=closed_ts,
            metadata={**lifecycle.metadata, **meta},
            canonical_hash=lifecycle.canonical_hash,
        )

        # Build LifecycleTransition log entry
        ltr_id, ltr_hash = compute_lifecycle_transition_id(
            lifecycle_id=lifecycle_id,
            from_state=current_enum.value,
            to_state=target_enum.value,
            timestamp=timestamp,
        )

        transition = LifecycleTransition(
            transition_id=ltr_id,
            lifecycle_id=lifecycle_id,
            from_state=current_enum,
            to_state=target_enum,
            reason=reason or f"Transition to {target_enum.value}",
            timestamp=timestamp,
            metadata=meta,
            canonical_hash=ltr_hash,
        )

        # State record
        tst_id, tst_hash = compute_trade_state_id(lifecycle_id, target_enum.value, timestamp)
        st_rec = TradeStateRecord(
            state_id=tst_id,
            lifecycle_id=lifecycle_id,
            state=target_enum,
            timestamp=timestamp,
            canonical_hash=tst_hash,
        )

        self._lifecycles[lifecycle_id] = updated_lifecycle
        self._transitions[lifecycle_id].append(transition)
        self._state_records[lifecycle_id].append(st_rec)

        return updated_lifecycle, transition

    def associate_position(self, lifecycle_id: str, position_id: str, timestamp: str) -> TradeLifecycle:
        """Associate portfolio position ID with trade lifecycle."""
        lifecycle = self._lifecycles.get(lifecycle_id)
        if lifecycle is None:
            raise KeyError(f"Trade Lifecycle ID {lifecycle_id} not found.")

        updated = TradeLifecycle(
            lifecycle_id=lifecycle.lifecycle_id,
            intent_id=lifecycle.intent_id,
            symbol=lifecycle.symbol,
            side=lifecycle.side,
            quantity=lifecycle.quantity,
            position_id=str(position_id).strip(),
            broker_execution_id=lifecycle.broker_execution_id,
            current_state=lifecycle.current_state,
            previous_state=lifecycle.previous_state,
            created_at=lifecycle.created_at,
            updated_at=timestamp,
            closed_at=lifecycle.closed_at,
            metadata=lifecycle.metadata,
            canonical_hash=lifecycle.canonical_hash,
        )
        self._lifecycles[lifecycle_id] = updated
        return updated

    def associate_broker_execution(self, lifecycle_id: str, broker_execution_id: str, timestamp: str) -> TradeLifecycle:
        """Associate broker execution fill ID with trade lifecycle."""
        lifecycle = self._lifecycles.get(lifecycle_id)
        if lifecycle is None:
            raise KeyError(f"Trade Lifecycle ID {lifecycle_id} not found.")

        updated = TradeLifecycle(
            lifecycle_id=lifecycle.lifecycle_id,
            intent_id=lifecycle.intent_id,
            symbol=lifecycle.symbol,
            side=lifecycle.side,
            quantity=lifecycle.quantity,
            position_id=lifecycle.position_id,
            broker_execution_id=str(broker_execution_id).strip(),
            current_state=lifecycle.current_state,
            previous_state=lifecycle.previous_state,
            created_at=lifecycle.created_at,
            updated_at=timestamp,
            closed_at=lifecycle.closed_at,
            metadata=lifecycle.metadata,
            canonical_hash=lifecycle.canonical_hash,
        )
        self._lifecycles[lifecycle_id] = updated
        return updated

    def get_lifecycle(self, lifecycle_id: str) -> TradeLifecycle | None:
        return self._lifecycles.get(lifecycle_id)

    def get_transitions(self, lifecycle_id: str) -> list[LifecycleTransition]:
        return list(self._transitions.get(lifecycle_id, []))

    def get_all_lifecycles(self) -> list[TradeLifecycle]:
        return list(self._lifecycles.values())
