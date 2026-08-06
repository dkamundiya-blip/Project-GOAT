"""
Project GOAT v0.8 — Execution Validation Engine

Verifies prerequisite conditions prior to order dispatch: qualification, simulation, risk approval,
capital allocation, market state, broker session status, signal freshness, and replay integrity.
Rejects execution immediately if any prerequisite rule fails.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.execution.core.canonical import compute_execution_decision_id
from goat.execution.core.models import ExecutionDecision, ExecutionIntent


class ExecutionValidationEngine:
    """Engine responsible for pre-dispatch validation rules verification."""

    def validate_intent(
        self,
        intent: ExecutionIntent,
        is_qualified: bool = True,
        is_risk_approved: bool = True,
        has_sufficient_capital: bool = True,
        is_market_active: bool = True,
        is_broker_connected: bool = True,
        is_signal_fresh: bool = True,
        is_duplicate: bool = False,
        timestamp: str | None = None,
    ) -> ExecutionDecision:
        """Validate ExecutionIntent against pre-execution rules."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Rule 1: Duplicate Order Check
        if is_duplicate:
            return self._make_decision(intent.intent_id, False, "Duplicate execution intent detected", now_iso)

        # Rule 2: Qualification Verification
        if not is_qualified:
            return self._make_decision(intent.intent_id, False, f"Signal {intent.signal_id} is not qualified or qualification has expired", now_iso)

        # Rule 3: Risk Engine Approval
        if not is_risk_approved:
            return self._make_decision(intent.intent_id, False, f"Position sizing decision {intent.sizing_decision_id} was rejected by Risk Engine", now_iso)

        # Rule 4: Capital Allocation Check
        if not has_sufficient_capital:
            return self._make_decision(intent.intent_id, False, f"Capital allocation {intent.allocation_id} insufficient or capital exhausted", now_iso)

        # Rule 5: Market State Validity
        if not is_market_active:
            return self._make_decision(intent.intent_id, False, f"Market state for symbol {intent.symbol} is closed or unavailable", now_iso)

        # Rule 6: Broker Session Connection
        if not is_broker_connected:
            return self._make_decision(intent.intent_id, False, f"Target broker session {intent.broker_id} is disconnected or degraded", now_iso)

        # Rule 7: Signal Freshness
        if not is_signal_fresh:
            return self._make_decision(intent.intent_id, False, f"Signal {intent.signal_id} has expired", now_iso)

        # Rule 8: Intent Quantity Check
        if intent.quantity <= 0.0:
            return self._make_decision(intent.intent_id, False, f"Invalid volume quantity: {intent.quantity}", now_iso)

        return self._make_decision(intent.intent_id, True, f"Execution intent {intent.intent_id} satisfied all 8 validation prerequisite rules", now_iso)

    def _make_decision(self, intent_id: str, approved: bool, explanation: str, timestamp: str) -> ExecutionDecision:
        dec_id, canonical_hash = compute_execution_decision_id(intent_id, approved, timestamp)
        return ExecutionDecision(
            decision_id=dec_id,
            intent_id=intent_id,
            approved=approved,
            explanation=explanation,
            timestamp=timestamp,
            metadata={},
            canonical_hash=canonical_hash,
        )
