"""
Project GOAT v0.8 — Step 7.6 Public API Dedicated Unit Tests
"""

import pytest

import goat.lifecycle as lifecycle_pkg


def test_public_api_exports():
    expected_exports = [
        "TradeLifecycleEngine",
        "TradeTrackingEngine",
        "TradeEventEngine",
        "TradeReconciliationEngine",
        "LifecycleReportEngine",
        "TradeState",
        "TradeEventType",
        "LifecycleAuditEventType",
        "TradeReconciliationMismatchType",
        "compute_trade_lifecycle_id",
        "compute_trade_state_id",
        "compute_trade_event_id",
        "compute_broker_execution_id",
        "compute_position_snapshot_id",
        "compute_lifecycle_transition_id",
        "compute_lifecycle_audit_id",
        "compute_lifecycle_summary_id",
        "TradeLifecycle",
        "TradeStateRecord",
        "TradeEvent",
        "BrokerExecution",
        "PositionSnapshot",
        "LifecycleTransition",
        "LifecycleAudit",
        "LifecycleSummary",
        "TradeReconciliationItem",
        "SQLiteLifecycleRepository",
        "TradeLifecycleRepository",
        "TradeEventRepository",
        "BrokerExecutionRepository",
        "LifecycleAuditRepository",
        "LifecycleReportRepository",
        "BaseLifecycleReport",
        "TradeLifecycleReport",
        "TradeEventReport",
        "ExecutionReport",
        "LifecycleAuditReport",
        "TradeSummaryReport",
        "LifecycleExecutiveReport",
    ]

    for item in expected_exports:
        assert hasattr(lifecycle_pkg, item)
    assert set(lifecycle_pkg.__all__) == set(expected_exports)
