"""
Project GOAT v0.9 — Dedicated Unit Tests for Live Validation SQLite Persistence
"""

import pytest

from goat.live_validation.core.canonical import (
    compute_audit_id,
    compute_candidate_id,
    compute_observation_id,
    compute_session_id,
    compute_summary_id,
    compute_validation_decision_id,
)
from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
    ValidationStatus,
)
from goat.live_validation.core.models import (
    LiveValidationCandidate,
    ValidationAudit,
    ValidationDecision,
    ValidationObservation,
    ValidationSession,
    ValidationSummary,
)
from goat.live_validation.persistence.sqlite import LiveValidationPersistenceContext


@pytest.fixture
def persistence_ctx():
    ctx = LiveValidationPersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.mark.parametrize("idx", range(1, 15))
def test_candidate_repository_roundtrip(persistence_ctx: LiveValidationPersistenceContext, idx: int):
    hyp_id = f"HYP_{idx:016X}"
    ste_id = f"STE_{idx:016X}"
    exp_id = f"EXP_{idx:016X}"

    lvc_id, canonical_hash = compute_candidate_id(
        hypothesis_id=hyp_id,
        evaluation_id=ste_id,
        experiment_id=exp_id,
    )

    cand = LiveValidationCandidate(
        candidate_id=lvc_id,
        hypothesis_id=hyp_id,
        evaluation_id=ste_id,
        experiment_id=exp_id,
        evidence_ids=[f"EVR_{idx:016X}"],
        replay_id=f"RPL_{idx:016X}",
        status=ValidationStatus.ELIGIBLE,
        eligibility_score=1.0,
        created_timestamp="2026-08-04T12:00:00Z",
        metadata={"idx": idx},
        canonical_hash=canonical_hash,
    )

    persistence_ctx.candidates.save(cand)
    fetched = persistence_ctx.candidates.get_by_id(lvc_id)

    assert fetched is not None
    assert fetched.candidate_id == cand.candidate_id
    assert fetched.status == ValidationStatus.ELIGIBLE
    assert fetched.canonical_hash == cand.canonical_hash


@pytest.mark.parametrize("idx", range(1, 10))
def test_session_repository_roundtrip(persistence_ctx: LiveValidationPersistenceContext, idx: int):
    lvc_id = f"LVC_{idx:016X}"
    vsn_id, vsn_hash = compute_session_id(candidate_id=lvc_id, start_timestamp="2026-08-04T12:00:00Z")

    session = ValidationSession(
        session_id=vsn_id,
        candidate_id=lvc_id,
        hypothesis_id=f"HYP_{idx:016X}",
        status=ValidationStatus.RUNNING,
        monitoring_status=MonitoringStatus.NORMAL,
        start_timestamp="2026-08-04T12:00:00Z",
        total_observations=idx * 5,
        operator="OPERATOR",
        canonical_hash=vsn_hash,
    )

    persistence_ctx.sessions.save(session)
    fetched = persistence_ctx.sessions.get_by_id(vsn_id)

    assert fetched is not None
    assert fetched.session_id == vsn_id
    assert fetched.total_observations == idx * 5


@pytest.mark.parametrize("idx", range(1, 10))
def test_observation_repository_roundtrip(persistence_ctx: LiveValidationPersistenceContext, idx: int):
    vsn_id = f"VSN_{idx:016X}"
    vob_id, vob_hash = compute_observation_id(
        session_id=vsn_id,
        timestamp="2026-08-04T12:00:00Z",
        live_outcome=0.1 * idx,
        expected_outcome=0.2,
    )

    obs = ValidationObservation(
        observation_id=vob_id,
        session_id=vsn_id,
        timestamp="2026-08-04T12:00:00Z",
        live_outcome=0.1 * idx,
        expected_outcome=0.2,
        slippage=0.001,
        spread=0.0002,
        latency_ms=25.0,
        fill_ratio=1.0,
        canonical_hash=vob_hash,
    )

    persistence_ctx.observations.save(obs)
    fetched = persistence_ctx.observations.get_by_id(vob_id)

    assert fetched is not None
    assert fetched.observation_id == vob_id
    assert fetched.live_outcome == 0.1 * idx


@pytest.mark.parametrize("idx", range(1, 10))
def test_decision_repository_roundtrip(persistence_ctx: LiveValidationPersistenceContext, idx: int):
    vsn_id = f"VSN_{idx:016X}"
    lvc_id = f"LVC_{idx:016X}"
    vdc_id, vdc_hash = compute_validation_decision_id(
        session_id=vsn_id,
        candidate_id=lvc_id,
        decision="PROMOTION_RECOMMENDED",
    )

    dec = ValidationDecision(
        decision_id=vdc_id,
        session_id=vsn_id,
        candidate_id=lvc_id,
        decision=ValidationDecisionOutcome.PROMOTION_RECOMMENDED,
        rationale=f"Rationale statement #{idx}",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=vdc_hash,
    )

    persistence_ctx.decisions.save(dec)
    fetched = persistence_ctx.decisions.get_by_id(vdc_id)

    assert fetched is not None
    assert fetched.decision_id == vdc_id
    assert fetched.decision == ValidationDecisionOutcome.PROMOTION_RECOMMENDED
