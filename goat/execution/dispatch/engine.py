"""
Project GOAT v0.8 — Execution Dispatch Engine

Translates validated ExecutionIntent into canonical Step 7.2 BrokerOrderIntent
and dispatches execution requests ONLY through AbstractBrokerAdapter implementations.
Contains zero direct broker API or network socket logic.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.brokers.contracts.adapter import AbstractBrokerAdapter
from goat.brokers.core.canonical import compute_order_intent_id
from goat.brokers.core.models import BrokerOrderIntent
from goat.execution.core.canonical import compute_execution_request_id
from goat.execution.core.models import ExecutionIntent, ExecutionRequest


class ExecutionDispatchEngine:
    """Engine responsible for translating ExecutionIntent to BrokerOrderIntent and dispatching via adapter."""

    def __init__(self, adapter: AbstractBrokerAdapter):
        self.adapter = adapter
        self._dispatch_history: list[ExecutionRequest] = []

    def dispatch_intent(self, intent: ExecutionIntent, timestamp: str | None = None) -> tuple[ExecutionRequest, dict[str, Any]]:
        """Translate ExecutionIntent to BrokerOrderIntent, dispatch via AbstractBrokerAdapter, and record ExecutionRequest."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()

        boi_id, boi_hash = compute_order_intent_id(
            broker_id=intent.broker_id,
            symbol=intent.symbol,
            side=intent.side.value,
            quantity=intent.quantity,
            order_type=intent.order_type.value,
            timestamp=now_iso,
        )

        broker_order_intent = BrokerOrderIntent(
            intent_id=boi_id,
            broker_id=intent.broker_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            order_type=intent.order_type,
            time_in_force=intent.time_in_force,
            stop_loss=intent.stop_loss,
            take_profit=intent.take_profit,
            comment=f"GOAT Execution {intent.intent_id}",
            metadata={"execution_intent_id": intent.intent_id, "signal_id": intent.signal_id},
            canonical_hash=boi_hash,
        )

        # Dispatch via AbstractBrokerAdapter contract
        fill_result = self.adapter.submit_order_intent(broker_order_intent)

        req_id, req_hash = compute_execution_request_id(intent.intent_id, intent.broker_id, now_iso)
        execution_request = ExecutionRequest(
            request_id=req_id,
            intent_id=intent.intent_id,
            broker_id=intent.broker_id,
            payload_dict=broker_order_intent.dict(),
            dispatched_at=now_iso,
            metadata={"fill_result": fill_result},
            canonical_hash=req_hash,
        )
        self._dispatch_history.append(execution_request)

        return execution_request, fill_result

    def get_dispatch_history(self) -> list[ExecutionRequest]:
        """Retrieve list of dispatched execution requests."""
        return list(self._dispatch_history)
