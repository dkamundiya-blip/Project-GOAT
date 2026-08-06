"""
Project GOAT v0.7 — Test Suite for PositionSizingEngine

Coverage:
- Fixed percentage risk calculation
- Stop loss, take profit, risk-reward ratio derivation
- Lot size rounding to lot step and min lot enforcement
- Special required metadata attributes
"""

from goat.risk.core.canonical import compute_risk_profile_id
from goat.risk.core.models import RiskProfile
from goat.risk.sizing.engine import PositionSizingEngine


def test_position_sizing_engine_calculation():
    engine = PositionSizingEngine()

    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(
        risk_profile_id=p_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        account_balance=100000.0,
        maximum_risk_percent=0.02,  # $2000 risk
        canonical_hash=p_hash,
    )

    sizing = engine.calculate_position_size(
        risk_profile=profile,
        instrument="EURUSD",
        entry_price=1.0850,
        stop_loss_price=1.0800,   # stop dist 0.0050
        take_profit_price=1.0950, # reward dist 0.0100 -> R:R 2.0
    )

    assert sizing.sizing_id.startswith("PSD_")
    assert sizing.instrument == "EURUSD"
    assert sizing.stop_distance == 0.0050
    assert sizing.reward_distance == 0.0100
    assert sizing.risk_reward_ratio == 2.0

    # Special required metadata fields check
    meta = sizing.metadata
    assert meta["entry_price"] == 1.0850
    assert meta["stop_loss"] == 1.0800
    assert meta["take_profit"] == 1.0950
    assert meta["monetary_risk"] == 2000.0
    assert meta["monetary_reward"] == 4000.0
    assert meta["recommended_lot_size"] == 4.0
    assert meta["minimum_lot_size"] == 0.01
    assert meta["risk_percentage"] == 2.0
