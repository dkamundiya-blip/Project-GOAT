"""
Project GOAT v0.7 — Position Sizing Engine

Calculates scientifically justified position sizing and price targets deterministically:
- Fixed percentage risk & fixed monetary risk sizing
- Stop-loss distance & take-profit distance
- Risk-reward ratio calculation
- Minimum lot constraints & broker lot increment rounding
"""

from __future__ import annotations

import math
from typing import Any

from goat.risk.core.canonical import (
    compute_canonical_sha256,
    compute_sizing_id,
)
from goat.risk.core.models import PositionSizingDecision, RiskProfile


class PositionSizingEngine:
    """Engine calculating deterministic position sizing, stop loss, and take profit targets."""

    def calculate_position_size(
        self,
        risk_profile: RiskProfile,
        instrument: str,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        point_value: float = 1.0,
        lot_step: float = 0.01,
        min_lot: float = 0.01,
        units_per_lot: float = 100000.0,
    ) -> PositionSizingDecision:
        """Calculate position sizing, stop loss, take profit, and monetary risk targets deterministically.

        Args:
            risk_profile: Target RiskProfile model.
            instrument: Ticker symbol string.
            entry_price: Target entry price.
            stop_loss_price: Target stop loss price.
            take_profit_price: Target take profit price.
            point_value: Monetary value per point per unit (default 1.0).
            lot_step: Broker lot increment step (default 0.01).
            min_lot: Broker minimum lot size (default 0.01).
            units_per_lot: Standard contract size per lot (default 100000.0).

        Returns:
            PositionSizingDecision model.
        """
        stop_dist = abs(float(entry_price) - float(stop_loss_price))
        reward_dist = abs(float(take_profit_price) - float(entry_price))
        rr_ratio = round(reward_dist / stop_dist, 4) if stop_dist > 0 else 1.0

        # Account-level monetary risk
        monetary_risk = float(risk_profile.account_balance) * float(risk_profile.maximum_risk_percent)

        # Raw position units
        risk_per_unit = stop_dist * point_value
        raw_units = (monetary_risk / risk_per_unit) if risk_per_unit > 0 else 0.0

        # Convert to lots
        raw_lots = raw_units / units_per_lot if units_per_lot > 0 else 0.0

        # Round down to nearest lot step
        if lot_step > 0:
            steps = math.floor(raw_lots / lot_step)
            recommended_lots = round(steps * lot_step, 4)
        else:
            recommended_lots = round(raw_lots, 4)

        if recommended_lots < min_lot and raw_lots > 0:
            recommended_lots = min_lot

        actual_units = recommended_lots * units_per_lot
        actual_monetary_risk = round(actual_units * stop_dist * point_value, 2)
        actual_monetary_reward = round(actual_units * reward_dist * point_value, 2)

        s_id, _ = compute_sizing_id(risk_profile.risk_profile_id, instrument, entry_price)

        # Special Requirement metadata exposure
        metadata = {
            "entry_price": entry_price,
            "stop_loss": stop_loss_price,
            "take_profit": take_profit_price,
            "monetary_risk": actual_monetary_risk,
            "monetary_reward": actual_monetary_reward,
            "recommended_lot_size": recommended_lots,
            "minimum_lot_size": min_lot,
            "risk_percentage": risk_profile.maximum_risk_percent * 100.0,
            "units_per_lot": units_per_lot,
            "point_value": point_value,
        }

        payload = {
            "entry_price": float(entry_price),
            "instrument": str(instrument).strip().upper(),
            "recommended_lot_size": float(recommended_lots),
            "sizing_id": s_id,
            "stop_loss_price": float(stop_loss_price),
            "take_profit_price": float(take_profit_price),
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return PositionSizingDecision(
            sizing_id=s_id,
            risk_profile_id=risk_profile.risk_profile_id,
            instrument=instrument,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            stop_distance=round(stop_dist, 5),
            reward_distance=round(reward_dist, 5),
            risk_reward_ratio=rr_ratio,
            position_size=round(actual_units, 2),
            minimum_lot_size=min_lot,
            recommended_lot_size=recommended_lots,
            metadata=metadata,
            canonical_hash=canonical_hash,
        )
