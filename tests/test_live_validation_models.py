"""
Project GOAT v0.9 — Comprehensive Dedicated Unit Tests for Live Validation Models
"""

import pytest
from pydantic import ValidationError

from goat.live_validation.core.canonical import (
    compute_audit_id,
    compute_candidate_id,
    compute_canonical_sha256,
    compute_observation_id,
    compute_session_id,
    compute_summary_id,
    compute_validation_decision_id,
    serialize_canonical_json,
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


@pytest.mark.parametrize("status", list(ValidationStatus))
def test_live_validation_candidate_model(status: ValidationStatus):
    hyp_id = "HYP_1234567890ABCDEF"
    ste_id = "STE_1234567890ABCDEF"
    exp_id = "EXP_1234567890ABCDEF"

    lvc_id, canonical_hash = compute_candidate_id(
        hypothesis_id=hyp_id,
        evaluation_id=ste_id,
        experiment_id=exp_id,
    )

    candidate = LiveValidationCandidate(
        candidate_id=lvc_id,
        hypothesis_id=hyp_id,
        evaluation_id=ste_id,
        experiment_id=exp_id,
        evidence_ids=["EVR_1234567890ABCDEF"],
        replay_id="RPL_1234567890ABCDEF",
        status=status,
        eligibility_score=1.0,
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    assert candidate.candidate_id == lvc_id
    assert candidate.hypothesis_id == hyp_id
    assert candidate.status == status
    assert candidate.canonical_hash == canonical_hash


@pytest.mark.parametrize("invalid_id", ["INVALID_ID", "LVC_SHORT", "123_LVC"])
def test_candidate_invalid_id_pattern(invalid_id: str):
    with pytest.raises(ValidationError):
        LiveValidationCandidate(
            candidate_id=invalid_id,
            hypothesis_id="HYP_1234567890ABCDEF",
            evaluation_id="STE_1234567890ABCDEF",
            experiment_id="EXP_1234567890ABCDEF",
            created_timestamp="2026-08-04T12:00:00Z",
        )


def test_candidate_immutability():
    lvc_id, canonical_hash = compute_candidate_id(
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
    )
    candidate = LiveValidationCandidate(
        candidate_id=lvc_id,
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    with pytest.raises(ValidationError):
        candidate.eligibility_score = 0.5  # Frozen check


@pytest.mark.parametrize("m_status", list(MonitoringStatus))
def test_validation_session_model(m_status: MonitoringStatus):
    lvc_id = "LVC_1234567890ABCDEF"
    vsn_id, vsn_hash = compute_session_id(
        candidate_id=lvc_id,
        start_timestamp="2026-08-04T12:00:00Z",
    )

    session = ValidationSession(
        session_id=vsn_id,
        candidate_id=lvc_id,
        hypothesis_id="HYP_1234567890ABCDEF",
        status=ValidationStatus.RUNNING,
        monitoring_status=m_status,
        start_timestamp="2026-08-04T12:00:00Z",
        total_observations=10,
        operator="OPERATOR",
        canonical_hash=vsn_hash,
    )

    assert session.session_id == vsn_id
    assert session.monitoring_status == m_status


@pytest.mark.parametrize("slippage", [0.0, 0.001, 0.005, 0.01])
def test_validation_observation_model(slippage: float):
    vsn_id = "VSN_1234567890ABCDEF"
    vob_id, vob_hash = compute_observation_id(
        session_id=vsn_id,
        timestamp="2026-08-04T12:00:00Z",
        live_outcome=0.5,
        expected_outcome=0.4,
    )

    obs = ValidationObservation(
        observation_id=vob_id,
        session_id=vsn_id,
        timestamp="2026-08-04T12:00:00Z",
        live_outcome=0.5,
        expected_outcome=0.4,
        slippage=slippage,
        spread=0.0002,
        latency_ms=45.0,
        fill_ratio=1.0,
        canonical_hash=vob_hash,
    )

    assert obs.observation_id == vob_id
    assert obs.slippage == slippage


@pytest.mark.parametrize("decision", list(ValidationDecisionOutcome))
def test_validation_decision_model(decision: ValidationDecisionOutcome):
    vsn_id = "VSN_1234567890ABCDEF"
    lvc_id = "LVC_1234567890ABCDEF"
    vdc_id, vdc_hash = compute_validation_decision_id(
        session_id=vsn_id,
        candidate_id=lvc_id,
        decision=decision.value,
    )

    dec = ValidationDecision(
        decision_id=vdc_id,
        session_id=vsn_id,
        candidate_id=lvc_id,
        decision=decision,
        rationale="Detailed test rationale statement.",
        timestamp="2026-08-04T12:00:00Z",
        authorizer="BOARD",
        canonical_hash=vdc_hash,
    )

    assert dec.decision_id == vdc_id
    assert dec.decision == decision


@pytest.mark.parametrize("total_sessions", [0, 5, 20, 100])
def test_validation_summary_model(total_sessions: int):
    vsm_id, vsm_hash = compute_summary_id(
        total_candidates=total_sessions,
        total_sessions=total_sessions,
        timestamp="2026-08-04T12:00:00Z",
    )

    summary = ValidationSummary(
        summary_id=vsm_id,
        total_candidates=total_sessions,
        total_sessions=total_sessions,
        total_observations=total_sessions * 10,
        status_counts={"RUNNING": total_sessions},
        decision_counts={"SUPPORTED": total_sessions},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=vsm_hash,
    )

    assert summary.summary_id == vsm_id
    assert summary.total_sessions == total_sessions


def test_validation_audit_model():
    vsn_id = "VSN_1234567890ABCDEF"
    vau_id, vau_hash = compute_audit_id(
        session_id=vsn_id,
        action="CREATE",
        timestamp="2026-08-04T12:00:00Z",
    )

    audit = ValidationAudit(
        audit_id=vau_id,
        session_id=vsn_id,
        action="CREATE",
        previous_status=ValidationStatus.ELIGIBLE,
        new_status=ValidationStatus.RUNNING,
        operator="SYSTEM",
        timestamp="2026-08-04T12:00:00Z",
        notes="Created test session.",
        canonical_hash=vau_hash,
    )

    assert audit.audit_id == vau_id
    assert audit.action == "CREATE"
