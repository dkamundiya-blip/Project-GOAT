"""
Project GOAT v0.8 — Master TradeLifecycleEngine Dedicated Unit Tests
"""

import pytest

from goat.lifecycle.core.enums import TradeEventType, TradeState
from goat.lifecycle.engine import TradeLifecycleEngine


def test_full_trade_lifecycle_workflow():
    engine = TradeLifecycleEngine()
    ts = "2026-08-01T00:00:00Z"

    # 1. Create Lifecycle
    l = engine.create_trade_lifecycle("EXI_1001", "EURUSD", "BUY", 1.0, ts)
    assert l.current_state == TradeState.CREATED

    # 2. Submit Order
    l = engine.process_order_submitted(l.lifecycle_id, "2026-08-01T00:00:01Z")
    assert l.current_state == TradeState.SUBMITTED

    # 3. Broker Accept
    l = engine.process_broker_accepted(l.lifecycle_id, "2026-08-01T00:00:02Z")
    assert l.current_state == TradeState.ACKNOWLEDGED

    # 4. Fill
    l, bex = engine.process_broker_execution_fill(l.lifecycle_id, "BO_99", 1.0850, 1.0, "2026-08-01T00:00:03Z", position_id="POS_101")
    assert l.current_state == TradeState.FILLED

    # 5. Position Open
    l = engine.process_position_opened(l.lifecycle_id, "POS_101", "2026-08-01T00:00:04Z")
    assert l.current_state == TradeState.OPEN

    # 6. SL Update
    l = engine.process_position_modified(l.lifecycle_id, "SL", "2026-08-01T00:00:05Z", details="SL set to 1.0800")
    assert l.current_state == TradeState.SL_UPDATED

    # 7. Partial Close
    l = engine.process_partial_close(l.lifecycle_id, 0.5, 1.0900, "2026-08-01T00:00:06Z")
    assert l.current_state == TradeState.PARTIALLY_CLOSED

    # 8. Complete Close
    l = engine.process_complete_close(l.lifecycle_id, 1.0950, "2026-08-01T01:00:00Z", close_reason="TAKE_PROFIT")
    assert l.current_state == TradeState.CLOSED
    assert l.closed_at == "2026-08-01T01:00:00Z"

    # Audit check
    audits = engine.get_audit_log()
    assert len(audits) >= 8


def test_trade_lifecycle_failure_path():
    engine = TradeLifecycleEngine()
    l = engine.create_trade_lifecycle("EXI_1002", "GBPUSD", "SELL", 2.0, "2026-08-01T00:00:00Z")
    l = engine.process_order_submitted(l.lifecycle_id, "2026-08-01T00:00:01Z")

    # Execution failure
    l = engine.process_execution_failure(l.lifecycle_id, "ERR_MARGIN", "Insufficient margin", "2026-08-01T00:00:02Z")
    assert l.current_state == TradeState.FAILED
