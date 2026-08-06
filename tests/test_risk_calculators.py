"""
Project GOAT v0.7 — Test Suite for MonetaryRiskCalculator & RiskRulesEngine

Coverage:
- Monetary risk, monetary reward, expected return % calculation
- Risk rule evaluation & PositionEligibility states
"""

from goat.risk.calculators.monetary import MonetaryRiskCalculator
from goat.risk.calculators.rules import RiskRulesEngine
from goat.risk.core.canonical import compute_risk_profile_id
from goat.risk.core.enums import PositionEligibility
from goat.risk.core.models import RiskProfile


def test_monetary_risk_calculator():
    calc = MonetaryRiskCalculator()

    risk = calc.compute_monetary_risk(100000.0, 0.02)
    assert risk == 2000.0

    reward = calc.compute_monetary_reward(2000.0, 2.5)
    assert reward == 5000.0

    ret_pct = calc.compute_expected_return_percent(5000.0, 100000.0)
    assert ret_pct == 5.0

    rem = calc.compute_remaining_capital(100000.0, 40000.0)
    assert rem == 60000.0

    util = calc.compute_portfolio_utilization(40000.0, 100000.0)
    assert util == 0.40


def test_risk_rules_engine_eligible():
    engine = RiskRulesEngine()

    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(risk_profile_id=p_id, qualification_id="SQL_1", simulation_result_id="SRS_1", account_balance=100000.0, maximum_portfolio_exposure=0.20, canonical_hash=p_hash)

    elig, explanations = engine.evaluate_position_eligibility(
        risk_profile=profile,
        requested_capital=10000.0,
        current_reserved_capital=0.0,
        risk_reward_ratio=2.0,
        current_portfolio_exposure=0.0,
    )

    assert elig == PositionEligibility.ELIGIBLE
    assert len(explanations) == 1


def test_risk_rules_engine_ineligible_low_rr():
    engine = RiskRulesEngine()

    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(risk_profile_id=p_id, qualification_id="SQL_1", simulation_result_id="SRS_1", account_balance=100000.0, maximum_portfolio_exposure=0.20, canonical_hash=p_hash)

    elig, explanations = engine.evaluate_position_eligibility(
        risk_profile=profile,
        requested_capital=10000.0,
        current_reserved_capital=0.0,
        risk_reward_ratio=1.1,  # below 1.5
        current_portfolio_exposure=0.0,
    )

    assert elig == PositionEligibility.INELIGIBLE_REWARD_RISK_TOO_LOW
    assert "below minimum threshold" in explanations[0]
