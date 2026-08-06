"""
Project GOAT v0.8 — Execution Intent Engine

Creates canonical ExecutionIntent objects from qualified scientific signals,
position sizing decisions, capital allocations, and target broker specifications.
Intent generation is strictly deterministic.
"""

from __future__ import annotations

from typing import Any

from goat.brokers.core.enums import OrderSide, OrderType, TimeInForce
from goat.execution.core.canonical import compute_execution_intent_id
from goat.execution.core.enums import ExecutionState
from goat.execution.core.models import ExecutionIntent


class ExecutionIntentEngine:
    """Engine responsible for deterministic construction of ExecutionIntent objects."""

    def create_intent(
        self,
        signal_id: str,
        sizing_decision_id: str,
        allocation_id: str,
        broker_id: str,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        time_in_force: TimeInForce = TimeInForce.GTC,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionIntent:
        """Create a deterministic canonical ExecutionIntent object."""
        quant_clean = round(float(quantity), 6)
        sym_clean = str(symbol).strip().upper()
        b_id_clean = str(broker_id).strip()

        intent_id, canonical_hash = compute_execution_intent_id(
            signal_id=signal_id,
            broker_id=b_id_clean,
            symbol=sym_clean,
            side=side.value,
            quantity=quant_clean,
        )

        return ExecutionIntent(
            intent_id=intent_id,
            signal_id=str(signal_id).strip(),
            sizing_decision_id=str(sizing_decision_id).strip(),
            allocation_id=str(allocation_id).strip(),
            broker_id=b_id_clean,
            symbol=sym_clean,
            side=side,
            quantity=quant_clean,
            order_type=order_type,
            time_in_force=time_in_force,
            stop_loss=round(float(stop_loss), 5) if stop_loss is not None else None,
            take_profit=round(float(take_profit), 5) if take_profit is not None else None,
            status=ExecutionState.CREATED,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )
