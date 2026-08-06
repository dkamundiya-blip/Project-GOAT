"""
Project GOAT v0.8 — Step 7.5 Portfolio Models Dedicated Unit Tests
"""

import pytest
from pydantic import ValidationError

from goat.portfolio.core.canonical import (
    compute_account_snapshot_id,
    compute_closed_position_id,
    compute_exposure_summary_id,
    compute_performance_summary_id,
    compute_portfolio_audit_id,
    compute_portfolio_id,
    compute_portfolio_snapshot_id,
    compute_position_id,
)
from goat.portfolio.core.enums import (
    CloseReason,
    PortfolioAuditEventType,
    PortfolioStatus,
    PositionSide,
    PositionStatus,
    ReconciliationMismatchType,
)
from goat.portfolio.core.models import (
    AccountSnapshot,
    ClosedPosition,
    ExposureSummary,
    PerformanceSummary,
    Portfolio,
    PortfolioAudit,
    PortfolioSnapshot,
    Position,
    ReconciliationItem,
)


def test_canonical_id_prefixes():
    ptf_id, ptf_hash = compute_portfolio_id("Main Portfolio", "BAC_1234567890ABCDEF", "2026-08-01T00:00:00Z")
    assert ptf_id.startswith("PTF_")
    assert len(ptf_id) == 20
    assert len(ptf_hash) == 64

    pos_id, pos_hash = compute_position_id(ptf_id, "EURUSD", "LONG", 1.0850, "2026-08-01T00:00:00Z")
    assert pos_id.startswith("POS_")
    assert len(pos_id) == 20

    cls_id, cls_hash = compute_closed_position_id(pos_id, 1.0900, "2026-08-01T01:00:00Z", 1.0)
    assert cls_id.startswith("CLS_")
    assert len(cls_id) == 20

    psn_id, psn_hash = compute_portfolio_snapshot_id(ptf_id, "2026-08-01T01:00:00Z")
    assert psn_id.startswith("PSN_")
    assert len(psn_id) == 20

    exp_id, exp_hash = compute_exposure_summary_id(ptf_id, "2026-08-01T01:00:00Z")
    assert exp_id.startswith("EXP_")
    assert len(exp_id) == 20

    per_id, per_hash = compute_performance_summary_id(ptf_id, "2026-08-01T01:00:00Z")
    assert per_id.startswith("PER_")
    assert len(per_id) == 20

    acc_id, acc_hash = compute_account_snapshot_id(ptf_id, "BAC_1234567890ABCDEF", "2026-08-01T01:00:00Z")
    assert acc_id.startswith("ACC_")
    assert len(acc_id) == 20

    pad_id, pad_hash = compute_portfolio_audit_id(ptf_id, "POSITION_OPENED", "2026-08-01T01:00:00Z")
    assert pad_id.startswith("PAD_")
    assert len(pad_id) == 20


def test_portfolio_model_immutability():
    ptf_id, ptf_hash = compute_portfolio_id("Main Portfolio", "BAC_1234567890ABCDEF", "2026-08-01T00:00:00Z")
    ptf = Portfolio(
        portfolio_id=ptf_id,
        account_id="BAC_1234567890ABCDEF",
        portfolio_name="Main Portfolio",
        initial_balance=10000.0,
        created_at="2026-08-01T00:00:00Z",
        canonical_hash=ptf_hash,
    )
    with pytest.raises(ValidationError):
        ptf.initial_balance = 20000.0


def test_portfolio_model_extra_forbid():
    ptf_id, ptf_hash = compute_portfolio_id("Main Portfolio", "BAC_1234567890ABCDEF", "2026-08-01T00:00:00Z")
    with pytest.raises(ValidationError):
        Portfolio(
            portfolio_id=ptf_id,
            account_id="BAC_1234567890ABCDEF",
            portfolio_name="Main Portfolio",
            initial_balance=10000.0,
            created_at="2026-08-01T00:00:00Z",
            canonical_hash=ptf_hash,
            extra_field="forbidden",
        )


def test_position_model_validation():
    ptf_id, _ = compute_portfolio_id("P", "BAC_1234567890ABCDEF", "2026-08-01T00:00:00Z")
    pos_id, pos_hash = compute_position_id(ptf_id, "EURUSD", "LONG", 1.0850, "2026-08-01T00:00:00Z")

    pos = Position(
        position_id=pos_id,
        portfolio_id=ptf_id,
        symbol="EURUSD",
        side=PositionSide.LONG,
        quantity=1.0,
        initial_quantity=1.0,
        entry_price=1.0850,
        current_price=1.0900,
        opened_at="2026-08-01T00:00:00Z",
        updated_at="2026-08-01T00:00:00Z",
        unrealized_pnl=500.0,
        canonical_hash=pos_hash,
    )
    assert pos.position_id == pos_id
    assert pos.status == PositionStatus.OPEN

    # Invalid ID pattern
    with pytest.raises(ValidationError):
        Position(
            position_id="INVALID_ID",
            portfolio_id=ptf_id,
            symbol="EURUSD",
            side=PositionSide.LONG,
            quantity=1.0,
            initial_quantity=1.0,
            entry_price=1.0850,
            current_price=1.0900,
            opened_at="2026-08-01T00:00:00Z",
            updated_at="2026-08-01T00:00:00Z",
        )


def test_closed_position_model():
    ptf_id, _ = compute_portfolio_id("P", "BAC_1234567890ABCDEF", "2026-08-01T00:00:00Z")
    pos_id, _ = compute_position_id(ptf_id, "EURUSD", "LONG", 1.0850, "2026-08-01T00:00:00Z")
    cls_id, cls_hash = compute_closed_position_id(pos_id, 1.0900, "2026-08-01T01:00:00Z", 1.0)

    cls_pos = ClosedPosition(
        closed_position_id=cls_id,
        position_id=pos_id,
        portfolio_id=ptf_id,
        symbol="EURUSD",
        side=PositionSide.LONG,
        quantity=1.0,
        entry_price=1.0850,
        exit_price=1.0900,
        opened_at="2026-08-01T00:00:00Z",
        closed_at="2026-08-01T01:00:00Z",
        realized_pnl=500.0,
        close_reason=CloseReason.TAKE_PROFIT,
        canonical_hash=cls_hash,
    )
    assert cls_pos.closed_position_id == cls_id
    assert cls_pos.close_reason == CloseReason.TAKE_PROFIT


@pytest.mark.parametrize("idx", range(150))
def test_model_serialization_parametrized(idx):
    ptf_id, ptf_hash = compute_portfolio_id(f"Port_{idx}", "BAC_1234567890ABCDEF", f"2026-08-01T00:{idx:02d}:00Z")
    ptf = Portfolio(
        portfolio_id=ptf_id,
        account_id="BAC_1234567890ABCDEF",
        portfolio_name=f"Port_{idx}",
        initial_balance=10000.0 + idx * 100.0,
        created_at=f"2026-08-01T00:{idx:02d}:00Z",
        canonical_hash=ptf_hash,
    )
    dumped = ptf.model_dump_json()
    reloaded = Portfolio.model_validate_json(dumped)
    assert reloaded == ptf
