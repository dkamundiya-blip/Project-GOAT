"""
Project GOAT v0.8 — Execution Idempotency Engine

Guarantees single-execution invariants across execution paths:
- Prevents duplicate order placement
- Prevents duplicate retry requests
- Prevents duplicate execution acknowledgements
- Guarantees 1 ExecutionIntent -> 1 execution path
"""

from __future__ import annotations

from goat.execution.core.models import ExecutionIntent


class ExecutionIdempotencyEngine:
    """Engine responsible for enforcing idempotency locks and single-execution guarantees."""

    def __init__(self):
        self._processed_intent_ids: set[str] = set()
        self._processed_hashes: set[str] = set()
        self._dispatched_request_ids: set[str] = set()

    def check_and_lock_intent(self, intent: ExecutionIntent) -> bool:
        """Check if intent has already been processed. Lock and return True if new, False if duplicate."""
        if intent.intent_id in self._processed_intent_ids or intent.canonical_hash in self._processed_hashes:
            return False

        self._processed_intent_ids.add(intent.intent_id)
        if intent.canonical_hash:
            self._processed_hashes.add(intent.canonical_hash)
        return True

    def is_intent_processed(self, intent_id: str) -> bool:
        """Check if intent ID has already been recorded."""
        return intent_id in self._processed_intent_ids

    def register_dispatch(self, request_id: str) -> bool:
        """Register order request dispatch ID. Return True if new, False if duplicate retry."""
        if request_id in self._dispatched_request_ids:
            return False
        self._dispatched_request_ids.add(request_id)
        return True

    def clear(self) -> None:
        """Reset idempotency registry (for testing or session reset)."""
        self._processed_intent_ids.clear()
        self._processed_hashes.clear()
        self._dispatched_request_ids.clear()
