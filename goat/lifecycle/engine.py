"""
Project GOAT v0.8 — Trade Lifecycle Engine Master Coordinator

Master coordinator implementing canonical trade lifecycle management.
Integrates TradeTrackingEngine, TradeEventEngine, TradeReconciliationEngine,
SQLiteLifecycleRepository, and LifecycleReportEngine.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from goat.lifecycle.core.canonical import (
    compute_broker_execution_id,
    compute_lifecycle_audit_id,
    compute_lifecycle_summary_id,
    compute_position_snapshot_id,
)
from goat.lifecycle.core.enums import LifecycleAuditEventType, TradeEventType, TradeState
from goat.lifecycle.core.models import (
    BrokerExecution,
    LifecycleAudit,
    LifecycleSummary,
    PositionSnapshot,
    TradeEvent,
    TradeLifecycle,
    TradeReconciliationItem,
)
from goat.lifecycle.events.engine import TradeEventEngine
from goat.lifecycle.persistence.repository import SQLiteLifecycleRepository
from goat.lifecycle.reconciliation.engine import TradeReconciliationEngine
from goat.lifecycle.reporting.reports import LifecycleExecutiveReport, LifecycleReportEngine
from goat.lifecycle.tracking.engine import TradeTrackingEngine


class TradeLifecycleEngine:
    """Master coordinator maintaining canonical trade lifecycles, event streams, and audit logs."""

    def __init__(self, db_path: str | Path | None = None):
        self.tracking_engine = TradeTrackingEngine()
        self.event_engine = TradeEventEngine()
        self.reconciliation_engine = TradeReconciliationEngine()
        self.report_engine = LifecycleReportEngine()

        self.repository = SQLiteLifecycleRepository(db_path) if db_path else None

        self._audit_log: list[LifecycleAudit] = []
        self._broker_executions: dict[str, BrokerExecution] = {}  # execution_id -> BrokerExecution

    def close(self) -> None:
        """Close database connection if active."""
        if self.repository:
            self.repository.close()

    def _record_audit(
        self,
        lifecycle_id: str,
        event_type: LifecycleAuditEventType | str,
        previous_state: TradeState | None,
        new_state: TradeState,
        reason: str,
        timestamp: str,
        execution_ref: str = "",
        broker_ref: str = "",
        portfolio_ref: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> LifecycleAudit:
        evt_enum = (
            LifecycleAuditEventType(str(event_type).upper())
            if not isinstance(event_type, LifecycleAuditEventType)
            else event_type
        )
        audit_id, audit_hash = compute_lifecycle_audit_id(
            lifecycle_id=lifecycle_id,
            event_type=evt_enum.value,
            timestamp=timestamp,
        )

        audit = LifecycleAudit(
            audit_id=audit_id,
            lifecycle_id=lifecycle_id,
            event_type=evt_enum,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
            timestamp=timestamp,
            execution_ref=execution_ref,
            broker_ref=broker_ref,
            portfolio_ref=portfolio_ref,
            metadata=metadata or {},
            canonical_hash=audit_hash,
        )

        self._audit_log.append(audit)
        if self.repository:
            self.repository.save_audit(audit)
        return audit

    def _record_event(
        self,
        lifecycle_id: str,
        event_type: TradeEventType | str,
        timestamp: str,
        details: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> TradeEvent:
        evt = self.event_engine.record_event(lifecycle_id, event_type, timestamp, details, metadata)
        if self.repository:
            self.repository.save_event(evt)
        return evt

    # ------------------------------------------------------------------
    # Lifecycle Lifecycle Management Pipeline
    # ------------------------------------------------------------------

    def create_trade_lifecycle(
        self,
        intent_id: str,
        symbol: str,
        side: str,
        quantity: float,
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> TradeLifecycle:
        """Create a new TradeLifecycle instance in CREATED state."""
        lifecycle = self.tracking_engine.create_lifecycle(
            intent_id=intent_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            created_at=timestamp,
            metadata=metadata,
        )

        if self.repository:
            self.repository.save_lifecycle(lifecycle)

        self._record_event(
            lifecycle_id=lifecycle.lifecycle_id,
            event_type=TradeEventType.ORDER_SUBMITTED,
            timestamp=timestamp,
            details=f"Trade lifecycle created for intent {intent_id}",
        )

        self._record_audit(
            lifecycle_id=lifecycle.lifecycle_id,
            event_type=LifecycleAuditEventType.LIFECYCLE_CREATED,
            previous_state=None,
            new_state=TradeState.CREATED,
            reason="Trade lifecycle created",
            timestamp=timestamp,
            execution_ref=intent_id,
        )

        return lifecycle

    def process_order_submitted(self, lifecycle_id: str, timestamp: str, details: str = "") -> TradeLifecycle:
        """Transition state from CREATED to SUBMITTED."""
        updated, transition = self.tracking_engine.transition_state(
            lifecycle_id, TradeState.SUBMITTED, timestamp, reason=details or "Order submitted to broker"
        )
        if self.repository:
            self.repository.save_lifecycle(updated)
            self.repository.save_transition(transition)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=TradeEventType.ORDER_SUBMITTED,
            timestamp=timestamp,
            details=details or "Order submitted to broker",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
        )
        return updated

    def process_broker_accepted(self, lifecycle_id: str, timestamp: str, details: str = "") -> TradeLifecycle:
        """Transition state from SUBMITTED to ACKNOWLEDGED."""
        updated, transition = self.tracking_engine.transition_state(
            lifecycle_id, TradeState.ACKNOWLEDGED, timestamp, reason=details or "Broker accepted order"
        )
        if self.repository:
            self.repository.save_lifecycle(updated)
            self.repository.save_transition(transition)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=TradeEventType.BROKER_ACCEPTED,
            timestamp=timestamp,
            details=details or "Broker accepted order",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
        )
        return updated

    def process_broker_rejected(self, lifecycle_id: str, timestamp: str, reason: str = "") -> TradeLifecycle:
        """Transition state to REJECTED."""
        updated, transition = self.tracking_engine.transition_state(
            lifecycle_id, TradeState.REJECTED, timestamp, reason=reason or "Broker rejected order"
        )
        if self.repository:
            self.repository.save_lifecycle(updated)
            self.repository.save_transition(transition)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=TradeEventType.BROKER_REJECTED,
            timestamp=timestamp,
            details=reason or "Broker rejected order",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
        )
        return updated

    def process_broker_execution_fill(
        self,
        lifecycle_id: str,
        broker_order_id: str,
        fill_price: float,
        fill_quantity: float,
        timestamp: str,
        position_id: str = "",
        is_partial: bool = False,
    ) -> tuple[TradeLifecycle, BrokerExecution]:
        """Process broker execution fill telemetry and transition state to PARTIALLY_FILLED or FILLED."""
        lifecycle = self.tracking_engine.get_lifecycle(lifecycle_id)
        if lifecycle is None:
            raise KeyError(f"Trade Lifecycle ID {lifecycle_id} not found.")

        target_state = TradeState.PARTIALLY_FILLED if is_partial else TradeState.FILLED
        evt_type = TradeEventType.PARTIAL_FILL if is_partial else TradeEventType.COMPLETE_FILL

        updated_lifecycle, transition = self.tracking_engine.transition_state(
            lifecycle_id, target_state, timestamp, reason=f"Fill {fill_quantity} @ {fill_price}"
        )

        ex_id, ex_hash = compute_broker_execution_id(
            intent_id=lifecycle.intent_id,
            broker_order_id=broker_order_id,
            fill_price=fill_price,
            fill_quantity=fill_quantity,
            timestamp=timestamp,
        )

        execution = BrokerExecution(
            execution_id=ex_id,
            intent_id=lifecycle.intent_id,
            broker_order_id=str(broker_order_id).strip(),
            symbol=lifecycle.symbol,
            side=lifecycle.side,
            quantity=float(fill_quantity),
            price=float(fill_price),
            timestamp=timestamp,
            canonical_hash=ex_hash,
        )

        self._broker_executions[ex_id] = execution
        updated_lifecycle = self.tracking_engine.associate_broker_execution(lifecycle_id, ex_id, timestamp)
        if position_id:
            updated_lifecycle = self.tracking_engine.associate_position(lifecycle_id, position_id, timestamp)

        if self.repository:
            self.repository.save_lifecycle(updated_lifecycle)
            self.repository.save_transition(transition)
            self.repository.save_broker_execution(execution)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=evt_type,
            timestamp=timestamp,
            details=f"Executed fill qty={fill_quantity} @ {fill_price}",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
            execution_ref=ex_id,
            broker_ref=broker_order_id,
            portfolio_ref=position_id,
        )

        return updated_lifecycle, execution

    def process_position_opened(self, lifecycle_id: str, position_id: str, timestamp: str) -> TradeLifecycle:
        """Transition state from FILLED to OPEN and associate portfolio position ID."""
        updated_lifecycle, transition = self.tracking_engine.transition_state(
            lifecycle_id, TradeState.OPEN, timestamp, reason=f"Position {position_id} opened"
        )
        updated_lifecycle = self.tracking_engine.associate_position(lifecycle_id, position_id, timestamp)

        if self.repository:
            self.repository.save_lifecycle(updated_lifecycle)
            self.repository.save_transition(transition)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=TradeEventType.POSITION_OPENED,
            timestamp=timestamp,
            details=f"Position {position_id} opened",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
            portfolio_ref=position_id,
        )

        return updated_lifecycle

    def process_position_modified(
        self,
        lifecycle_id: str,
        mod_type: str,
        timestamp: str,
        details: str = "",
    ) -> TradeLifecycle:
        """Process position modifications (SL, TP, Trailing stop, or General modified)."""
        mod_upper = str(mod_type).strip().upper()
        if mod_upper == "SL":
            target_state = TradeState.SL_UPDATED
            evt = TradeEventType.STOP_LOSS_UPDATED
        elif mod_upper == "TP":
            target_state = TradeState.TP_UPDATED
            evt = TradeEventType.TAKE_PROFIT_UPDATED
        elif mod_upper == "TRAILING":
            target_state = TradeState.TRAILING_UPDATED
            evt = TradeEventType.TRAILING_STOP_UPDATED
        else:
            target_state = TradeState.MODIFIED
            evt = TradeEventType.POSITION_MODIFIED

        updated_lifecycle, transition = self.tracking_engine.transition_state(
            lifecycle_id, target_state, timestamp, reason=details or f"Position modification: {mod_type}"
        )

        if self.repository:
            self.repository.save_lifecycle(updated_lifecycle)
            self.repository.save_transition(transition)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=evt,
            timestamp=timestamp,
            details=details or f"Modified {mod_type}",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
        )

        return updated_lifecycle

    def process_partial_close(self, lifecycle_id: str, closed_qty: float, close_price: float, timestamp: str) -> TradeLifecycle:
        """Process partial closure of trade lifecycle."""
        updated_lifecycle, transition = self.tracking_engine.transition_state(
            lifecycle_id, TradeState.PARTIALLY_CLOSED, timestamp, reason=f"Partially closed {closed_qty} @ {close_price}"
        )

        if self.repository:
            self.repository.save_lifecycle(updated_lifecycle)
            self.repository.save_transition(transition)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=TradeEventType.PARTIAL_CLOSE,
            timestamp=timestamp,
            details=f"Partially closed qty={closed_qty} @ {close_price}",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
        )

        return updated_lifecycle

    def process_complete_close(self, lifecycle_id: str, close_price: float, timestamp: str, close_reason: str = "MANUAL") -> TradeLifecycle:
        """Process final complete closure of trade lifecycle into CLOSED state."""
        updated_lifecycle, transition = self.tracking_engine.transition_state(
            lifecycle_id, TradeState.CLOSED, timestamp, reason=f"Closed @ {close_price} ({close_reason})"
        )

        if self.repository:
            self.repository.save_lifecycle(updated_lifecycle)
            self.repository.save_transition(transition)

        evt_type = TradeEventType.COMPLETE_CLOSE
        if close_reason.upper() == "MANUAL":
            evt_type = TradeEventType.MANUAL_CLOSE
        elif close_reason.upper() in {"AUTOMATIC", "SIGNAL", "STOP_LOSS", "TAKE_PROFIT"}:
            evt_type = TradeEventType.AUTOMATIC_CLOSE

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=evt_type,
            timestamp=timestamp,
            details=f"Closed position @ {close_price} ({close_reason})",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
        )

        return updated_lifecycle

    def process_execution_failure(self, lifecycle_id: str, error_code: str, reason: str, timestamp: str) -> TradeLifecycle:
        """Transition trade lifecycle to FAILED state upon execution error."""
        updated_lifecycle, transition = self.tracking_engine.transition_state(
            lifecycle_id, TradeState.FAILED, timestamp, reason=f"Failure ({error_code}): {reason}"
        )

        if self.repository:
            self.repository.save_lifecycle(updated_lifecycle)
            self.repository.save_transition(transition)

        self._record_event(
            lifecycle_id=lifecycle_id,
            event_type=TradeEventType.EXECUTION_FAILURE,
            timestamp=timestamp,
            details=f"Execution failure [{error_code}]: {reason}",
        )

        self._record_audit(
            lifecycle_id=lifecycle_id,
            event_type=LifecycleAuditEventType.STATE_TRANSITION,
            previous_state=transition.from_state,
            new_state=transition.to_state,
            reason=transition.reason,
            timestamp=timestamp,
        )

        return updated_lifecycle

    # ------------------------------------------------------------------
    # Telemetry Analytics & Reconciliation
    # ------------------------------------------------------------------

    def reconcile_trade_state(
        self,
        positions: list[PositionSnapshot],
        timestamp: str,
    ) -> list[TradeReconciliationItem]:
        """Perform 3-way reconciliation audit across Broker executions, Portfolio positions, and Trade Lifecycles."""
        lifecycles = self.tracking_engine.get_all_lifecycles()
        executions = list(self._broker_executions.values())

        items = self.reconciliation_engine.reconcile(
            lifecycles=lifecycles,
            executions=executions,
            positions=positions,
            timestamp=timestamp,
        )

        if items:
            self._record_audit(
                lifecycle_id="SYSTEM",
                event_type=LifecycleAuditEventType.ANOMALY_DETECTED,
                previous_state=None,
                new_state=TradeState.CREATED,
                reason=f"Reconciliation detected {len(items)} discrepancies",
                timestamp=timestamp,
            )
        else:
            self._record_audit(
                lifecycle_id="SYSTEM",
                event_type=LifecycleAuditEventType.RECONCILIATION_AUDIT,
                previous_state=None,
                new_state=TradeState.CREATED,
                reason="Reconciliation audit passed cleanly",
                timestamp=timestamp,
            )

        return items

    def get_summary(self, timestamp: str) -> LifecycleSummary:
        """Compute aggregated LifecycleSummary metrics across all trade lifecycles."""
        lifecycles = self.tracking_engine.get_all_lifecycles()
        total = len(lifecycles)
        open_cnt = sum(1 for l in lifecycles if l.current_state in {
            TradeState.OPEN, TradeState.MODIFIED, TradeState.SL_UPDATED, TradeState.TP_UPDATED, TradeState.TRAILING_UPDATED, TradeState.PARTIALLY_CLOSED
        })
        closed_cnt = sum(1 for l in lifecycles if l.current_state == TradeState.CLOSED)
        cancelled_cnt = sum(1 for l in lifecycles if l.current_state == TradeState.CANCELLED)
        rejected_cnt = sum(1 for l in lifecycles if l.current_state == TradeState.REJECTED)
        failed_cnt = sum(1 for l in lifecycles if l.current_state == TradeState.FAILED)

        lsm_id, lsm_hash = compute_lifecycle_summary_id(total, timestamp)
        return LifecycleSummary(
            summary_id=lsm_id,
            total_trades=total,
            open_trades=open_cnt,
            closed_trades=closed_cnt,
            cancelled_trades=cancelled_cnt,
            rejected_trades=rejected_cnt,
            failed_trades=failed_cnt,
            timestamp=timestamp,
            canonical_hash=lsm_hash,
        )

    def generate_executive_report(self, timestamp: str, positions: list[PositionSnapshot] | None = None) -> LifecycleExecutiveReport:
        """Generate complete LifecycleExecutiveReport in Markdown and JSON formats."""
        summary = self.get_summary(timestamp)
        pos_list = positions or []
        recon_items = self.reconcile_trade_state(pos_list, timestamp)
        recent_events = self.event_engine.get_all_events()[-20:]

        report = self.report_engine.build_executive_report(summary, recon_items, recent_events)

        if self.repository:
            self.repository.save_report(f"REP_{summary.summary_id[4:]}", "SYSTEM", "EXECUTIVE", timestamp, report.to_markdown(), report.get_dict())

        return report

    def get_audit_log(self) -> list[LifecycleAudit]:
        return list(self._audit_log)
