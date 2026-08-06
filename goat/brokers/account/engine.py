"""
Project GOAT v0.8 — Broker Account Engine

Manages broker account balance, equity, margin, free margin calculations,
and account state tracking without live API logic.
"""

from __future__ import annotations

from goat.brokers.core.canonical import compute_account_id
from goat.brokers.core.models import BrokerAccount


class BrokerAccountEngine:
    """Engine responsible for representing and tracking broker account state."""

    def __init__(self, broker_id: str, initial_balance: float = 10000.0, currency: str = "USD", leverage: float = 100.0):
        self.broker_id = broker_id.strip()
        self.account_currency = currency.strip().upper()
        self.leverage = float(leverage)
        self._balance = float(initial_balance)
        self._margin = 0.0
        self._unrealized_pnl = 0.0

    def get_account_snapshot(self, account_type: str = "REAL") -> BrokerAccount:
        """Generate current snapshot of BrokerAccount state."""
        equity = max(0.0, round(self._balance + self._unrealized_pnl, 2))
        free_margin = round(max(0.0, equity - self._margin), 2)

        acc_id, canonical_hash = compute_account_id(self.broker_id, account_type, self.account_currency)
        return BrokerAccount(
            account_id=acc_id,
            broker_id=self.broker_id,
            account_type=account_type.strip().upper(),
            account_currency=self.account_currency,
            balance=round(self._balance, 2),
            equity=equity,
            margin=round(self._margin, 2),
            free_margin=free_margin,
            leverage=self.leverage,
            metadata={"unrealized_pnl": self._unrealized_pnl},
            canonical_hash=canonical_hash,
        )

    def update_balance(self, amount: float) -> None:
        """Update account balance (deposit/withdrawal/realized PnL)."""
        self._balance = max(0.0, self._balance + amount)

    def update_unrealized_pnl(self, pnl: float) -> None:
        """Update active positions unrealized PnL."""
        self._unrealized_pnl = float(pnl)

    def update_used_margin(self, margin: float) -> None:
        """Update used margin amount."""
        self._margin = max(0.0, float(margin))
