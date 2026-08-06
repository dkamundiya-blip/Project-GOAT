"""
Project GOAT v0.7 — Test Suite for CapitalAllocationEngine

Coverage:
- Capital allocation to qualified opportunities
- Capital reservation & unallocated capital tracking
- Over-allocation prevention
"""

from goat.risk.allocation.engine import CapitalAllocationEngine
from goat.risk.core.canonical import compute_risk_profile_id
from goat.risk.core.models import RiskProfile


def test_capital_allocation_engine():
    engine = CapitalAllocationEngine()

    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(
        risk_profile_id=p_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        account_balance=100000.0,
        canonical_hash=p_hash,
    )

    alloc1 = engine.allocate_capital(
        qualification_id="SQL_1",
        requested_capital=40000.0,
        risk_profile=profile,
        current_reserved_capital=0.0,
    )

    assert alloc1.allocation_id.startswith("CAL_")
    assert alloc1.allocated_capital == 40000.0
    assert alloc1.reserved_capital == 40000.0
    assert alloc1.available_capital == 60000.0
    assert alloc1.utilization_percent == 0.40

    # Over-allocation check
    alloc2 = engine.allocate_capital(
        qualification_id="SQL_2",
        requested_capital=80000.0,
        risk_profile=profile,
        current_reserved_capital=40000.0,
    )

    assert alloc2.allocated_capital == 60000.0  # Capped at remaining available
    assert alloc2.reserved_capital == 100000.0
    assert alloc2.available_capital == 0.0
    assert alloc2.utilization_percent == 1.0
