"""
Project GOAT v0.8 — Portfolio Engine Master Coordinator

Master coordinator implementing canonical portfolio lifecycle tracking.
Integrates PositionEngine, AccountEngine, ExposureEngine, PerformanceEngine,
PortfolioReconciliationEngine, SQLite persistence, and ReportingEngine.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from goat.brokers.core.models import BrokerAccount
from goat.portfolio.account.engine import AccountEngine
from goat.portfolio.core.canonical import compute_portfolio_audit_id, compute_portfolio_id, compute_portfolio_snapshot_id
from goat.portfolio.core.enums import CloseReason, PortfolioAuditEventType, PortfolioStatus, PositionSide
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
from goat.portfolio.exposure.engine import ExposureEngine
from goat.portfolio.performance.engine import PerformanceEngine
from goat.portfolio.persistence.repository import SQLitePortfolioRepository
from goat.portfolio.positions.engine import PositionEngine
from goat.portfolio.reconciliation.engine import PortfolioReconciliationEngine
from goat.portfolio.reporting.reports import PortfolioReportEngine


class PortfolioEngine:
    """Master coordinator maintaining canonical GOAT portfolio state and reporting."""

    def __init__(
        self,
        portfolio_name: str,
        account_id: str,
        initial_balance: float = 10000.0,
        currency: str = "USD",
        leverage: float = 1.0,
        db_path: str | Path | None = None,
        created_at: str | None = None,
    ):
        ts = created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        ptf_id, ptf_hash = compute_portfolio_id(
            portfolio_name=portfolio_name,
            account_id=account_id,
            created_at=ts,
        )

        self.portfolio = Portfolio(
            portfolio_id=ptf_id,
            account_id=str(account_id).strip(),
            portfolio_name=str(portfolio_name).strip(),
            currency=str(currency).strip().upper(),
            initial_balance=float(initial_balance),
            created_at=ts,
            status=PortfolioStatus.ACTIVE,
            canonical_hash=ptf_hash,
        )

        self.position_engine = PositionEngine(portfolio_id=self.portfolio.portfolio_id)
        self.account_engine = AccountEngine(
            portfolio_id=self.portfolio.portfolio_id,
            account_id=self.portfolio.account_id,
            initial_balance=self.portfolio.initial_balance,
            leverage=leverage,
        )
        self.exposure_engine = ExposureEngine(portfolio_id=self.portfolio.portfolio_id)
        self.performance_engine = PerformanceEngine(
            portfolio_id=self.portfolio.portfolio_id,
            initial_balance=self.portfolio.initial_balance,
        )
        self.reconciliation_engine = PortfolioReconciliationEngine(portfolio_id=self.portfolio.portfolio_id)
        self.reporting_engine = PortfolioReportEngine(portfolio=self.portfolio)

        self.repository = SQLitePortfolioRepository(db_path) if db_path else None
        if self.repository:
            self.repository.save_portfolio(self.portfolio)

        self._audit_log: list[PortfolioAudit] = []
        self._record_audit(PortfolioAuditEventType.PORTFOLIO_CREATED, f"Portfolio {self.portfolio.portfolio_name} created", ts)

    def _record_audit(self, event_type: PortfolioAuditEventType | str, details: str, timestamp: str, metadata: dict[str, Any] | None = None) -> PortfolioAudit:
        if isinstance(event_type, PortfolioAuditEventType):
            evt_enum = event_type
        else:
            evt_enum = PortfolioAuditEventType(str(event_type).upper())
        audit_id, audit_hash = compute_portfolio_audit_id(
            portfolio_id=self.portfolio.portfolio_id,
            event_type=evt_enum.value,
            timestamp=timestamp,
        )
        audit = PortfolioAudit(
            audit_id=audit_id,
            portfolio_id=self.portfolio.portfolio_id,
            event_type=evt_enum,
            timestamp=timestamp,
            details=details,
            metadata=metadata or {},
            canonical_hash=audit_hash,
        )
        self._audit_log.append(audit)
        if self.repository:
            self.repository.save_audit(audit)
        return audit

    # ------------------------------------------------------------------
    # Execution & Position Management Pipeline
    # ------------------------------------------------------------------

    def process_execution_fill(
        self,
        symbol: str,
        side: PositionSide | str,
        quantity: float,
        fill_price: float,
        filled_at: str,
        intent_id: str = "",
        stop_loss: float | None = None,
        take_profit: float | None = None,
        margin_used: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> Position:
        """Process an execution fill notification and update position state."""
        pos = self.position_engine.open_position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=fill_price,
            opened_at=filled_at,
            intent_id=intent_id,
            stop_loss=stop_loss,
            take_profit=take_profit,
            margin_used=margin_used,
            metadata=metadata,
        )
        if self.repository:
            self.repository.save_position(pos)

        self._record_audit(
            PortfolioAuditEventType.POSITION_OPENED,
            f"Opened/Scaled position {pos.position_id} on {pos.symbol} qty={quantity} @ {fill_price}",
            filled_at,
        )
        return pos

    def process_position_close(
        self,
        position_id: str,
        close_price: float,
        closed_at: str,
        close_reason: CloseReason | str = CloseReason.MANUAL,
        metadata: dict[str, Any] | None = None,
    ) -> ClosedPosition:
        """Process full closure of an active position."""
        closed_pos = self.position_engine.close_position(
            position_id=position_id,
            close_price=close_price,
            closed_at=closed_at,
            close_reason=close_reason,
            metadata=metadata,
        )
        if self.repository:
            self.repository.save_closed_position(closed_pos)
            pos_in_db = self.position_engine.get_open_position(position_id)
            if pos_in_db:
                self.repository.save_position(pos_in_db)

        self._record_audit(
            PortfolioAuditEventType.POSITION_CLOSED,
            f"Closed position {position_id} @ {close_price} realized PnL={closed_pos.realized_pnl}",
            closed_at,
        )
        return closed_pos

    def process_partial_close(
        self,
        position_id: str,
        partial_quantity: float,
        close_price: float,
        closed_at: str,
        close_reason: CloseReason | str = CloseReason.PARTIAL_CLOSE,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Position | None, ClosedPosition]:
        """Process partial closure of an active position."""
        remaining_pos, closed_pos = self.position_engine.partial_close(
            position_id=position_id,
            partial_quantity=partial_quantity,
            close_price=close_price,
            closed_at=closed_at,
            close_reason=close_reason,
            metadata=metadata,
        )
        if self.repository:
            self.repository.save_closed_position(closed_pos)
            if remaining_pos:
                self.repository.save_position(remaining_pos)

        self._record_audit(
            PortfolioAuditEventType.PARTIAL_CLOSE,
            f"Partially closed {partial_quantity} lots of position {position_id} @ {close_price} PnL={closed_pos.realized_pnl}",
            closed_at,
        )
        return remaining_pos, closed_pos

    # ------------------------------------------------------------------
    # Market Data & Telemetry Updates
    # ------------------------------------------------------------------

    def update_market_data(self, price_map: dict[str, float], timestamp: str) -> PortfolioSnapshot:
        """Update market prices, recalculate account, exposure, and performance metrics, and emit PortfolioSnapshot."""
        # Update prices on open positions
        self.position_engine.update_market_prices(price_map, timestamp)

        open_positions = self.position_engine.get_open_positions()
        closed_positions = self.position_engine.get_closed_positions()

        # Update Account
        acc_snapshot = self.account_engine.calculate_account_snapshot(
            open_positions=open_positions,
            closed_positions=closed_positions,
            timestamp=timestamp,
        )

        # Update Exposure
        exp_summary = self.exposure_engine.calculate_exposure(
            open_positions=open_positions,
            account_equity=acc_snapshot.equity,
            used_margin=acc_snapshot.used_margin,
            timestamp=timestamp,
        )

        # Update Performance
        perf_summary = self.performance_engine.calculate_performance(
            open_positions=open_positions,
            closed_positions=closed_positions,
            current_equity=acc_snapshot.equity,
            timestamp=timestamp,
        )

        # Build Portfolio Snapshot
        snap_id, snap_hash = compute_portfolio_snapshot_id(
            portfolio_id=self.portfolio.portfolio_id,
            timestamp=timestamp,
        )

        unrealized = sum(p.unrealized_pnl for p in open_positions)
        realized = sum(cp.realized_pnl for cp in closed_positions)

        snapshot = PortfolioSnapshot(
            snapshot_id=snap_id,
            portfolio_id=self.portfolio.portfolio_id,
            timestamp=timestamp,
            balance=acc_snapshot.balance,
            equity=acc_snapshot.equity,
            used_margin=acc_snapshot.used_margin,
            free_margin=acc_snapshot.free_margin,
            unrealized_pnl=unrealized,
            realized_pnl=realized,
            open_positions_count=len(open_positions),
            closed_positions_count=len(closed_positions),
            net_exposure=exp_summary.net_exposure,
            gross_exposure=exp_summary.gross_exposure,
            metadata={},
            canonical_hash=snap_hash,
        )

        if self.repository:
            for p in open_positions:
                self.repository.save_position(p)
            self.repository.save_account_snapshot(acc_snapshot)
            self.repository.save_exposure(exp_summary)
            self.repository.save_performance(perf_summary)
            self.repository.save_snapshot(snapshot)

        self._record_audit(
            PortfolioAuditEventType.PRICE_UPDATED,
            f"Updated market prices for {len(price_map)} symbols. Equity=${acc_snapshot.equity:,.2f}",
            timestamp,
        )

        return snapshot

    # ------------------------------------------------------------------
    # Reconciliation & Reporting
    # ------------------------------------------------------------------

    def reconcile_broker_state(
        self,
        broker_account: BrokerAccount | None,
        broker_positions: list[dict[str, Any]],
        timestamp: str,
    ) -> list[ReconciliationItem]:
        """Perform broker vs GOAT portfolio state reconciliation audit."""
        open_positions = self.position_engine.get_open_positions()
        closed_positions = self.position_engine.get_closed_positions()
        acc_snapshot = self.account_engine.calculate_account_snapshot(open_positions, closed_positions, timestamp)

        items = self.reconciliation_engine.reconcile(
            broker_account=broker_account,
            broker_positions=broker_positions,
            portfolio_positions=open_positions,
            account_snapshot=acc_snapshot,
            timestamp=timestamp,
        )

        if items:
            self._record_audit(
                PortfolioAuditEventType.ANOMALY_DETECTED,
                f"Reconciliation detected {len(items)} discrepancies",
                timestamp,
            )
        else:
            self._record_audit(
                PortfolioAuditEventType.RECONCILIATION_PERFORMED,
                "Reconciliation audit passed with 0 discrepancies",
                timestamp,
            )

        return items

    def generate_executive_report(
        self,
        timestamp: str,
        broker_account: BrokerAccount | None = None,
        broker_positions: list[dict[str, Any]] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Generate complete portfolio executive report in Markdown and JSON."""
        open_positions = self.position_engine.get_open_positions()
        closed_positions = self.position_engine.get_closed_positions()

        acc = self.account_engine.calculate_account_snapshot(open_positions, closed_positions, timestamp)
        exp = self.exposure_engine.calculate_exposure(open_positions, acc.equity, acc.used_margin, timestamp)
        perf = self.performance_engine.calculate_performance(open_positions, closed_positions, acc.equity, timestamp)

        snap_id, snap_hash = compute_portfolio_snapshot_id(self.portfolio.portfolio_id, timestamp)
        snapshot = PortfolioSnapshot(
            snapshot_id=snap_id,
            portfolio_id=self.portfolio.portfolio_id,
            timestamp=timestamp,
            balance=acc.balance,
            equity=acc.equity,
            used_margin=acc.used_margin,
            free_margin=acc.free_margin,
            unrealized_pnl=sum(p.unrealized_pnl for p in open_positions),
            realized_pnl=sum(cp.realized_pnl for cp in closed_positions),
            open_positions_count=len(open_positions),
            closed_positions_count=len(closed_positions),
            net_exposure=exp.net_exposure,
            gross_exposure=exp.gross_exposure,
            canonical_hash=snap_hash,
        )

        b_positions = broker_positions if broker_positions is not None else [
            {"symbol": p.symbol, "quantity": p.quantity, "entry_price": p.entry_price} for p in open_positions
        ]
        b_acc = broker_account if broker_account is not None else BrokerAccount(
            account_id=self.portfolio.account_id,
            broker_id="BRK_GENERIC",
            balance=acc.balance,
            equity=acc.equity,
            free_margin=acc.free_margin,
        )

        recon_items = self.reconcile_broker_state(b_acc, b_positions, timestamp)
        md, js = self.reporting_engine.build_executive_report(snapshot, exp, perf, acc, recon_items)

        if self.repository:
            self.repository.save_report(f"REP_{snapshot.snapshot_id[4:]}", self.portfolio.portfolio_id, "EXECUTIVE", timestamp, md, js)

        return md, js

    def close(self) -> None:
        if self.repository:
            self.repository.close()

    def get_audit_log(self) -> list[PortfolioAudit]:
        return list(self._audit_log)
