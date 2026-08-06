"""
Project GOAT v0.8 — Account Engine

Maintains cash balance, equity, used margin, free margin, margin level (%),
portfolio value, buying power, and account margin utilization metrics.
"""

from __future__ import annotations

from typing import Any

from goat.portfolio.core.canonical import compute_account_snapshot_id
from goat.portfolio.core.models import AccountSnapshot, ClosedPosition, Position


class AccountEngine:
    """Engine tracking portfolio capital, equity mark-to-market, and margin limits."""

    def __init__(
        self,
        portfolio_id: str,
        account_id: str,
        initial_balance: float = 10000.0,
        leverage: float = 1.0,
    ):
        if initial_balance < 0.0:
            raise ValueError(f"Initial balance cannot be negative, got {initial_balance}")
        if leverage < 1.0:
            raise ValueError(f"Leverage must be >= 1.0, got {leverage}")

        self.portfolio_id = str(portfolio_id).strip()
        self.account_id = str(account_id).strip()
        self.balance = float(initial_balance)
        self.leverage = float(leverage)
        self._initial_balance = float(initial_balance)

    def deposit(self, amount: float) -> float:
        """Add cash balance deposit."""
        if amount <= 0.0:
            raise ValueError(f"Deposit amount must be strictly positive (> 0.0), got {amount}")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        """Withdraw cash balance."""
        if amount <= 0.0:
            raise ValueError(f"Withdrawal amount must be strictly positive (> 0.0), got {amount}")
        if amount > self.balance:
            raise ValueError(f"Insufficient cash balance for withdrawal: balance={self.balance}, requested={amount}")
        self.balance -= amount
        return self.balance

    def calculate_account_snapshot(
        self,
        open_positions: list[Position],
        closed_positions: list[ClosedPosition],
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> AccountSnapshot:
        """Calculate complete immutable AccountSnapshot from active open positions and closed trade history."""
        # Sum realized PnLs from closed positions
        cum_realized_pnl = sum(cp.realized_pnl for cp in closed_positions)
        
        # Realized cash balance = initial balance + cumulative realized PnL
        # Note: self.balance stores current cash balance directly
        current_balance = max(0.0, self.balance)
        
        # Open unrealized PnL & Used Margin
        open_unrealized_pnl = sum(p.unrealized_pnl for p in open_positions)
        used_margin = sum(p.margin_used for p in open_positions)

        # Net Equity = Cash Balance + Open Unrealized PnL
        equity = max(0.0, current_balance + open_unrealized_pnl)
        
        # Free Margin = Equity - Used Margin
        free_margin = max(0.0, equity - used_margin)

        # Margin Level (%) = (Equity / Used Margin) * 100
        if used_margin > 0.0:
            margin_level = (equity / used_margin) * 100.0
        else:
            margin_level = 0.0

        # Portfolio Value (Equity)
        portfolio_value = equity

        # Buying Power = Free Margin * Leverage
        buying_power = free_margin * self.leverage

        # Utilization Rate = Used Margin / Equity
        if equity > 0.0:
            utilization_rate = min(1.0, max(0.0, used_margin / equity))
        else:
            utilization_rate = 1.0 if used_margin > 0.0 else 0.0

        meta = metadata or {}
        acc_id, acc_hash = compute_account_snapshot_id(
            portfolio_id=self.portfolio_id,
            account_id=self.account_id,
            timestamp=timestamp,
        )

        return AccountSnapshot(
            account_snapshot_id=acc_id,
            portfolio_id=self.portfolio_id,
            account_id=self.account_id,
            timestamp=timestamp,
            balance=current_balance,
            equity=equity,
            used_margin=used_margin,
            free_margin=free_margin,
            margin_level=margin_level,
            portfolio_value=portfolio_value,
            buying_power=buying_power,
            utilization_rate=utilization_rate,
            metadata=meta,
            canonical_hash=acc_hash,
        )
