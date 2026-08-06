"""
Project GOAT v0.9 — Dedicated Unit Tests for Controlled Live Validation Engine
"""

import pytest

from goat.live_validation.core.enums import MonitoringStatus, ValidationStatus
from goat.live_validation.eligibility.engine import ValidationEligibilityEngine
from goat.live_validation.validation.engine import ControlledLiveValidationEngine


@pytest.fixture
def val_engine():
    return ControlledLiveValidationEngine()


@pytest.fixture
def eligible_candidate():
    elig_engine = ValidationEligibilityEngine()
    return elig_engine.evaluate_eligibility(
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        statistical_decision="SUPPORTED",
        evidence_ids=["EVR_1234567890ABCDEF"],
    )


def test_start_session_success(val_engine: ControlledLiveValidationEngine, eligible_candidate):
    session = val_engine.start_session(candidate=eligible_candidate)

    assert session.session_id.startswith("VSN_")
    assert session.candidate_id == eligible_candidate.candidate_id
    assert session.status == ValidationStatus.RUNNING
    assert session.total_observations == 0
    assert val_engine.get_session(session.session_id) is not None


@pytest.mark.parametrize("obs_count", [1, 5, 10, 50])
def test_record_observation_success(val_engine: ControlledLiveValidationEngine, eligible_candidate, obs_count: int):
    session = val_engine.start_session(candidate=eligible_candidate)

    for i in range(obs_count):
        obs = val_engine.record_observation(
            session_id=session.session_id,
            live_outcome=0.5 + i * 0.01,
            expected_outcome=0.4,
            slippage=0.001,
            spread=0.0002,
            latency_ms=30.0,
        )
        assert obs.observation_id.startswith("VOB_")

    updated_s = val_engine.get_session(session.session_id)
    assert updated_s is not None
    assert updated_s.total_observations == obs_count
    assert len(val_engine.get_observations(session.session_id)) == obs_count


def test_update_session_status(val_engine: ControlledLiveValidationEngine, eligible_candidate):
    session = val_engine.start_session(candidate=eligible_candidate)

    updated = val_engine.update_session_status(
        session_id=session.session_id,
        new_status=ValidationStatus.PAUSED,
        new_monitoring=MonitoringStatus.WATCH,
    )

    assert updated.status == ValidationStatus.PAUSED
    assert updated.monitoring_status == MonitoringStatus.WATCH
