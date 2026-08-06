"""
Project GOAT v0.9 — Dedicated Unit Tests for Validation Retirement Engine
"""

import pytest

from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
    ValidationStatus,
)
from goat.live_validation.core.models import (
    ValidationObservation,
    ValidationSession,
)
from goat.live_validation.retirement.engine import ValidationRetirementEngine


@pytest.fixture
def ret_engine():
    return ValidationRetirementEngine()


@pytest.fixture
def test_session():
    return ValidationSession(
        session_id="VSN_1234567890ABCDEF",
        candidate_id="LVC_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        status=ValidationStatus.RUNNING,
        monitoring_status=MonitoringStatus.NORMAL,
        start_timestamp="2026-08-04T12:00:00Z",
    )


def test_derive_recommendation_promotion(ret_engine: ValidationRetirementEngine, test_session: ValidationSession):
    # 60 positive observations with normal monitoring -> PROMOTION_RECOMMENDED
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id=test_session.session_id,
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
        )
        for i in range(60)
    ]

    dec = ret_engine.derive_recommendation(session=test_session, observations=observations)

    assert dec.decision_id.startswith("VDC_")
    assert dec.decision == ValidationDecisionOutcome.PROMOTION_RECOMMENDED
    assert ret_engine.get_decision(dec.decision_id) is not None


def test_derive_recommendation_critical_retirement(ret_engine: ValidationRetirementEngine, test_session: ValidationSession):
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id=test_session.session_id,
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
        )
        for i in range(50)
    ]

    dec = ret_engine.derive_recommendation(
        session=test_session,
        observations=observations,
        monitoring_status=MonitoringStatus.CRITICAL,
    )

    assert dec.decision == ValidationDecisionOutcome.RETIREMENT_RECOMMENDED


def test_derive_recommendation_inconclusive_insufficient_samples(ret_engine: ValidationRetirementEngine, test_session: ValidationSession):
    # Only 10 observations (< 30) -> INCONCLUSIVE
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id=test_session.session_id,
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
        )
        for i in range(10)
    ]

    dec = ret_engine.derive_recommendation(session=test_session, observations=observations)

    assert dec.decision == ValidationDecisionOutcome.INCONCLUSIVE
