"""
Project GOAT v0.8 — Trade Lifecycle Management Engine

Export all public objects via __all__. No namespace leakage.
"""

from goat.lifecycle.core.canonical import (
    compute_broker_execution_id,
    compute_lifecycle_audit_id,
    compute_lifecycle_summary_id,
    compute_lifecycle_transition_id,
    compute_position_snapshot_id,
    compute_trade_event_id,
    compute_trade_lifecycle_id,
    compute_trade_state_id,
)
from goat.lifecycle.core.enums import (
    LifecycleAuditEventType,
    TradeEventType,
    TradeReconciliationMismatchType,
    TradeState,
)
from goat.lifecycle.core.models import (
    BrokerExecution,
    LifecycleAudit,
    LifecycleSummary,
    LifecycleTransition,
    PositionSnapshot,
    TradeEvent,
    TradeLifecycle,
    TradeReconciliationItem,
    TradeStateRecord,
)
from goat.lifecycle.engine import TradeLifecycleEngine
from goat.lifecycle.events.engine import TradeEventEngine
from goat.lifecycle.persistence.repository import (
    BrokerExecutionRepository,
    LifecycleAuditRepository,
    LifecycleReportRepository,
    SQLiteLifecycleRepository,
    TradeEventRepository,
    TradeLifecycleRepository,
)
from goat.lifecycle.reconciliation.engine import TradeReconciliationEngine
from goat.lifecycle.reporting.reports import (
    BaseLifecycleReport,
    ExecutionReport,
    LifecycleAuditReport,
    LifecycleExecutiveReport,
    LifecycleReportEngine,
    TradeEventReport,
    TradeLifecycleReport,
    TradeSummaryReport,
)
from goat.lifecycle.tracking.engine import TradeTrackingEngine

__all__ = [
    # Master Coordinator
    "TradeLifecycleEngine",
    # Subsystem Engines
    "TradeTrackingEngine",
    "TradeEventEngine",
    "TradeReconciliationEngine",
    "LifecycleReportEngine",
    # Enums
    "TradeState",
    "TradeEventType",
    "LifecycleAuditEventType",
    "TradeReconciliationMismatchType",
    # Canonical SHA-256 Generators
    "compute_trade_lifecycle_id",
    "compute_trade_state_id",
    "compute_trade_event_id",
    "compute_broker_execution_id",
    "compute_position_snapshot_id",
    "compute_lifecycle_transition_id",
    "compute_lifecycle_audit_id",
    "compute_lifecycle_summary_id",
    # Domain Models
    "TradeLifecycle",
    "TradeStateRecord",
    "TradeEvent",
    "BrokerExecution",
    "PositionSnapshot",
    "LifecycleTransition",
    "LifecycleAudit",
    "LifecycleSummary",
    "TradeReconciliationItem",
    # SQLite Repositories
    "SQLiteLifecycleRepository",
    "TradeLifecycleRepository",
    "TradeEventRepository",
    "BrokerExecutionRepository",
    "LifecycleAuditRepository",
    "LifecycleReportRepository",
    # Reports
    "BaseLifecycleReport",
    "TradeLifecycleReport",
    "TradeEventReport",
    "ExecutionReport",
    "LifecycleAuditReport",
    "TradeSummaryReport",
    "LifecycleExecutiveReport",
]
