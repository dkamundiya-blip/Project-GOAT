"""
Project GOAT v0.8 — Exposure Engine

Measures total portfolio exposure, individual instrument exposure, long/short exposures,
net/gross exposures, asset concentration risk, and margin utilization.
"""

from __future__ import annotations

from typing import Any

from goat.portfolio.core.canonical import compute_exposure_summary_id
from goat.portfolio.core.enums import PositionSide
from goat.portfolio.core.models import ExposureSummary, Position


class ExposureEngine:
    """Engine measuring portfolio risk exposures and asset concentration metrics."""

    def __init__(self, portfolio_id: str):
        self.portfolio_id = str(portfolio_id).strip()

    def calculate_exposure(
        self,
        open_positions: list[Position],
        account_equity: float,
        used_margin: float,
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> ExposureSummary:
        """Calculate complete ExposureSummary from active open positions."""
        total_long_exposure = 0.0
        total_short_exposure = 0.0
        instrument_exposures: dict[str, float] = {}  # symbol -> net exposure
        symbol_gross_exposures: dict[str, float] = {}  # symbol -> gross exposure

        for pos in open_positions:
            notional = pos.current_price * pos.quantity
            sym = pos.symbol
            if pos.side == PositionSide.LONG:
                total_long_exposure += notional
                instrument_exposures[sym] = instrument_exposures.get(sym, 0.0) + notional
                symbol_gross_exposures[sym] = symbol_gross_exposures.get(sym, 0.0) + notional
            else:
                total_short_exposure += notional
                instrument_exposures[sym] = instrument_exposures.get(sym, 0.0) - notional
                symbol_gross_exposures[sym] = symbol_gross_exposures.get(sym, 0.0) + notional

        net_exposure = total_long_exposure - total_short_exposure
        gross_exposure = total_long_exposure + total_short_exposure

        # Calculate concentration fractions per symbol relative to total gross exposure
        risk_concentration: dict[str, float] = {}
        max_concentration = 0.0

        if gross_exposure > 0.0:
            for sym, gross_val in symbol_gross_exposures.items():
                conc = gross_val / gross_exposure
                risk_concentration[sym] = round(conc, 6)
                if conc > max_concentration:
                    max_concentration = conc

        # Margin utilization fraction
        if account_equity > 0.0:
            account_utilization = min(1.0, max(0.0, used_margin / account_equity))
        else:
            account_utilization = 1.0 if used_margin > 0.0 else 0.0

        meta = metadata or {}
        exp_id, exp_hash = compute_exposure_summary_id(
            portfolio_id=self.portfolio_id,
            timestamp=timestamp,
        )

        return ExposureSummary(
            exposure_id=exp_id,
            portfolio_id=self.portfolio_id,
            timestamp=timestamp,
            total_long_exposure=total_long_exposure,
            total_short_exposure=total_short_exposure,
            net_exposure=net_exposure,
            gross_exposure=gross_exposure,
            account_utilization=account_utilization,
            instrument_exposures=instrument_exposures,
            risk_concentration=risk_concentration,
            max_instrument_concentration=max_concentration,
            metadata=meta,
            canonical_hash=exp_hash,
        )
