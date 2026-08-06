"""
Project GOAT v0.8 — Step 7.6 Trade Reconciliation Engine Dedicated Unit Tests
"""

import pytest

from goat.lifecycle.core.enums import TradeReconciliationMismatchType, TradeState
from goat.lifecycle.core.models import BrokerExecution, PositionSnapshot, TradeLifecycle
from goat.lifecycle.reconciliation.engine import TradeReconciliationEngine


def test_reconciliation_clean_state():
    recon_eng = TradeReconciliationEngine()

    l1 = TradeLifecycle(
        lifecycle_id="TRL_1234567890ABCDEF",
        intent_id="EXI_1234567890ABCDEF",
        symbol="EURUSD",
        side="BUY",
        quantity=1.0,
        position_id="POS_1234567890ABCDEF",
        broker_execution_id="BEX_1234567890ABCDEF",
        current_state=TradeState.OPEN,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    )

    ex1 = BrokerExecution(
        execution_id="BEX_1234567890ABCDEF",
        intent_id="EXI_1234567890ABCDEF",
        broker_order_id="BO_1001",
        symbol="EURUSD",
        side="BUY",
        quantity=1.0,
        price=1.0850,
        timestamp="2026-08-01T00:00:00Z",
    )

    pos1 = PositionSnapshot(
        snapshot_id="PSP_1234567890ABCDEF",
        position_id="POS_1234567890ABCDEF",
        symbol="EURUSD",
        side="LONG",
        quantity=1.0,
        entry_price=1.0850,
        current_price=1.0900,
        status="OPEN",
        timestamp="2026-08-01T00:00:00Z",
    )

    items = recon_eng.reconcile([l1], [ex1], [pos1], "2026-08-01T00:00:00Z")
    assert len(items) == 0


def test_reconciliation_orphan_execution():
    recon_eng = TradeReconciliationEngine()
    ex1 = BrokerExecution(
        execution_id="BEX_1234567890ABCDEF",
        intent_id="EXI_ORPHAN_INTENT",
        broker_order_id="BO_9999",
        symbol="GBPUSD",
        side="BUY",
        quantity=1.0,
        price=1.3000,
        timestamp="2026-08-01T00:00:00Z",
    )

    items = recon_eng.reconcile([], [ex1], [], "2026-08-01T00:00:00Z")
    assert len(items) == 1
    assert items[0].mismatch_type == TradeReconciliationMismatchType.ORPHAN_EXECUTION


def test_reconciliation_orphan_position():
    recon_eng = TradeReconciliationEngine()
    pos1 = PositionSnapshot(
        snapshot_id="PSP_1234567890ABCDEF",
        position_id="POS_ORPHAN",
        symbol="USDJPY",
        side="LONG",
        quantity=1.0,
        entry_price=150.0,
        current_price=151.0,
        status="OPEN",
        timestamp="2026-08-01T00:00:00Z",
    )

    items = recon_eng.reconcile([], [], [pos1], "2026-08-01T00:00:00Z")
    assert len(items) == 1
    assert items[0].mismatch_type == TradeReconciliationMismatchType.ORPHAN_POSITION


def test_reconciliation_missing_close():
    recon_eng = TradeReconciliationEngine()

    l1 = TradeLifecycle(
        lifecycle_id="TRL_1234567890ABCDEF",
        intent_id="EXI_1234567890ABCDEF",
        symbol="EURUSD",
        side="BUY",
        quantity=1.0,
        position_id="POS_1234567890ABCDEF",
        current_state=TradeState.OPEN,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
    )

    # Position is CLOSED in portfolio, but lifecycle is still OPEN
    pos1 = PositionSnapshot(
        snapshot_id="PSP_1234567890ABCDEF",
        position_id="POS_1234567890ABCDEF",
        symbol="EURUSD",
        side="LONG",
        quantity=1.0,
        entry_price=1.0850,
        current_price=1.0900,
        status="CLOSED",
        timestamp="2026-08-01T00:00:00Z",
    )

    items = recon_eng.reconcile([l1], [], [pos1], "2026-08-01T00:00:00Z")
    assert len(items) == 1
    assert items[0].mismatch_type == TradeReconciliationMismatchType.MISSING_CLOSE
