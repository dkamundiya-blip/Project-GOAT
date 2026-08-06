"""
Project GOAT v0.7 — Exposure Assessment Engine

Evaluates portfolio and asset exposure limits deterministically:
- Portfolio exposure & instrument exposure
- Correlated asset exposure
- Exposure status assignment (ACCEPTABLE, WARNING, VIOLATION_EXCEEDED)
"""

from __future__ import annotations

from typing import Any

from goat.risk.core.canonical import (
    compute_canonical_sha256,
    compute_exposure_id,
)
from goat.risk.core.enums import ExposureStatus
from goat.risk.core.models import ExposureAssessment, PositionSizingDecision, RiskProfile


class ExposureAssessmentEngine:
    """Engine assessing portfolio and instrument-level exposure risk deterministically."""

    def assess_exposure(
        self,
        risk_profile: RiskProfile,
        active_sizings: list[PositionSizingDecision],
        new_sizing: PositionSizingDecision | None = None,
    ) -> ExposureAssessment:
        """Assess overall portfolio and asset exposure deterministically.

        Args:
            risk_profile: Target RiskProfile model.
            active_sizings: List of currently active PositionSizingDecision models.
            new_sizing: Optional new PositionSizingDecision model to evaluate.

        Returns:
            ExposureAssessment model.
        """
        all_sizings = list(active_sizings)
        if new_sizing:
            all_sizings.append(new_sizing)

        active_ids = sorted([s.sizing_id for s in all_sizings])

        # Monetary risk calculation per position
        total_exposure = 0.0
        instrument_map: dict[str, float] = {}

        for s in all_sizings:
            pos_capital = s.position_size * s.entry_price
            total_exposure += pos_capital
            instrument_map[s.instrument] = instrument_map.get(s.instrument, 0.0) + pos_capital

        max_inst_exposure = max(instrument_map.values()) if instrument_map else 0.0
        correlated_exp = total_exposure * 0.50  # Deterministic 50% correlation baseline

        exposure_fraction = total_exposure / risk_profile.account_balance if risk_profile.account_balance > 0 else 0.0

        status: ExposureStatus
        if exposure_fraction > risk_profile.maximum_portfolio_exposure:
            status = ExposureStatus.VIOLATION_EXCEEDED
        elif exposure_fraction >= risk_profile.maximum_portfolio_exposure * 0.80:
            status = ExposureStatus.WARNING
        else:
            status = ExposureStatus.ACCEPTABLE

        e_id, _ = compute_exposure_id(len(active_ids), total_exposure)

        payload = {
            "active_positions_count": len(active_ids),
            "exposure_id": e_id,
            "exposure_status": status.value,
            "portfolio_exposure": float(total_exposure),
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return ExposureAssessment(
            exposure_id=e_id,
            active_positions=active_ids,
            portfolio_exposure=round(total_exposure, 2),
            instrument_exposure=round(max_inst_exposure, 2),
            correlated_exposure=round(correlated_exp, 2),
            exposure_status=status,
            metadata={"exposure_fraction": round(exposure_fraction, 4), "instruments_count": len(instrument_map)},
            canonical_hash=canonical_hash,
        )
