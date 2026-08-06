"""
Project GOAT v0.7 — Deterministic Risk Rules Engine

Evaluates risk rules deterministically:
- Maximum risk per trade
- Maximum portfolio exposure
- Maximum correlated exposure
- Minimum reward-risk ratio
- Minimum account balance
- Capital reservation & position eligibility
"""

from __future__ import annotations

from typing import Any

from goat.risk.core.enums import PositionEligibility, RiskRuleStatus
from goat.risk.core.models import RiskProfile


class RiskRulesEngine:
    """Engine for evaluating risk rules deterministically."""

    def evaluate_position_eligibility(
        self,
        risk_profile: RiskProfile,
        requested_capital: float,
        current_reserved_capital: float,
        risk_reward_ratio: float,
        current_portfolio_exposure: float,
        min_rr_threshold: float = 1.5,
    ) -> tuple[PositionEligibility, list[str]]:
        """Evaluate position eligibility against all risk rules deterministically.

        Args:
            risk_profile: Target RiskProfile model.
            requested_capital: Capital required for requested position.
            current_reserved_capital: Currently reserved capital amount.
            risk_reward_ratio: Ratio of expected reward to risk.
            current_portfolio_exposure: Current monetary portfolio exposure.
            min_rr_threshold: Minimum required reward-risk ratio (default 1.5).

        Returns:
            Tuple of (PositionEligibility, list[explanation_strings]).
        """
        rejection_reasons: list[str] = []

        # 1. Minimum Account Balance Check
        if risk_profile.account_balance <= 0:
            rejection_reasons.append("Account balance is zero or negative.")

        # 2. Capital Reservation Check
        available_cap = risk_profile.account_balance - current_reserved_capital
        if requested_capital > available_cap:
            rejection_reasons.append(
                f"Requested capital ({requested_capital:.2f}) exceeds available capital ({available_cap:.2f})."
            )

        # 3. Portfolio Exposure Check
        new_exposure_fraction = (current_portfolio_exposure + requested_capital) / risk_profile.account_balance
        if new_exposure_fraction > risk_profile.maximum_portfolio_exposure:
            rejection_reasons.append(
                f"Projected portfolio exposure ({new_exposure_fraction:.2%}) exceeds limit ({risk_profile.maximum_portfolio_exposure:.2%})."
            )

        # 4. Minimum Reward-to-Risk Ratio Check
        if risk_reward_ratio < min_rr_threshold:
            rejection_reasons.append(
                f"Risk-reward ratio ({risk_reward_ratio:.2f}) is below minimum threshold ({min_rr_threshold:.2f})."
            )

        # Assign Eligibility State
        if not rejection_reasons:
            return PositionEligibility.ELIGIBLE, ["All risk rules passed deterministically."]

        if "exceeds available capital" in " ".join(rejection_reasons):
            return PositionEligibility.INELIGIBLE_INSUFFICIENT_CAPITAL, rejection_reasons
        if "exceeds limit" in " ".join(rejection_reasons):
            return PositionEligibility.INELIGIBLE_EXPOSURE_VIOLATION, rejection_reasons
        if "below minimum threshold" in " ".join(rejection_reasons):
            return PositionEligibility.INELIGIBLE_REWARD_RISK_TOO_LOW, rejection_reasons

        return PositionEligibility.INELIGIBLE_EXPOSURE_VIOLATION, rejection_reasons
