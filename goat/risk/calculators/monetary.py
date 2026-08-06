"""
Project GOAT v0.7 — Monetary Risk Calculator

Computes deterministic monetary risk, reward, and portfolio balance metrics:
- Monetary Stop Loss & Monetary Take Profit
- Risk Amount & Reward Amount
- Expected Return % & Maximum Account Loss
- Remaining Capital & Portfolio Utilization
"""

from __future__ import annotations

from typing import Any


class MonetaryRiskCalculator:
    """Calculator for computing monetary risk and capital metrics deterministically."""

    def compute_monetary_risk(
        self,
        balance: float,
        risk_percent: float,
    ) -> float:
        """Compute exact monetary risk amount in account base currency.

        Args:
            balance: Account balance.
            risk_percent: Maximum risk fraction (e.g. 0.02 = 2%).

        Returns:
            Monetary risk amount.
        """
        return round(float(balance) * float(risk_percent), 2)

    def compute_monetary_reward(
        self,
        monetary_risk: float,
        risk_reward_ratio: float,
    ) -> float:
        """Compute exact expected monetary reward in account base currency.

        Args:
            monetary_risk: Monetary risk amount.
            risk_reward_ratio: Ratio of reward to risk distance.

        Returns:
            Monetary reward amount.
        """
        return round(float(monetary_risk) * float(risk_reward_ratio), 2)

    def compute_expected_return_percent(
        self,
        monetary_reward: float,
        balance: float,
    ) -> float:
        """Compute expected return on account balance percentage.

        Args:
            monetary_reward: Expected monetary reward amount.
            balance: Account balance.

        Returns:
            Percentage return (e.g. 3.0 for 3.0%).
        """
        if balance <= 0:
            return 0.0
        return round((float(monetary_reward) / float(balance)) * 100.0, 4)

    def compute_remaining_capital(
        self,
        balance: float,
        reserved_capital: float,
    ) -> float:
        """Compute remaining unallocated account capital.

        Args:
            balance: Total account balance.
            reserved_capital: Capital reserved across active positions.

        Returns:
            Available unallocated capital.
        """
        return round(max(0.0, float(balance) - float(reserved_capital)), 2)

    def compute_portfolio_utilization(
        self,
        reserved_capital: float,
        balance: float,
    ) -> float:
        """Compute portfolio capital utilization fraction (0.0 to 1.0).

        Args:
            reserved_capital: Capital reserved across active positions.
            balance: Total account balance.

        Returns:
            Utilization fraction.
        """
        if balance <= 0:
            return 0.0
        return round(min(1.0, float(reserved_capital) / float(balance)), 4)
