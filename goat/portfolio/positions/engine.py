"""
Project GOAT v0.8 — Position Engine

Manages open positions, closing positions, partial closes, average price math,
mark-to-market valuations, position sizing verification, and net quantities.
"""

from __future__ import annotations

from typing import Any

from goat.portfolio.core.canonical import compute_closed_position_id, compute_position_id
from goat.portfolio.core.enums import CloseReason, PositionSide, PositionStatus
from goat.portfolio.core.models import ClosedPosition, Position


class PositionEngine:
    """Engine managing position lifecycle state and mark-to-market calculations."""

    def __init__(self, portfolio_id: str):
        self.portfolio_id = str(portfolio_id).strip()
        self._open_positions: dict[str, Position] = {}  # position_id -> Position
        self._closed_positions: list[ClosedPosition] = []

    def open_position(
        self,
        symbol: str,
        side: PositionSide | str,
        quantity: float,
        entry_price: float,
        opened_at: str,
        intent_id: str = "",
        stop_loss: float | None = None,
        take_profit: float | None = None,
        margin_used: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> Position:
        """Open a new position or scale into an existing open position with volume-weighted average entry price."""
        if quantity <= 0.0:
            raise ValueError(f"Quantity must be strictly positive (> 0.0), got {quantity}")
        if entry_price <= 0.0:
            raise ValueError(f"Entry price must be strictly positive (> 0.0), got {entry_price}")

        if isinstance(side, PositionSide):
            side_enum = side
        else:
            side_enum = PositionSide(str(side).upper())
        symbol_upper = str(symbol).strip().upper()
        meta = metadata or {}

        # Search for existing open position with matching symbol and side
        existing_pos = None
        for pos in self._open_positions.values():
            if pos.symbol == symbol_upper and pos.side == side_enum and pos.status != PositionStatus.CLOSED:
                existing_pos = pos
                break

        if existing_pos is not None:
            # Scale into existing position -> compute VWAP
            total_qty = existing_pos.quantity + quantity
            total_initial = existing_pos.initial_quantity + quantity
            vwap = ((existing_pos.entry_price * existing_pos.quantity) + (entry_price * quantity)) / total_qty
            updated_margin = existing_pos.margin_used + margin_used

            pos_id = existing_pos.position_id
            pos_hash = existing_pos.canonical_hash

            # Calculate unrealized pnl at current entry price
            if side_enum == PositionSide.LONG:
                unrealized_pnl = (entry_price - vwap) * total_qty
            else:
                unrealized_pnl = (vwap - entry_price) * total_qty

            updated_position = Position(
                position_id=pos_id,
                portfolio_id=self.portfolio_id,
                intent_id=intent_id or existing_pos.intent_id,
                symbol=symbol_upper,
                side=side_enum,
                quantity=total_qty,
                initial_quantity=total_initial,
                entry_price=vwap,
                current_price=entry_price,
                stop_loss=stop_loss if stop_loss is not None else existing_pos.stop_loss,
                take_profit=take_profit if take_profit is not None else existing_pos.take_profit,
                opened_at=existing_pos.opened_at,
                updated_at=opened_at,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=existing_pos.realized_pnl,
                margin_used=updated_margin,
                status=existing_pos.status,
                metadata={**existing_pos.metadata, **meta},
                canonical_hash=pos_hash,
            )
            self._open_positions[pos_id] = updated_position
            return updated_position

        # Create brand new position
        pos_id, pos_hash = compute_position_id(
            portfolio_id=self.portfolio_id,
            symbol=symbol_upper,
            side=side_enum.value,
            open_price=entry_price,
            open_time=opened_at,
        )

        new_position = Position(
            position_id=pos_id,
            portfolio_id=self.portfolio_id,
            intent_id=intent_id,
            symbol=symbol_upper,
            side=side_enum,
            quantity=quantity,
            initial_quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            opened_at=opened_at,
            updated_at=opened_at,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            margin_used=margin_used,
            status=PositionStatus.OPEN,
            metadata=meta,
            canonical_hash=pos_hash,
        )
        self._open_positions[pos_id] = new_position
        return new_position

    def close_position(
        self,
        position_id: str,
        close_price: float,
        closed_at: str,
        close_reason: CloseReason | str = CloseReason.MANUAL,
        metadata: dict[str, Any] | None = None,
    ) -> ClosedPosition:
        """Fully close an active open position."""
        pos = self._open_positions.get(position_id)
        if pos is None:
            raise KeyError(f"Position ID {position_id} not found in open positions.")
        if close_price <= 0.0:
            raise ValueError(f"Close price must be strictly positive (> 0.0), got {close_price}")

        if isinstance(close_reason, CloseReason):
            reason_enum = close_reason
        else:
            reason_enum = CloseReason(str(close_reason).upper())
        meta = metadata or {}

        # Compute realized PnL
        if pos.side == PositionSide.LONG:
            pnl = (close_price - pos.entry_price) * pos.quantity
        else:
            pnl = (pos.entry_price - close_price) * pos.quantity

        closed_id, closed_hash = compute_closed_position_id(
            position_id=pos.position_id,
            close_price=close_price,
            close_time=closed_at,
            closed_quantity=pos.quantity,
        )

        closed_pos = ClosedPosition(
            closed_position_id=closed_id,
            position_id=pos.position_id,
            portfolio_id=self.portfolio_id,
            symbol=pos.symbol,
            side=pos.side,
            quantity=pos.quantity,
            entry_price=pos.entry_price,
            exit_price=close_price,
            opened_at=pos.opened_at,
            closed_at=closed_at,
            realized_pnl=pnl,
            close_reason=reason_enum,
            metadata={**pos.metadata, **meta},
            canonical_hash=closed_hash,
        )

        # Remove from open positions
        del self._open_positions[position_id]
        self._closed_positions.append(closed_pos)
        return closed_pos

    def partial_close(
        self,
        position_id: str,
        partial_quantity: float,
        close_price: float,
        closed_at: str,
        close_reason: CloseReason | str = CloseReason.PARTIAL_CLOSE,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Position | None, ClosedPosition]:
        """Partially close an active position by reducing its quantity."""
        pos = self._open_positions.get(position_id)
        if pos is None:
            raise KeyError(f"Position ID {position_id} not found in open positions.")
        if partial_quantity <= 0.0:
            raise ValueError(f"Partial quantity must be > 0.0, got {partial_quantity}")
        if partial_quantity > pos.quantity + 1e-9:
            raise ValueError(f"Partial quantity {partial_quantity} exceeds position quantity {pos.quantity}")

        if abs(partial_quantity - pos.quantity) < 1e-9:
            # Full close
            closed_pos = self.close_position(position_id, close_price, closed_at, close_reason, metadata)
            return None, closed_pos

        if isinstance(close_reason, CloseReason):
            reason_enum = close_reason
        else:
            reason_enum = CloseReason(str(close_reason).upper())
        meta = metadata or {}

        # Compute partial realized PnL
        if pos.side == PositionSide.LONG:
            partial_pnl = (close_price - pos.entry_price) * partial_quantity
        else:
            partial_pnl = (pos.entry_price - close_price) * partial_quantity

        closed_id, closed_hash = compute_closed_position_id(
            position_id=pos.position_id,
            close_price=close_price,
            close_time=closed_at,
            closed_quantity=partial_quantity,
        )

        closed_pos = ClosedPosition(
            closed_position_id=closed_id,
            position_id=pos.position_id,
            portfolio_id=self.portfolio_id,
            symbol=pos.symbol,
            side=pos.side,
            quantity=partial_quantity,
            entry_price=pos.entry_price,
            exit_price=close_price,
            opened_at=pos.opened_at,
            closed_at=closed_at,
            realized_pnl=partial_pnl,
            close_reason=reason_enum,
            metadata=meta,
            canonical_hash=closed_hash,
        )

        remaining_qty = pos.quantity - partial_quantity
        margin_freed_ratio = remaining_qty / pos.quantity
        updated_margin = pos.margin_used * margin_freed_ratio

        # Update remaining position unrealized PnL
        if pos.side == PositionSide.LONG:
            unrealized = (pos.current_price - pos.entry_price) * remaining_qty
        else:
            unrealized = (pos.entry_price - pos.current_price) * remaining_qty

        updated_pos = Position(
            position_id=pos.position_id,
            portfolio_id=pos.portfolio_id,
            intent_id=pos.intent_id,
            symbol=pos.symbol,
            side=pos.side,
            quantity=remaining_qty,
            initial_quantity=pos.initial_quantity,
            entry_price=pos.entry_price,
            current_price=pos.current_price,
            stop_loss=pos.stop_loss,
            take_profit=pos.take_profit,
            opened_at=pos.opened_at,
            updated_at=closed_at,
            unrealized_pnl=unrealized,
            realized_pnl=pos.realized_pnl + partial_pnl,
            margin_used=updated_margin,
            status=PositionStatus.PARTIALLY_CLOSED,
            metadata={**pos.metadata, **meta},
            canonical_hash=pos.canonical_hash,
        )

        self._open_positions[position_id] = updated_pos
        self._closed_positions.append(closed_pos)
        return updated_pos, closed_pos

    def update_market_prices(self, price_map: dict[str, float], timestamp: str) -> list[Position]:
        """Update market prices for open positions and recalculate unrealized PnL."""
        updated = []
        for pos_id, pos in list(self._open_positions.items()):
            if pos.symbol in price_map:
                new_price = float(price_map[pos.symbol])
                if new_price <= 0.0:
                    continue
                if pos.side == PositionSide.LONG:
                    unrealized = (new_price - pos.entry_price) * pos.quantity
                else:
                    unrealized = (pos.entry_price - new_price) * pos.quantity

                new_pos = Position(
                    position_id=pos.position_id,
                    portfolio_id=pos.portfolio_id,
                    intent_id=pos.intent_id,
                    symbol=pos.symbol,
                    side=pos.side,
                    quantity=pos.quantity,
                    initial_quantity=pos.initial_quantity,
                    entry_price=pos.entry_price,
                    current_price=new_price,
                    stop_loss=pos.stop_loss,
                    take_profit=pos.take_profit,
                    opened_at=pos.opened_at,
                    updated_at=timestamp,
                    unrealized_pnl=unrealized,
                    realized_pnl=pos.realized_pnl,
                    margin_used=pos.margin_used,
                    status=pos.status,
                    metadata=pos.metadata,
                    canonical_hash=pos.canonical_hash,
                )
                self._open_positions[pos_id] = new_pos
                updated.append(new_pos)
        return updated

    def verify_position_sizing(
        self,
        symbol: str,
        quantity: float,
        price: float,
        account_equity: float,
        max_position_size: float = 1000.0,
        max_equity_fraction: float = 0.20,
    ) -> bool:
        """Verify position sizing against absolute and equity-fraction limits."""
        if quantity <= 0.0 or price <= 0.0 or account_equity <= 0.0:
            return False
        if quantity > max_position_size:
            return False
        notional = quantity * price
        if notional > account_equity * max_equity_fraction:
            return False
        return True

    def get_net_quantity(self, symbol: str) -> float:
        """Calculate net open quantity for a given symbol (Long positive, Short negative)."""
        symbol_upper = str(symbol).strip().upper()
        net = 0.0
        for pos in self._open_positions.values():
            if pos.symbol == symbol_upper:
                if pos.side == PositionSide.LONG:
                    net += pos.quantity
                else:
                    net -= pos.quantity
        return net

    def get_open_position(self, position_id: str) -> Position | None:
        return self._open_positions.get(position_id)

    def get_open_positions(self) -> list[Position]:
        return list(self._open_positions.values())

    def get_closed_positions(self) -> list[ClosedPosition]:
        return list(self._closed_positions)
