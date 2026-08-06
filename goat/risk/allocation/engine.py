"""
Project GOAT v0.7 — Capital Allocation Engine

Manages account capital allocation across qualified opportunities deterministically:
- Reserves capital for active opportunities
- Calculates available unallocated capital
- Prevents portfolio over-allocation
- Tracks portfolio capital utilization percentage
"""

from __future__ import annotations

from typing import Any

from goat.risk.core.canonical import (
    compute_allocation_id,
    compute_canonical_sha256,
)
from goat.risk.core.models import CapitalAllocation, RiskProfile


class CapitalAllocationEngine:
    """Engine allocating and tracking capital across concurrent qualified opportunities deterministically."""

    def allocate_capital(
        self,
        qualification_id: str,
        requested_capital: float,
        risk_profile: RiskProfile,
        current_reserved_capital: float,
    ) -> CapitalAllocation:
        """Allocate capital to a qualified opportunity deterministically.

        Args:
            qualification_id: Target ScientificQualification ID.
            requested_capital: Requested monetary capital allocation.
            risk_profile: Target RiskProfile model.
            current_reserved_capital: Currently reserved capital across active positions.

        Returns:
            CapitalAllocation model.
        """
        available = max(0.0, float(risk_profile.account_balance) - float(current_reserved_capital))
        actual_allocated = min(requested_capital, available)

        new_reserved = float(current_reserved_capital) + actual_allocated
        remaining_available = max(0.0, float(risk_profile.account_balance) - new_reserved)
        utilization = round(min(1.0, new_reserved / float(risk_profile.account_balance)), 4) if risk_profile.account_balance > 0 else 0.0

        c_id, _ = compute_allocation_id(qualification_id)

        payload = {
            "allocated_capital": float(actual_allocated),
            "allocation_id": c_id,
            "qualification_id": str(qualification_id).strip(),
            "reserved_capital": float(new_reserved),
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return CapitalAllocation(
            allocation_id=c_id,
            qualification_id=qualification_id,
            allocated_capital=round(actual_allocated, 2),
            available_capital=round(remaining_available, 2),
            reserved_capital=round(new_reserved, 2),
            utilization_percent=utilization,
            metadata={"requested_capital": requested_capital, "account_balance": risk_profile.account_balance},
            canonical_hash=canonical_hash,
        )
