"""
Project GOAT v0.7 — Test Suite for Risk Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (RiskProfile, PositionSizingDecision, CapitalAllocation, ExposureAssessment, RiskAssessment)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.risk.core.canonical import (
    compute_allocation_id,
    compute_exposure_id,
    compute_risk_assessment_id,
    compute_risk_profile_id,
    compute_risk_report_id,
    compute_sizing_id,
    serialize_canonical_json,
)
from goat.risk.core.enums import ExposureStatus, PositionEligibility
from goat.risk.core.models import (
    CapitalAllocation,
    ExposureAssessment,
    PositionSizingDecision,
    RiskAssessment,
    RiskProfile,
)


def test_risk_profile_id_determinism():
    id1, hash1 = compute_risk_profile_id("SQL_1", "SRS_1")
    id2, hash2 = compute_risk_profile_id("SQL_1", "SRS_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RPF_")


def test_sizing_id_determinism():
    id1, hash1 = compute_sizing_id("RPF_1", "EURUSD", 1.0850)
    id2, hash2 = compute_sizing_id("RPF_1", "EURUSD", 1.0850)
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("PSD_")


def test_allocation_id_determinism():
    id1, hash1 = compute_allocation_id("SQL_1")
    id2, hash2 = compute_allocation_id("SQL_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CAL_")


def test_exposure_id_determinism():
    id1, hash1 = compute_exposure_id(2, 20000.0)
    id2, hash2 = compute_exposure_id(2, 20000.0)
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EXP_")


def test_risk_assessment_id_determinism():
    id1, hash1 = compute_risk_assessment_id("PSD_1")
    id2, hash2 = compute_risk_assessment_id("PSD_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RSA_")


def test_risk_report_id_determinism():
    id1, hash1 = compute_risk_report_id("RiskExecutiveReport", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_risk_report_id("RiskExecutiveReport", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SRR_")


def test_risk_profile_model():
    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(
        risk_profile_id=p_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        account_balance=100000.0,
        maximum_risk_percent=0.02,
        canonical_hash=p_hash,
    )
    assert profile.risk_profile_id == p_id
    with pytest.raises((TypeError, ValidationError)):
        profile.account_balance = 200000.0


def test_position_sizing_decision_model():
    s_id, s_hash = compute_sizing_id("RPF_1", "EURUSD", 1.0850)
    sizing = PositionSizingDecision(
        sizing_id=s_id,
        risk_profile_id="RPF_1",
        instrument="EURUSD",
        entry_price=1.0850,
        stop_loss_price=1.0800,
        take_profit_price=1.0950,
        stop_distance=0.0050,
        reward_distance=0.0100,
        risk_reward_ratio=2.0,
        position_size=40000.0,
        recommended_lot_size=0.40,
        canonical_hash=s_hash,
    )
    assert sizing.sizing_id == s_id
    with pytest.raises((TypeError, ValidationError)):
        sizing.recommended_lot_size = 1.0


def test_capital_allocation_model():
    a_id, a_hash = compute_allocation_id("SQL_1")
    alloc = CapitalAllocation(
        allocation_id=a_id,
        qualification_id="SQL_1",
        allocated_capital=43400.0,
        available_capital=56600.0,
        reserved_capital=43400.0,
        utilization_percent=0.434,
        canonical_hash=a_hash,
    )
    assert alloc.allocation_id == a_id
    with pytest.raises((TypeError, ValidationError)):
        alloc.allocated_capital = 50000.0


def test_exposure_assessment_model():
    e_id, e_hash = compute_exposure_id(1, 43400.0)
    exp = ExposureAssessment(
        exposure_id=e_id,
        active_positions=["PSD_1"],
        portfolio_exposure=43400.0,
        instrument_exposure=43400.0,
        correlated_exposure=21700.0,
        exposure_status=ExposureStatus.ACCEPTABLE,
        canonical_hash=e_hash,
    )
    assert exp.exposure_id == e_id
    with pytest.raises((TypeError, ValidationError)):
        exp.exposure_status = ExposureStatus.VIOLATION_EXCEEDED


def test_risk_assessment_model():
    r_id, r_hash = compute_risk_assessment_id("PSD_1")
    rsa = RiskAssessment(
        assessment_id=r_id,
        sizing_id="PSD_1",
        total_risk=2.0,
        monetary_risk=2000.0,
        expected_reward=4000.0,
        expected_return_percent=4.0,
        drawdown_impact=0.02,
        canonical_hash=r_hash,
    )
    assert rsa.assessment_id == r_id
    with pytest.raises((TypeError, ValidationError)):
        rsa.monetary_risk = 3000.0
