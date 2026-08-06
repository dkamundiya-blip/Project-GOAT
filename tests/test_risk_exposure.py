"""
Project GOAT v0.7 — Test Suite for ExposureAssessmentEngine

Coverage:
- Portfolio and instrument monetary exposure assessment
- Exposure status assignments (ACCEPTABLE, WARNING, VIOLATION_EXCEEDED)
"""

from goat.risk.core.canonical import compute_risk_profile_id, compute_sizing_id
from goat.risk.core.enums import ExposureStatus
from goat.risk.core.models import PositionSizingDecision, RiskProfile
from goat.risk.exposure.engine import ExposureAssessmentEngine


def test_exposure_assessment_engine_acceptable():
    engine = ExposureAssessmentEngine()

    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(risk_profile_id=p_id, qualification_id="SQL_1", simulation_result_id="SRS_1", account_balance=100000.0, maximum_portfolio_exposure=0.20, canonical_hash=p_hash)

    s_id, s_hash = compute_sizing_id(p_id, "EURUSD", 1.0)
    sizing = PositionSizingDecision(
        sizing_id=s_id,
        risk_profile_id=p_id,
        instrument="EURUSD",
        entry_price=1.0,
        stop_loss_price=0.99,
        take_profit_price=1.02,
        stop_distance=0.01,
        reward_distance=0.02,
        risk_reward_ratio=2.0,
        position_size=10000.0,  # $10,000 exposure = 10%
        recommended_lot_size=0.10,
        canonical_hash=s_hash,
    )

    assessment = engine.assess_exposure(profile, [sizing])

    assert assessment.exposure_id.startswith("EXP_")
    assert assessment.portfolio_exposure == 10000.0
    assert assessment.exposure_status == ExposureStatus.ACCEPTABLE


def test_exposure_assessment_engine_violation():
    engine = ExposureAssessmentEngine()

    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(risk_profile_id=p_id, qualification_id="SQL_1", simulation_result_id="SRS_1", account_balance=100000.0, maximum_portfolio_exposure=0.20, canonical_hash=p_hash)

    s_id, s_hash = compute_sizing_id(p_id, "EURUSD", 1.0)
    sizing = PositionSizingDecision(
        sizing_id=s_id,
        risk_profile_id=p_id,
        instrument="EURUSD",
        entry_price=1.0,
        stop_loss_price=0.99,
        take_profit_price=1.02,
        stop_distance=0.01,
        reward_distance=0.02,
        risk_reward_ratio=2.0,
        position_size=30000.0,  # $30,000 exposure = 30% > 20%
        recommended_lot_size=0.30,
        canonical_hash=s_hash,
    )

    assessment = engine.assess_exposure(profile, [sizing])

    assert assessment.exposure_status == ExposureStatus.VIOLATION_EXCEEDED
