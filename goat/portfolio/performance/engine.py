"""
Project GOAT v0.8 — Performance Engine

Calculates realized P/L, unrealized P/L, total P/L, win/loss rates, average winner/loser,
largest winner/loser, profit factor, expectancy, peak/running/max drawdown, and portfolio returns.
"""

from __future__ import annotations

from typing import Any

from goat.portfolio.core.canonical import compute_performance_summary_id
from goat.portfolio.core.models import ClosedPosition, PerformanceSummary, Position


class PerformanceEngine:
    """Engine calculating statistical portfolio performance metrics and drawdown history."""

    def __init__(self, portfolio_id: str, initial_balance: float = 10000.0):
        if initial_balance <= 0.0:
            raise ValueError(f"Initial balance must be > 0.0, got {initial_balance}")
        self.portfolio_id = str(portfolio_id).strip()
        self.initial_balance = float(initial_balance)
        self.peak_equity = float(initial_balance)
        self.max_drawdown = 0.0

    def update_peak_and_drawdown(self, current_equity: float) -> tuple[float, float]:
        """Update historical peak equity and compute running / max drawdown."""
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        running_drawdown = max(0.0, self.peak_equity - current_equity)
        if running_drawdown > self.max_drawdown:
            self.max_drawdown = running_drawdown

        return running_drawdown, self.max_drawdown

    def calculate_performance(
        self,
        open_positions: list[Position],
        closed_positions: list[ClosedPosition],
        current_equity: float,
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> PerformanceSummary:
        """Calculate complete PerformanceSummary from closed trades and open positions."""
        running_dd, max_dd = self.update_peak_and_drawdown(current_equity)

        total_trades = len(closed_positions)
        winners = [cp for cp in closed_positions if cp.realized_pnl > 0.0]
        losers = [cp for cp in closed_positions if cp.realized_pnl < 0.0]

        winning_trades_count = len(winners)
        losing_trades_count = len(losers)

        win_rate = winning_trades_count / total_trades if total_trades > 0 else 0.0
        loss_rate = losing_trades_count / total_trades if total_trades > 0 else 0.0

        realized_pnl = sum(cp.realized_pnl for cp in closed_positions)
        unrealized_pnl = sum(p.unrealized_pnl for p in open_positions)
        total_pnl = realized_pnl + unrealized_pnl

        gross_profit = sum(cp.realized_pnl for cp in winners)
        gross_loss = abs(sum(cp.realized_pnl for cp in losers))

        avg_winner = (gross_profit / winning_trades_count) if winning_trades_count > 0 else 0.0
        avg_loser = (-gross_loss / losing_trades_count) if losing_trades_count > 0 else 0.0

        largest_winner = max((cp.realized_pnl for cp in winners), default=0.0)
        largest_loser = min((cp.realized_pnl for cp in losers), default=0.0)

        if gross_loss > 0.0:
            profit_factor = gross_profit / gross_loss
        else:
            profit_factor = gross_profit if gross_profit > 0.0 else 0.0

        expectancy = (win_rate * avg_winner) - (loss_rate * abs(avg_loser))
        portfolio_return = total_pnl / self.initial_balance if self.initial_balance > 0.0 else 0.0

        meta = metadata or {}
        per_id, per_hash = compute_performance_summary_id(
            portfolio_id=self.portfolio_id,
            timestamp=timestamp,
        )

        return PerformanceSummary(
            performance_id=per_id,
            portfolio_id=self.portfolio_id,
            timestamp=timestamp,
            total_trades=total_trades,
            winning_trades=winning_trades_count,
            losing_trades=losing_trades_count,
            win_rate=win_rate,
            loss_rate=loss_rate,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            total_pnl=total_pnl,
            average_winner=avg_winner,
            average_loser=avg_loser,
            largest_winner=largest_winner,
            largest_loser=largest_loser,
            profit_factor=profit_factor,
            expectancy=expectancy,
            running_drawdown=running_dd,
            max_drawdown=max_dd,
            portfolio_return=portfolio_return,
            metadata=meta,
            canonical_hash=per_hash,
        )
