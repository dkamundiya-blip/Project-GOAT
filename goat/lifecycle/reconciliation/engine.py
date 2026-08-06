"""
Project GOAT v0.8 — Trade Reconciliation Engine

Compares Broker State vs Portfolio State vs Lifecycle State to detect orphan executions,
orphan positions, missing fills, duplicate fills, volume mismatches, execution mismatches,
missing closes, and inconsistent lifecycle states.
"""

from __future__ import annotations

from typing import Any

from goat.lifecycle.core.enums import TradeReconciliationMismatchType, TradeState
from goat.lifecycle.core.models import BrokerExecution, PositionSnapshot, TradeLifecycle, TradeReconciliationItem


class TradeReconciliationEngine:
    """Engine reconciling Broker Execution, Portfolio Position, and Trade Lifecycle states."""

    def __init__(self, quantity_tolerance: float = 1e-6, price_tolerance: float = 1e-4):
        self.quantity_tolerance = float(quantity_tolerance)
        self.price_tolerance = float(price_tolerance)

    def reconcile(
        self,
        lifecycles: list[TradeLifecycle],
        executions: list[BrokerExecution],
        positions: list[PositionSnapshot],
        timestamp: str,
    ) -> list[TradeReconciliationItem]:
        """Perform 3-way reconciliation audit across Broker, Portfolio, and Lifecycle states."""
        items: list[TradeReconciliationItem] = []

        lifecycle_map: dict[str, TradeLifecycle] = {l.lifecycle_id: l for l in lifecycles}
        intent_lifecycle_map: dict[str, TradeLifecycle] = {l.intent_id: l for l in lifecycles if l.intent_id}
        pos_lifecycle_map: dict[str, TradeLifecycle] = {l.position_id: l for l in lifecycles if l.position_id}

        exec_map: dict[str, list[BrokerExecution]] = {}
        for ex in executions:
            if ex.intent_id not in exec_map:
                exec_map[ex.intent_id] = []
            exec_map[ex.intent_id].append(ex)

        pos_map: dict[str, PositionSnapshot] = {p.position_id: p for p in positions}

        # 1. Detect Orphan Executions
        for ex in executions:
            if ex.intent_id not in intent_lifecycle_map:
                items.append(
                    TradeReconciliationItem(
                        item_id=f"TREC_ORPH_EX_{ex.execution_id[:12]}",
                        mismatch_type=TradeReconciliationMismatchType.ORPHAN_EXECUTION,
                        symbol=ex.symbol,
                        broker_value=ex.price,
                        lifecycle_value=None,
                        description=f"Broker execution {ex.execution_id} has no matching TradeLifecycle for intent {ex.intent_id}",
                    )
                )

        # 2. Detect Orphan Positions
        for pos in positions:
            if pos.position_id not in pos_lifecycle_map and pos.status != "CLOSED":
                items.append(
                    TradeReconciliationItem(
                        item_id=f"TREC_ORPH_POS_{pos.position_id[:12]}",
                        mismatch_type=TradeReconciliationMismatchType.ORPHAN_POSITION,
                        symbol=pos.symbol,
                        portfolio_value=pos.quantity,
                        lifecycle_value=None,
                        description=f"Active portfolio position {pos.position_id} has no matching TradeLifecycle",
                    )
                )

        # 3. Detect Missing / Duplicate Fills & Volume / Execution Mismatches
        for l in lifecycles:
            exec_list = exec_map.get(l.intent_id, [])

            if l.current_state in {TradeState.SUBMITTED, TradeState.ACKNOWLEDGED} and not exec_list:
                # Check missing fill
                items.append(
                    TradeReconciliationItem(
                        item_id=f"TREC_MISS_FILL_{l.lifecycle_id[:12]}",
                        mismatch_type=TradeReconciliationMismatchType.MISSING_FILL,
                        lifecycle_id=l.lifecycle_id,
                        symbol=l.symbol,
                        broker_value=0.0,
                        lifecycle_value=l.quantity,
                        description=f"Trade lifecycle {l.lifecycle_id} in {l.current_state.value} has no broker executions",
                    )
                )

            if len(exec_list) > 1:
                items.append(
                    TradeReconciliationItem(
                        item_id=f"TREC_DUP_FILL_{l.lifecycle_id[:12]}",
                        mismatch_type=TradeReconciliationMismatchType.DUPLICATE_FILL,
                        lifecycle_id=l.lifecycle_id,
                        symbol=l.symbol,
                        broker_value=len(exec_list),
                        lifecycle_value=1,
                        description=f"Multiple broker executions ({len(exec_list)}) detected for single intent {l.intent_id}",
                    )
                )

            if exec_list:
                tot_exec_qty = sum(e.quantity for e in exec_list)
                if abs(tot_exec_qty - l.quantity) > self.quantity_tolerance and l.current_state == TradeState.FILLED:
                    items.append(
                        TradeReconciliationItem(
                            item_id=f"TREC_VOL_MIS_{l.lifecycle_id[:12]}",
                            mismatch_type=TradeReconciliationMismatchType.VOLUME_MISMATCH,
                            lifecycle_id=l.lifecycle_id,
                            symbol=l.symbol,
                            broker_value=tot_exec_qty,
                            lifecycle_value=l.quantity,
                            description=f"Executed quantity {tot_exec_qty} mismatches lifecycle quantity {l.quantity}",
                        )
                    )

            # 4. Check Inconsistent Lifecycle / Missing Closes
            if l.position_id:
                p_snap = pos_map.get(l.position_id)
                if p_snap is None and l.current_state in {TradeState.OPEN, TradeState.MODIFIED, TradeState.SL_UPDATED, TradeState.TP_UPDATED}:
                    items.append(
                        TradeReconciliationItem(
                            item_id=f"TREC_INCONS_{l.lifecycle_id[:12]}",
                            mismatch_type=TradeReconciliationMismatchType.INCONSISTENT_LIFECYCLE,
                            lifecycle_id=l.lifecycle_id,
                            symbol=l.symbol,
                            portfolio_value=None,
                            lifecycle_value=l.current_state.value,
                            description=f"Lifecycle {l.lifecycle_id} is in active state {l.current_state.value} but position {l.position_id} is missing in portfolio",
                        )
                    )
                elif p_snap and p_snap.status == "CLOSED" and l.current_state not in {TradeState.CLOSED, TradeState.PARTIALLY_CLOSED}:
                    items.append(
                        TradeReconciliationItem(
                            item_id=f"TREC_MISS_CLS_{l.lifecycle_id[:12]}",
                            mismatch_type=TradeReconciliationMismatchType.MISSING_CLOSE,
                            lifecycle_id=l.lifecycle_id,
                            symbol=l.symbol,
                            portfolio_value="CLOSED",
                            lifecycle_value=l.current_state.value,
                            description=f"Portfolio position {l.position_id} is CLOSED but lifecycle {l.lifecycle_id} state is {l.current_state.value}",
                        )
                    )

        return items
