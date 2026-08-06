"""
Project GOAT v0.8 — Test Suite: Execution Lifecycle Engine (Exhaustive Matrix)
"""

import pytest

from goat.execution.core.enums import ExecutionState
from goat.execution.lifecycle.engine import ExecutionLifecycleEngine
from goat.marketdata.core.enums import DerivSymbol

SYMBOLS = [s.value for s in DerivSymbol]
VALID_PATHS = [
    [ExecutionState.CREATED, ExecutionState.VALIDATED, ExecutionState.READY, ExecutionState.DISPATCHED, ExecutionState.ACKNOWLEDGED, ExecutionState.FILLED],
    [ExecutionState.CREATED, ExecutionState.REJECTED],
    [ExecutionState.CREATED, ExecutionState.VALIDATED, ExecutionState.READY, ExecutionState.DISPATCHED, ExecutionState.REJECTED],
    [ExecutionState.CREATED, ExecutionState.VALIDATED, ExecutionState.READY, ExecutionState.DISPATCHED, ExecutionState.ACKNOWLEDGED, ExecutionState.PARTIALLY_FILLED, ExecutionState.FILLED],
    [ExecutionState.CREATED, ExecutionState.VALIDATED, ExecutionState.READY, ExecutionState.CANCELLED],
]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("path", VALID_PATHS)
def test_execution_lifecycle_transitions_matrix(symbol, path):
    engine = ExecutionLifecycleEngine()
    intent_id = f"EXI_{symbol}_1001"

    for state in path[1:]:
        entry = engine.transition_state(intent_id, state, explanation=f"Transition to {state.value}")
        assert entry.lifecycle_id.startswith("EXL_")
        assert entry.intent_id == intent_id
        assert entry.state == state
        assert engine.get_current_state(intent_id) == state

    history = engine.get_history(intent_id)
    assert len(history) == len(path) - 1
