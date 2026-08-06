"""
Project GOAT v0.9 — Comprehensive Live Validation Public API & Canonical Hash Integrity Tests
"""

import pytest

import goat.live_validation as live_val
from goat.live_validation import (
    AuditRepository,
    CandidateRepository,
    ControlledLiveValidationEngine,
    DecisionRepository,
    LiveValidationCandidate,
    LiveValidationPersistenceContext,
    MasterLiveValidationEngine,
    MonitoringStatus,
    ObservationRepository,
    SummaryRepository,
    ValidationAudit,
    ValidationDecision,
    ValidationDecisionOutcome,
    ValidationEligibilityEngine,
    ValidationMonitoringEngine,
    ValidationObservation,
    ValidationRetirementEngine,
    ValidationSession,
    ValidationSessionRepository,
    ValidationStatus,
    ValidationSummary,
    compute_audit_id,
    compute_candidate_id,
    compute_canonical_sha256,
    compute_observation_id,
    compute_session_id,
    compute_summary_id,
    compute_validation_decision_id,
    generate_decision_report,
    generate_eligibility_report,
    generate_executive_report,
    generate_json_report,
    generate_monitoring_report,
    generate_validation_report,
    init_live_validation_db,
    serialize_canonical_json,
)


def test_public_api_exports():
    expected_exports = [
        "AuditRepository",
        "CandidateRepository",
        "ControlledLiveValidationEngine",
        "DecisionRepository",
        "LiveValidationCandidate",
        "LiveValidationPersistenceContext",
        "MasterLiveValidationEngine",
        "MonitoringStatus",
        "ObservationRepository",
        "SummaryRepository",
        "ValidationAudit",
        "ValidationDecision",
        "ValidationDecisionOutcome",
        "ValidationEligibilityEngine",
        "ValidationMonitoringEngine",
        "ValidationObservation",
        "ValidationRetirementEngine",
        "ValidationSession",
        "ValidationSessionRepository",
        "ValidationStatus",
        "ValidationSummary",
        "compute_audit_id",
        "compute_candidate_id",
        "compute_canonical_sha256",
        "compute_observation_id",
        "compute_session_id",
        "compute_summary_id",
        "compute_validation_decision_id",
        "generate_decision_report",
        "generate_eligibility_report",
        "generate_executive_report",
        "generate_json_report",
        "generate_monitoring_report",
        "generate_validation_report",
        "init_live_validation_db",
        "serialize_canonical_json",
    ]

    for export_name in expected_exports:
        assert hasattr(live_val, export_name)
        assert export_name in live_val.__all__

    assert len(live_val.__all__) == len(expected_exports)


@pytest.mark.parametrize("i", range(1, 1401))
def test_candidate_id_determinism_large(i: int):
    hyp_id = f"HYP_{i:016X}"
    ste_id = f"STE_{i:016X}"
    exp_id = f"EXP_{i:016X}"

    id1, hash1 = compute_candidate_id(hypothesis_id=hyp_id, evaluation_id=ste_id, experiment_id=exp_id)
    id2, hash2 = compute_candidate_id(hypothesis_id=hyp_id, evaluation_id=ste_id, experiment_id=exp_id)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("LVC_")
    assert len(id1) == 20
    assert len(hash1) == 64


@pytest.mark.parametrize("s", range(1, 1401))
def test_session_id_determinism_large(s: int):
    lvc_id = f"LVC_{s:016X}"
    ts = f"2026-08-04T12:{s % 60:02d}:00Z"

    id1, hash1 = compute_session_id(candidate_id=lvc_id, start_timestamp=ts)
    id2, hash2 = compute_session_id(candidate_id=lvc_id, start_timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("VSN_")
    assert len(id1) == 20


@pytest.mark.parametrize("o", range(1, 1401))
def test_observation_id_determinism_large(o: int):
    vsn_id = f"VSN_{o:016X}"
    ts = f"2026-08-04T12:{o % 60:02d}:00Z"

    id1, hash1 = compute_observation_id(session_id=vsn_id, timestamp=ts, live_outcome=0.1 * o, expected_outcome=0.2)
    id2, hash2 = compute_observation_id(session_id=vsn_id, timestamp=ts, live_outcome=0.1 * o, expected_outcome=0.2)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("VOB_")
    assert len(id1) == 20


@pytest.mark.parametrize("d", range(1, 1401))
def test_decision_id_determinism_large(d: int):
    vsn_id = f"VSN_{d:016X}"
    lvc_id = f"LVC_{d:016X}"

    id1, hash1 = compute_validation_decision_id(session_id=vsn_id, candidate_id=lvc_id, decision="PROMOTION_RECOMMENDED")
    id2, hash2 = compute_validation_decision_id(session_id=vsn_id, candidate_id=lvc_id, decision="PROMOTION_RECOMMENDED")

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("VDC_")
    assert len(id1) == 20


@pytest.mark.parametrize("u", range(1, 1401))
def test_summary_id_determinism_large(u: int):
    ts = f"2026-08-04T12:{u % 60:02d}:00Z"

    id1, hash1 = compute_summary_id(total_candidates=u, total_sessions=u, timestamp=ts)
    id2, hash2 = compute_summary_id(total_candidates=u, total_sessions=u, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("VSM_")
    assert len(id1) == 20


@pytest.mark.parametrize("a", range(1, 1401))
def test_audit_id_determinism_large(a: int):
    vsn_id = f"VSN_{a:016X}"
    ts = f"2026-08-04T12:{a % 60:02d}:00Z"

    id1, hash1 = compute_audit_id(session_id=vsn_id, action="CREATE", timestamp=ts)
    id2, hash2 = compute_audit_id(session_id=vsn_id, action="CREATE", timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("VAU_")
    assert len(id1) == 20
