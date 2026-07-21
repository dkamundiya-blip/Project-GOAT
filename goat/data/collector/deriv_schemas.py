"""
Project GOAT v0.2 — Deriv Symbol & Message Schemas

Provider-specific schema definitions and adapters for Deriv WebSocket responses.
Isolates provider field name variations (current vs legacy) from GOAT's canonical research layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from goat.data.schemas import DataSource, Tick


class DerivSymbolMetadata(BaseModel):
    """Normalized internal representation of a Deriv market instrument.

    Handles both current Deriv API fields (underlying_symbol, pip_size, etc.)
    and legacy fields (symbol, pip, display_name) gracefully.
    """

    symbol: str
    display_name: str
    market: str = "synthetic_index"
    submarket: str = "random_index"
    is_trading_suspended: bool = False
    pip_size: int = 4
    raw_metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_active_symbol_dict(cls, data: dict[str, Any]) -> DerivSymbolMetadata:
        """Parse raw active_symbols dictionary from Deriv API response.

        Supports both current API field names and legacy API field names.
        """
        # Current API field: underlying_symbol; Legacy: symbol
        symbol = str(data.get("underlying_symbol") or data.get("symbol") or "").strip()
        if not symbol:
            raise ValueError("Invalid active_symbol response: missing symbol/underlying_symbol")

        # Current API field: underlying_symbol_name; Legacy: display_name
        display_name = str(
            data.get("underlying_symbol_name") or data.get("display_name") or symbol
        ).strip()

        # Market & Submarket
        market = str(data.get("market") or data.get("market_name") or "synthetic_index").strip()
        submarket = str(
            data.get("submarket") or data.get("submarket_name") or "random_index"
        ).strip()

        # Trading status
        suspended_flag = data.get("is_trading_suspended")
        is_suspended = bool(suspended_flag == 1 or suspended_flag is True)

        # Current API field: pip_size; Legacy: pip (which might be float e.g. 0.0001 or int 4)
        raw_pip = data.get("pip_size") if "pip_size" in data else data.get("pip")
        pip_size = 4
        if isinstance(raw_pip, int):
            pip_size = raw_pip
        elif isinstance(raw_pip, float) or isinstance(raw_pip, str):
            try:
                dec_str = str(Decimal(str(raw_pip)))
                if "." in dec_str:
                    pip_size = len(dec_str.split(".")[1])
                else:
                    pip_size = int(dec_str)
            except Exception:
                pip_size = 4

        return cls(
            symbol=symbol,
            display_name=display_name,
            market=market,
            submarket=submarket,
            is_trading_suspended=is_suspended,
            pip_size=pip_size,
            raw_metadata=data,
        )


class DerivTickPayload(BaseModel):
    """Raw tick data received from Deriv tick subscription or historical tick query."""

    symbol: str
    quote: Decimal
    epoch: int
    id: str | None = None
    pip_size: int | None = None
    ask: Decimal | None = None
    bid: Decimal | None = None

    @classmethod
    def from_tick_dict(cls, data: dict[str, Any]) -> DerivTickPayload:
        """Parse tick object from WebSocket payload."""
        sym = str(data.get("symbol") or data.get("underlying_symbol") or "").strip()
        if not sym:
            raise ValueError("Deriv tick payload missing symbol")

        quote_val = data.get("quote") if "quote" in data else data.get("price")
        if quote_val is None:
            raise ValueError("Deriv tick payload missing quote/price")

        epoch_val = data.get("epoch")
        if epoch_val is None:
            raise ValueError("Deriv tick payload missing epoch")

        tick_id = str(data["id"]) if "id" in data and data["id"] is not None else None
        pip_size = data.get("pip_size") if isinstance(data.get("pip_size"), int) else None

        ask_val = Decimal(str(data["ask"])) if "ask" in data and data["ask"] is not None else None
        bid_val = Decimal(str(data["bid"])) if "bid" in data and data["bid"] is not None else None

        return cls(
            symbol=sym,
            quote=Decimal(str(quote_val)),
            epoch=int(epoch_val),
            id=tick_id,
            pip_size=pip_size,
            ask=ask_val,
            bid=bid_val,
        )

    def to_goat_tick(self, source: DataSource = DataSource.LIVE) -> Tick:
        """Convert Deriv tick payload into canonical GOAT Tick object."""
        dt = datetime.fromtimestamp(self.epoch, tz=timezone.utc)
        meta: dict[str, Any] = {
            "provider": "deriv",
        }
        if self.pip_size is not None:
            meta["pip_size"] = self.pip_size
        if self.ask is not None:
            meta["ask"] = float(self.ask)
        if self.bid is not None:
            meta["bid"] = float(self.bid)

        return Tick(
            symbol=self.symbol,
            timestamp=dt,
            price=self.quote,
            tick_id=self.id,
            source=source,
            metadata=meta,
        )
