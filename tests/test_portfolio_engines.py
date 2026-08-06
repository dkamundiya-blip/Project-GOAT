"""
Project GOAT v0.8 — Step 7.5 Subsystem Engines Dedicated Tests
"""

import pytest

from goat.brokers.core.models import BrokerAccount
from goat.portfolio.account.engine import AccountEngine
from goat.portfolio.core.enums import CloseReason, PositionSide, PositionStatus, ReconciliationMismatchType
from goat.portfolio.exposure.engine import ExposureEngine
from goat.portfolio.performance.engine import PerformanceEngine
from goat.portfolio.positions.engine import PositionEngine
from goat.portfolio.reconciliation.engine import PortfolioReconciliationEngine


def test_position_engine_open_and_vwap():
    engine = PositionEngine("PTF_0123456789ABCDEF")
    pos1 = engine.open_position("EURUSD", "LONG", 1.0, 1.0800, "2026-08-01T00:00:00Z")
    assert pos1.quantity == 1.0
    assert pos1.entry_price == 1.0800

    # Scale in with another lot @ 1.1000 -> VWAP = (1.0800*1 + 1.1000*1) / 2 = 1.0900
    pos2 = engine.open_position("EURUSD", "LONG", 1.0, 1.1000, "2026-08-01T01:00:00Z")
    assert pos2.quantity == 2.0
    assert pos2.entry_price == 1.0900
    assert pos2.position_id == pos1.position_id


def test_position_engine_partial_and_full_close():
    engine = PositionEngine("PTF_0123456789ABCDEF")
    pos = engine.open_position("EURUSD", "LONG", 2.0, 1.0800, "2026-08-01T00:00:00Z")

    # Partial close 1.0 lot @ 1.0900 -> PnL = (1.0900 - 1.0800)*1.0 = 0.0100 * 100,000 = 100.0 (using standard unit 1.0 lot = 100 PnL if multiplier=1.0)
    # Note: PnL formula in engine is (exit - entry)*qty = (1.0900 - 1.0800)*1.0 = 0.0100
    rem_pos, closed_lot = engine.partial_close(pos.position_id, 1.0, 1.0900, "2026-08-01T01:00:00Z")
    assert rem_pos is not None
    assert rem_pos.quantity == 1.0
    assert rem_pos.status == PositionStatus.PARTIALLY_CLOSED
    assert closed_lot.quantity == 1.0
    assert pytest.approx(closed_lot.realized_pnl) == 0.01

    # Full close remaining lot
    rem_pos2, final_closed = engine.partial_close(pos.position_id, 1.0, 1.1000, "2026-08-01T02:00:00Z")
    assert rem_pos2 is None
    assert final_closed.quantity == 1.0
    assert pytest.approx(final_closed.realized_pnl) == 0.02
    assert len(engine.get_open_positions()) == 0
    assert len(engine.get_closed_positions()) == 2


def test_account_engine_metrics():
    engine = AccountEngine("PTF_0123456789ABCDEF", "BAC_1234567890ABCDEF", initial_balance=10000.0, leverage=10.0)
    pos_eng = PositionEngine("PTF_0123456789ABCDEF")
    pos = pos_eng.open_position("EURUSD", "LONG", 1.0, 1.0000, "2026-08-01T00:00:00Z", margin_used=500.0)

    # Mark price up by 0.0500 -> Unrealized PnL = 0.05
    pos_eng.update_market_prices({"EURUSD": 1.0500}, "2026-08-01T01:00:00Z")
    open_positions = pos_eng.get_open_positions()

    acc_snap = engine.calculate_account_snapshot(open_positions, [], "2026-08-01T01:00:00Z")
    assert acc_snap.balance == 10000.0
    assert pytest.approx(acc_snap.equity) == 10000.05
    assert acc_snap.used_margin == 500.0
    assert pytest.approx(acc_snap.free_margin) == 9500.05
    assert pytest.approx(acc_snap.buying_power) == 95000.5


def test_exposure_engine():
    exp_eng = ExposureEngine("PTF_0123456789ABCDEF")
    pos_eng = PositionEngine("PTF_0123456789ABCDEF")
    pos_eng.open_position("EURUSD", "LONG", 2.0, 1.1000, "2026-08-01T00:00:00Z")
    pos_eng.open_position("GBPUSD", "SHORT", 1.0, 1.3000, "2026-08-01T00:00:00Z")

    open_positions = pos_eng.get_open_positions()
    exp = exp_eng.calculate_exposure(open_positions, 10000.0, 1000.0, "2026-08-01T00:00:00Z")

    assert pytest.approx(exp.total_long_exposure) == 2.2000
    assert pytest.approx(exp.total_short_exposure) == 1.3000
    assert pytest.approx(exp.net_exposure) == 0.9000
    assert pytest.approx(exp.gross_exposure) == 3.5000
    assert "EURUSD" in exp.risk_concentration
    assert "GBPUSD" in exp.risk_concentration


def test_performance_engine():
    perf_eng = PerformanceEngine("PTF_0123456789ABCDEF", initial_balance=10000.0)
    pos_eng = PositionEngine("PTF_0123456789ABCDEF")
    p1 = pos_eng.open_position("EURUSD", "LONG", 1.0, 1.0000, "2026-08-01T00:00:00Z")
    c1 = pos_eng.close_position(p1.position_id, 1.1000, "2026-08-01T01:00:00Z")

    p2 = pos_eng.open_position("GBPUSD", "LONG", 1.0, 1.5000, "2026-08-01T02:00:00Z")
    c2 = pos_eng.close_position(p2.position_id, 1.4000, "2026-08-01T03:00:00Z")

    perf = perf_eng.calculate_performance([], [c1, c2], 10000.0, "2026-08-01T03:00:00Z")
    assert perf.total_trades == 2
    assert perf.winning_trades == 1
    assert perf.losing_trades == 1
    assert perf.win_rate == 0.5
    assert perf.loss_rate == 0.5


def test_reconciliation_engine():
    recon_eng = PortfolioReconciliationEngine("PTF_0123456789ABCDEF")
    pos_eng = PositionEngine("PTF_0123456789ABCDEF")
    pos_eng.open_position("EURUSD", "LONG", 1.0, 1.0800, "2026-08-01T00:00:00Z")

    broker_acc = BrokerAccount(
        account_id="BAC_1234567890ABCDEF",
        broker_id="BRK_1234567890ABCDEF",
        balance=10000.0,
        equity=10000.0,
        free_margin=10000.0,
    )
    # Broker has GBPUSD position missing in portfolio
    broker_positions = [{"symbol": "GBPUSD", "quantity": 1.0, "entry_price": 1.3000}]

    items = recon_eng.reconcile(broker_acc, broker_positions, pos_eng.get_open_positions(), None, "2026-08-01T00:00:00Z")
    assert len(items) >= 2  # Missing GBPUSD on portfolio, Missing EURUSD on broker
    mtypes = {item.mismatch_type for item in items}
    assert ReconciliationMismatchType.MISSING_POSITION in mtypes
