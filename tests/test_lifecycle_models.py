"""
Project GOAT v0.8 — Step 7.6 Trade Lifecycle Models Dedicated Unit Tests
"""

import pytest
from pydantic import ValidationError

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


def test_canonical_id_prefixes():
    trl_id, trl_hash = compute_trade_lifecycle_id("EXI_1234567890ABCDEF", "EURUSD", "BUY", "2026-08-01T00:00:00Z")
    assert trl_id.startswith("TRL_")
    assert len(trl_id) == 20
    assert len(trl_hash) == 64

    tst_id, tst_hash = compute_trade_state_id(trl_id, "CREATED", "2026-08-01T00:00:00Z")
    assert tst_id.startswith("TST_")
    assert len(tst_id) == 20

    tev_id, tev_hash = compute_trade_event_id(trl_id, "ORDER_SUBMITTED", "2026-08-01T00:00:00Z")
    assert tev_id.startswith("TEV_")
    assert len(tev_id) == 20

    bex_id, bex_hash = compute_broker_execution_id("EXI_1234567890ABCDEF", "BO_1001", 1.0850, 1.0, "2026-08-01T00:00:00Z")
    assert bex_id.startswith("BEX_")
    assert len(bex_id) == 20

    psp_id, psp_hash = compute_position_snapshot_id("POS_1234567890ABCDEF", "2026-08-01T00:00:00Z")
    assert psp_id.startswith("PSP_")
    assert len(psp_id) == 20

    ltr_id, ltr_hash = compute_lifecycle_transition_id(trl_id, "CREATED", "SUBMITTED", "2026-08-01T00:00:00Z")
    assert ltr_id.startswith("LTR_")
    assert len(ltr_id) == 20

    lad_id, lad_hash = compute_lifecycle_audit_id(trl_id, "LIFECYCLE_CREATED", "2026-08-01T00:00:00Z")
    assert lad_id.startswith("LAD_")
    assert len(lad_id) == 20

    lsm_id, lsm_hash = compute_lifecycle_summary_id(10, "2026-08-01T00:00:00Z")
    assert lsm_id.startswith("LSM_")
    assert len(lsm_id) == 20


def test_trade_lifecycle_model_immutability():
    trl_id, trl_hash = compute_trade_lifecycle_id("EXI_1234567890ABCDEF", "EURUSD", "BUY", "2026-08-01T00:00:00Z")
    lifecycle = TradeLifecycle(
        lifecycle_id=trl_id,
        intent_id="EXI_1234567890ABCDEF",
        symbol="EURUSD",
        side="BUY",
        quantity=1.0,
        current_state=TradeState.CREATED,
        created_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
        canonical_hash=trl_hash,
    )

    with pytest.raises(ValidationError):
        lifecycle.quantity = 2.0


def test_trade_lifecycle_model_extra_forbid():
    trl_id, trl_hash = compute_trade_lifecycle_id("EXI_1234567890ABCDEF", "EURUSD", "BUY", "2026-08-01T00:00:00Z")
    with pytest.raises(ValidationError):
        TradeLifecycle(
            lifecycle_id=trl_id,
            intent_id="EXI_1234567890ABCDEF",
            symbol="EURUSD",
            side="BUY",
            quantity=1.0,
            current_state=TradeState.CREATED,
            created_at="2026-08-01T00:00:00Z",
            updated_at="2026-08-01T00:00:00Z",
            canonical_hash=trl_hash,
            extra_forbidden_field="invalid",
        )


def test_broker_execution_model_validation():
    bex_id, bex_hash = compute_broker_execution_id("EXI_1234567890ABCDEF", "BO_1001", 1.0850, 1.0, "2026-08-01T00:00:00Z")
    bex = BrokerExecution(
        execution_id=bex_id,
        intent_id="EXI_1234567890ABCDEF",
        broker_order_id="BO_1001",
        symbol="EURUSD",
        side="BUY",
        quantity=1.0,
        price=1.0850,
        timestamp="2026-08-01T00:00:00Z",
        canonical_hash=bex_hash,
    )
    assert bex.execution_id == bex_id
    assert bex.price == 1.0850

    with pytest.raises(ValidationError):
        BrokerExecution(
            execution_id="INVALID_PATTERN",
            intent_id="EXI_1234567890ABCDEF",
            broker_order_id="BO_1001",
            symbol="EURUSD",
            side="BUY",
            quantity=1.0,
            price=1.0850,
            timestamp="2026-08-01T00:00:00Z",
        )


@pytest.mark.parametrize("idx", range(150))
def test_model_serialization_matrix(idx):
    trl_id, trl_hash = compute_trade_lifecycle_id(f"EXI_{idx:016X}", "EURUSD", "BUY", f"2026-08-01T00:{idx % 60:02d}:00Z")
    lifecycle = TradeLifecycle(
        lifecycle_id=trl_id,
        intent_id=f"EXI_{idx:016X}",
        symbol="EURUSD",
        side="BUY",
        quantity=1.0 + idx * 0.1,
        current_state=TradeState.CREATED,
        created_at=f"2026-08-01T00:{idx % 60:02d}:00Z",
        updated_at=f"2026-08-01T00:{idx % 60:02d}:00Z",
        canonical_hash=trl_hash,
    )
    json_str = lifecycle.model_dump_json()
    reloaded = TradeLifecycle.model_validate_json(json_str)
    assert reloaded == lifecycle
