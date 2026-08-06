"""
Project GOAT v0.8 — Portfolio Reporting Engine

Generates canonical Markdown and JSON reports for:
- PortfolioReport
- PositionReport
- ExposureReport
- PerformanceReport
- AccountReport
- ReconciliationReport
- PortfolioExecutiveReport
"""

from __future__ import annotations

import json
from typing import Any

from goat.portfolio.core.models import (
    AccountSnapshot,
    ClosedPosition,
    ExposureSummary,
    PerformanceSummary,
    Portfolio,
    PortfolioSnapshot,
    Position,
    ReconciliationItem,
)


class PortfolioReportEngine:
    """Reporting engine producing Markdown and canonical JSON outputs for portfolio analytics."""

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def build_portfolio_report(
        self,
        snapshot: PortfolioSnapshot,
        open_positions: list[Position],
        closed_positions: list[ClosedPosition],
    ) -> tuple[str, dict[str, Any]]:
        """Generate PortfolioReport in Markdown and Canonical JSON formats."""
        canonical_json = {
            "portfolio_id": self.portfolio.portfolio_id,
            "portfolio_name": self.portfolio.portfolio_name,
            "timestamp": snapshot.timestamp,
            "balance": snapshot.balance,
            "equity": snapshot.equity,
            "open_positions_count": snapshot.open_positions_count,
            "closed_positions_count": snapshot.closed_positions_count,
            "net_exposure": snapshot.net_exposure,
            "gross_exposure": snapshot.gross_exposure,
            "canonical_hash": snapshot.canonical_hash,
        }

        markdown = f"""# GOAT Portfolio Report

- **Portfolio ID**: `{self.portfolio.portfolio_id}`
- **Portfolio Name**: {self.portfolio.portfolio_name}
- **Timestamp**: {snapshot.timestamp}
- **Status**: {self.portfolio.status.value if hasattr(self.portfolio.status, 'value') else self.portfolio.status}

## Financial Summary
- **Realized Cash Balance**: `${snapshot.balance:,.2f}`
- **Net Portfolio Equity**: `${snapshot.equity:,.2f}`
- **Unrealized P/L**: `${snapshot.unrealized_pnl:,.2f}`
- **Realized P/L**: `${snapshot.realized_pnl:,.2f}`

## Position Metrics
- **Active Open Positions**: {snapshot.open_positions_count}
- **Closed Positions History**: {snapshot.closed_positions_count}
- **Net Dollar Exposure**: `${snapshot.net_exposure:,.2f}`
- **Gross Dollar Exposure**: `${snapshot.gross_exposure:,.2f}`

---
*Canonical Hash*: `{snapshot.canonical_hash}`
"""
        return markdown, canonical_json

    def build_position_report(
        self, open_positions: list[Position], closed_positions: list[ClosedPosition], timestamp: str
    ) -> tuple[str, dict[str, Any]]:
        """Generate PositionReport detailing active open positions and closed trade history."""
        canonical_json = {
            "portfolio_id": self.portfolio.portfolio_id,
            "timestamp": timestamp,
            "open_positions": [p.model_dump() for p in open_positions],
            "closed_positions_count": len(closed_positions),
        }

        rows = []
        for p in open_positions:
            rows.append(
                f"| `{p.position_id[:12]}` | {p.symbol} | {p.side.value} | {p.quantity:.4f} | `${p.entry_price:,.2f}` | `${p.current_price:,.2f}` | `${p.unrealized_pnl:,.2f}` |"
            )
        pos_table = "\n".join(rows) if rows else "| None | - | - | - | - | - | - |"

        markdown = f"""# GOAT Position Management Report

- **Portfolio ID**: `{self.portfolio.portfolio_id}`
- **Timestamp**: {timestamp}

## Active Open Positions ({len(open_positions)})

| Position ID | Symbol | Side | Quantity | Entry Price | Current Mark | Unrealized P/L |
|---|---|---|---|---|---|---|
{pos_table}

## Historical Closed Positions: {len(closed_positions)} trades
"""
        return markdown, canonical_json

    def build_exposure_report(self, exposure: ExposureSummary) -> tuple[str, dict[str, Any]]:
        """Generate ExposureReport detailing long/short, net/gross, and asset concentration risk."""
        canonical_json = exposure.model_dump()

        conc_rows = []
        for sym, frac in exposure.risk_concentration.items():
            conc_rows.append(f"- **{sym}**: `{frac * 100:.2f}%` of gross exposure")
        conc_text = "\n".join(conc_rows) if conc_rows else "- None"

        markdown = f"""# GOAT Exposure Risk Report

- **Portfolio ID**: `{self.portfolio.portfolio_id}`
- **Timestamp**: {exposure.timestamp}

## Risk Exposure Breakdown
- **Total Long Exposure**: `${exposure.total_long_exposure:,.2f}`
- **Total Short Exposure**: `${exposure.total_short_exposure:,.2f}`
- **Net Dollar Exposure**: `${exposure.net_exposure:,.2f}`
- **Gross Dollar Exposure**: `${exposure.gross_exposure:,.2f}`
- **Account Utilization**: `{exposure.account_utilization * 100:.2f}%`

## Asset Concentration Analysis
{conc_text}
- **Max Instrument Concentration**: `{exposure.max_instrument_concentration * 100:.2f}%`
"""
        return markdown, canonical_json

    def build_performance_report(self, perf: PerformanceSummary) -> tuple[str, dict[str, Any]]:
        """Generate PerformanceReport detailing win rate, drawdown, expectancy, and returns."""
        canonical_json = perf.model_dump()

        markdown = f"""# GOAT Portfolio Performance Report

- **Portfolio ID**: `{self.portfolio.portfolio_id}`
- **Timestamp**: {perf.timestamp}

## Trade Statistics
- **Total Closed Trades**: {perf.total_trades}
- **Winning Trades**: {perf.winning_trades} ({perf.win_rate * 100:.2f}%)
- **Losing Trades**: {perf.losing_trades} ({perf.loss_rate * 100:.2f}%)
- **Average Winner**: `${perf.average_winner:,.2f}`
- **Average Loser**: `${perf.average_loser:,.2f}`
- **Largest Winner**: `${perf.largest_winner:,.2f}`
- **Largest Loser**: `${perf.largest_loser:,.2f}`

## Return & Drawdown Metrics
- **Realized P/L**: `${perf.realized_pnl:,.2f}`
- **Unrealized P/L**: `${perf.unrealized_pnl:,.2f}`
- **Total Net P/L**: `${perf.total_pnl:,.2f}`
- **Profit Factor**: `{perf.profit_factor:.2f}`
- **Statistical Expectancy**: `${perf.expectancy:,.2f}` per trade
- **Running Drawdown**: `${perf.running_drawdown:,.2f}`
- **Maximum Drawdown**: `${perf.max_drawdown:,.2f}`
- **Total Return**: `{perf.portfolio_return * 100:.2f}%`
"""
        return markdown, canonical_json

    def build_account_report(self, acc: AccountSnapshot) -> tuple[str, dict[str, Any]]:
        """Generate AccountReport detailing balance, equity, free margin, and buying power."""
        canonical_json = acc.model_dump()

        markdown = f"""# GOAT Account Telemetry Report

- **Portfolio ID**: `{self.portfolio.portfolio_id}`
- **Account ID**: `{acc.account_id}`
- **Timestamp**: {acc.timestamp}

## Account Balance & Margin
- **Cash Balance**: `${acc.balance:,.2f}`
- **Net Equity**: `${acc.equity:,.2f}`
- **Used Margin**: `${acc.used_margin:,.2f}`
- **Free Available Margin**: `${acc.free_margin:,.2f}`
- **Margin Level**: `{acc.margin_level:.2f}%`
- **Available Buying Power**: `${acc.buying_power:,.2f}`
- **Margin Utilization Rate**: `{acc.utilization_rate * 100:.2f}%`
"""
        return markdown, canonical_json

    def build_reconciliation_report(
        self, items: list[ReconciliationItem], timestamp: str
    ) -> tuple[str, dict[str, Any]]:
        """Generate ReconciliationReport detailing discrepancies between broker and portfolio."""
        is_reconciled = len(items) == 0
        canonical_json = {
            "portfolio_id": self.portfolio.portfolio_id,
            "timestamp": timestamp,
            "is_reconciled": is_reconciled,
            "discrepancies_count": len(items),
            "discrepancies": [item.model_dump() for item in items],
        }

        disc_rows = []
        for it in items:
            disc_rows.append(f"- **[{it.mismatch_type.value}]** ({it.symbol}): {it.description}")
        disc_text = "\n".join(disc_rows) if disc_rows else "- No discrepancies detected. Broker and GOAT portfolio are 100% synchronized."

        markdown = f"""# GOAT Broker Reconciliation Report

- **Portfolio ID**: `{self.portfolio.portfolio_id}`
- **Timestamp**: {timestamp}
- **Status**: {"✓ RECONCILED (SYNCHRONIZED)" if is_reconciled else "⚠️ DISCREPANCIES DETECTED"}

## Discrepancies Summary ({len(items)})
{disc_text}
"""
        return markdown, canonical_json

    def build_executive_report(
        self,
        snapshot: PortfolioSnapshot,
        exposure: ExposureSummary,
        perf: PerformanceSummary,
        acc: AccountSnapshot,
        recon_items: list[ReconciliationItem],
    ) -> tuple[str, dict[str, Any]]:
        """Generate comprehensive PortfolioExecutiveReport combining all subsystem telemetry."""
        canonical_json = {
            "portfolio": self.portfolio.model_dump(),
            "snapshot": snapshot.model_dump(),
            "exposure": exposure.model_dump(),
            "performance": perf.model_dump(),
            "account": acc.model_dump(),
            "reconciliation_status": "RECONCILED" if not recon_items else "DISCREPANCIES",
        }

        markdown = f"""# GOAT Portfolio Executive Report

- **Portfolio**: {self.portfolio.portfolio_name} (`{self.portfolio.portfolio_id}`)
- **Account ID**: `{self.portfolio.account_id}`
- **Timestamp**: {snapshot.timestamp}
- **Reconciliation Audit**: {"✓ RECONCILED" if not recon_items else f"⚠️ {len(recon_items)} DISCREPANCIES"}

---

## Executive Financial Telemetry
- **Equity**: `${acc.equity:,.2f}` | **Balance**: `${acc.balance:,.2f}` | **Free Margin**: `${acc.free_margin:,.2f}`
- **Total Net Return**: `{perf.portfolio_return * 100:.2f}%` | **Total P/L**: `${perf.total_pnl:,.2f}`
- **Gross Exposure**: `${exposure.gross_exposure:,.2f}` | **Net Exposure**: `${exposure.net_exposure:,.2f}`

## Performance Highlights
- **Win Rate**: `{perf.win_rate * 100:.2f}%` | **Profit Factor**: `{perf.profit_factor:.2f}` | **Max Drawdown**: `${perf.max_drawdown:,.2f}`
- **Total Trades**: {perf.total_trades} | **Open Positions**: {snapshot.open_positions_count}
"""
        return markdown, canonical_json
