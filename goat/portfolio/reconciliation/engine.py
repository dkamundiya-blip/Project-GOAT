"""
Project GOAT v0.8 — Portfolio Reconciliation Engine

Compares broker state against internal GOAT portfolio state to detect missing positions,
duplicate positions, quantity mismatches, price mismatches, and account balance mismatches.
"""

from __future__ import annotations

from typing import Any

from goat.brokers.core.models import BrokerAccount
from goat.portfolio.core.enums import ReconciliationMismatchType
from goat.portfolio.core.models import AccountSnapshot, Position, ReconciliationItem


class PortfolioReconciliationEngine:
    """Engine comparing external broker telemetry against canonical portfolio state."""

    def __init__(
        self,
        portfolio_id: str,
        price_tolerance: float = 1e-4,
        quantity_tolerance: float = 1e-6,
        balance_tolerance: float = 0.01,
    ):
        self.portfolio_id = str(portfolio_id).strip()
        self.price_tolerance = float(price_tolerance)
        self.quantity_tolerance = float(quantity_tolerance)
        self.balance_tolerance = float(balance_tolerance)

    def reconcile(
        self,
        broker_account: BrokerAccount | None,
        broker_positions: list[dict[str, Any]],
        portfolio_positions: list[Position],
        account_snapshot: AccountSnapshot | None,
        timestamp: str,
    ) -> list[ReconciliationItem]:
        """Perform line-by-line reconciliation audit and return list of discrepancy items."""
        items: list[ReconciliationItem] = []

        # 1. Account Level Reconciliation
        if broker_account is not None and account_snapshot is not None:
            if abs(broker_account.balance - account_snapshot.balance) > self.balance_tolerance:
                items.append(
                    ReconciliationItem(
                        item_id=f"REC_ACC_BAL_{self.portfolio_id[:8]}",
                        mismatch_type=ReconciliationMismatchType.ACCOUNT_MISMATCH,
                        broker_value=broker_account.balance,
                        portfolio_value=account_snapshot.balance,
                        description=f"Account balance mismatch: Broker={broker_account.balance}, Portfolio={account_snapshot.balance}",
                    )
                )
            if abs(broker_account.equity - account_snapshot.equity) > self.balance_tolerance:
                items.append(
                    ReconciliationItem(
                        item_id=f"REC_ACC_EQ_{self.portfolio_id[:8]}",
                        mismatch_type=ReconciliationMismatchType.ACCOUNT_MISMATCH,
                        broker_value=broker_account.equity,
                        portfolio_value=account_snapshot.equity,
                        description=f"Account equity mismatch: Broker={broker_account.equity}, Portfolio={account_snapshot.equity}",
                    )
                )

        # 2. Position Level Reconciliation
        broker_map: dict[str, list[dict[str, Any]]] = {}
        for bp in broker_positions:
            sym = str(bp.get("symbol", "")).strip().upper()
            if sym not in broker_map:
                broker_map[sym] = []
            broker_map[sym].append(bp)

        portfolio_map: dict[str, list[Position]] = {}
        for p in portfolio_positions:
            sym = p.symbol
            if sym not in portfolio_map:
                portfolio_map[sym] = []
            portfolio_map[sym].append(p)

        all_symbols = set(broker_map.keys()).union(set(portfolio_map.keys()))

        for sym in all_symbols:
            b_list = broker_map.get(sym, [])
            p_list = portfolio_map.get(sym, [])

            # Check duplicate positions
            if len(b_list) > 1:
                items.append(
                    ReconciliationItem(
                        item_id=f"REC_DUP_BRK_{sym}",
                        mismatch_type=ReconciliationMismatchType.DUPLICATE_POSITION,
                        symbol=sym,
                        broker_value=len(b_list),
                        portfolio_value=len(p_list),
                        description=f"Duplicate open positions detected on broker for symbol {sym} (count={len(b_list)})",
                    )
                )
            if len(p_list) > 1:
                items.append(
                    ReconciliationItem(
                        item_id=f"REC_DUP_PTF_{sym}",
                        mismatch_type=ReconciliationMismatchType.DUPLICATE_POSITION,
                        symbol=sym,
                        broker_value=len(b_list),
                        portfolio_value=len(p_list),
                        description=f"Duplicate open positions detected in portfolio state for symbol {sym} (count={len(p_list)})",
                    )
                )

            # Check missing positions
            if b_list and not p_list:
                items.append(
                    ReconciliationItem(
                        item_id=f"REC_MISS_PTF_{sym}",
                        mismatch_type=ReconciliationMismatchType.MISSING_POSITION,
                        symbol=sym,
                        broker_value=b_list[0].get("quantity", 0.0),
                        portfolio_value=0.0,
                        description=f"Position present in broker state but missing in portfolio for symbol {sym}",
                    )
                )
                continue

            if p_list and not b_list:
                items.append(
                    ReconciliationItem(
                        item_id=f"REC_MISS_BRK_{sym}",
                        mismatch_type=ReconciliationMismatchType.MISSING_POSITION,
                        symbol=sym,
                        broker_value=0.0,
                        portfolio_value=sum(p.quantity for p in p_list),
                        description=f"Position present in portfolio state but missing in broker state for symbol {sym}",
                    )
                )
                continue

            # Compare Quantity and Price for matched symbol
            b_total_qty = sum(float(bp.get("quantity", 0.0)) for bp in b_list)
            p_total_qty = sum(p.quantity for p in p_list)

            if abs(b_total_qty - p_total_qty) > self.quantity_tolerance:
                items.append(
                    ReconciliationItem(
                        item_id=f"REC_QTY_{sym}",
                        mismatch_type=ReconciliationMismatchType.QUANTITY_MISMATCH,
                        symbol=sym,
                        broker_value=b_total_qty,
                        portfolio_value=p_total_qty,
                        description=f"Quantity mismatch for symbol {sym}: Broker={b_total_qty}, Portfolio={p_total_qty}",
                    )
                )

            # Price comparison
            if b_list and p_list:
                b_price = float(b_list[0].get("entry_price", b_list[0].get("price", 0.0)))
                p_price = p_list[0].entry_price
                if b_price > 0.0 and abs(b_price - p_price) > self.price_tolerance:
                    items.append(
                        ReconciliationItem(
                            item_id=f"REC_PRC_{sym}",
                            mismatch_type=ReconciliationMismatchType.PRICE_MISMATCH,
                            symbol=sym,
                            broker_value=b_price,
                            portfolio_value=p_price,
                            description=f"Entry price mismatch for symbol {sym}: Broker={b_price}, Portfolio={p_price}",
                        )
                    )

        return items
