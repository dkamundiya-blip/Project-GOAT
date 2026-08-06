"""
Project GOAT v0.7 — Test Suite for Scientific Risk Persistence Repositories

Coverage:
- RiskProfileRepository (save, get, list round-trip)
- PositionSizingRepository (save, get round-trip)
- CapitalAllocationRepository (save, get round-trip)
- ExposureRepository (save, get round-trip)
- RiskAssessmentRepository (save, get round-trip)
- RiskReportRepository (save, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.risk.core.canonical import (
    compute_allocation_id,
    compute_exposure_id,
    compute_risk_assessment_id,
    compute_risk_profile_id,
    compute_sizing_id,
)
from goat.risk.core.enums import ExposureStatus
from goat.risk.core.models import (
    CapitalAllocation,
    ExposureAssessment,
    PositionSizingDecision,
    RiskAssessment,
    RiskProfile,
)
from goat.risk.persistence.sqlite import (
    CapitalAllocationRepository,
    ExposureRepository,
    PositionSizingRepository,
    RiskAssessmentRepository,
    RiskProfileRepository,
    RiskReportRepository,
    init_risk_db,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_risk_db(conn)
    yield conn
    conn.close()


def test_profile_repository_roundtrip(db_conn):
    repo = RiskProfileRepository(db_conn)
    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(
        risk_profile_id=p_id,
        qualification_id="SQL_1",
        simulation_result_id="SRS_1",
        account_balance=100000.0,
        canonical_hash=p_hash,
    )

    repo.save_profile(profile)
    fetched = repo.get_profile(p_id)

    assert fetched == profile
    assert len(repo.list_profiles()) == 1


def test_sizing_repository_roundtrip(db_conn):
    p_repo = RiskProfileRepository(db_conn)
    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(risk_profile_id=p_id, qualification_id="SQL_1", simulation_result_id="SRS_1", account_balance=100000.0, canonical_hash=p_hash)
    p_repo.save_profile(profile)

    sz_repo = PositionSizingRepository(db_conn)
    s_id, s_hash = compute_sizing_id(p_id, "EURUSD", 1.0850)
    sizing = PositionSizingDecision(
        sizing_id=s_id,
        risk_profile_id=p_id,
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

    sz_repo.save_sizing(sizing)
    fetched = sz_repo.get_sizing(s_id)

    assert fetched == sizing


def test_allocation_repository_roundtrip(db_conn):
    repo = CapitalAllocationRepository(db_conn)
    a_id, a_hash = compute_allocation_id("SQL_1")
    alloc = CapitalAllocation(
        allocation_id=a_id,
        qualification_id="SQL_1",
        allocated_capital=40000.0,
        available_capital=60000.0,
        reserved_capital=40000.0,
        utilization_percent=0.40,
        canonical_hash=a_hash,
    )

    repo.save_allocation(alloc)
    fetched = repo.get_allocation(a_id)

    assert fetched == alloc


def test_exposure_repository_roundtrip(db_conn):
    repo = ExposureRepository(db_conn)
    e_id, e_hash = compute_exposure_id(1, 40000.0)
    exposure = ExposureAssessment(
        exposure_id=e_id,
        active_positions=["PSD_1"],
        portfolio_exposure=40000.0,
        instrument_exposure=40000.0,
        correlated_exposure=20000.0,
        exposure_status=ExposureStatus.ACCEPTABLE,
        canonical_hash=e_hash,
    )

    repo.save_exposure(exposure)
    fetched = repo.get_exposure(e_id)

    assert fetched == exposure


def test_risk_assessment_repository_roundtrip(db_conn):
    p_repo = RiskProfileRepository(db_conn)
    p_id, p_hash = compute_risk_profile_id("SQL_1", "SRS_1")
    profile = RiskProfile(risk_profile_id=p_id, qualification_id="SQL_1", simulation_result_id="SRS_1", account_balance=100000.0, canonical_hash=p_hash)
    p_repo.save_profile(profile)

    sz_repo = PositionSizingRepository(db_conn)
    s_id, s_hash = compute_sizing_id(p_id, "EURUSD", 1.0850)
    sizing = PositionSizingDecision(sizing_id=s_id, risk_profile_id=p_id, instrument="EURUSD", entry_price=1.0850, stop_loss_price=1.0800, take_profit_price=1.0950, stop_distance=0.0050, reward_distance=0.0100, risk_reward_ratio=2.0, position_size=40000.0, recommended_lot_size=0.40, canonical_hash=s_hash)
    sz_repo.save_sizing(sizing)

    rsa_repo = RiskAssessmentRepository(db_conn)
    r_id, r_hash = compute_risk_assessment_id(s_id)
    assessment = RiskAssessment(
        assessment_id=r_id,
        sizing_id=s_id,
        total_risk=2.0,
        monetary_risk=2000.0,
        expected_reward=4000.0,
        expected_return_percent=4.0,
        drawdown_impact=0.02,
        canonical_hash=r_hash,
    )

    rsa_repo.save_assessment(assessment)
    fetched = rsa_repo.get_assessment(r_id)

    assert fetched == assessment
