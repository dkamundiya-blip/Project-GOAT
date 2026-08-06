"""
Project GOAT v0.9 — Dedicated Unit Tests for Live Validation Reporting Generators
"""

import json
import pytest

from goat.live_validation.core.canonical import compute_summary_id
from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
    ValidationStatus,
)
from goat.live_validation.core.models import (
    LiveValidationCandidate,
    ValidationDecision,
    ValidationObservation,
    ValidationSession,
    ValidationSummary,
)
from goat.live_validation.reporting.reports import (
    generate_decision_report,
    generate_eligibility_report,
    generate_executive_report,
    generate_json_report,
    generate_monitoring_report,
    generate_validation_report,
)


def test_generate_eligibility_report():
    cand = LiveValidationCandidate(
        candidate_id="LVC_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        evidence_ids=["EVR_1234567890ABCDEF"],
        created_timestamp="2026-08-04T12:00:00Z",
    )

    report = generate_eligibility_report(cand)
    assert "# LIVE VALIDATION CANDIDATE ELIGIBILITY REPORT" in report
    assert cand.candidate_id in report


def test_generate_validation_report():
    session = ValidationSession(
        session_id="VSN_1234567890ABCDEF",
        candidate_id="LVC_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        status=ValidationStatus.RUNNING,
        monitoring_status=MonitoringStatus.NORMAL,
        start_timestamp="2026-08-04T12:00:00Z",
        total_observations=5,
    )
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id=session.session_id,
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
        )
        for i in range(5)
    ]

    report = generate_validation_report(session, observations)
    assert "# CONTROLLED LIVE VALIDATION SESSION REPORT" in report
    assert session.session_id in report


def test_generate_monitoring_report():
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id="VSN_1234567890ABCDEF",
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
            slippage=0.001,
            latency_ms=40.0,
        )
        for i in range(5)
    ]

    report = generate_monitoring_report("VSN_1234567890ABCDEF", observations)
    assert "# EXECUTION QUALITY MONITORING REPORT" in report


def test_generate_decision_report():
    dec = ValidationDecision(
        decision_id="VDC_1234567890ABCDEF",
        session_id="VSN_1234567890ABCDEF",
        candidate_id="LVC_1234567890ABCDEF",
        decision=ValidationDecisionOutcome.PROMOTION_RECOMMENDED,
        rationale="Passed all criteria.",
        timestamp="2026-08-04T12:00:00Z",
    )

    report = generate_decision_report(dec)
    assert "# VALIDATION SCIENTIFIC DECISION REPORT" in report
    assert dec.decision_id in report


def test_generate_json_report():
    session = ValidationSession(
        session_id="VSN_1234567890ABCDEF",
        candidate_id="LVC_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        start_timestamp="2026-08-04T12:00:00Z",
    )

    json_str = generate_json_report(session)
    data = json.loads(json_str)
    assert data["session_id"] == session.session_id


@pytest.mark.parametrize("session_count", range(1, 10))
def test_generate_executive_report(session_count: int):
    sessions = [
        ValidationSession(
            session_id=f"VSN_{i:016X}",
            candidate_id=f"LVC_{i:016X}",
            hypothesis_id=f"HYP_{i:016X}",
            start_timestamp="2026-08-04T12:00:00Z",
        )
        for i in range(session_count)
    ]

    vsm_id, vsm_hash = compute_summary_id(total_candidates=session_count, total_sessions=session_count)
    summary = ValidationSummary(
        summary_id=vsm_id,
        total_candidates=session_count,
        total_sessions=session_count,
        total_observations=session_count * 10,
        status_counts={"RUNNING": session_count},
        decision_counts={"SUPPORTED": session_count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=vsm_hash,
    )

    report = generate_executive_report(summary, sessions)
    assert "# PROJECT GOAT — CONTROLLED LIVE VALIDATION EXECUTIVE REPORT" in report
    assert f"Total Sessions**: `{session_count}`" in report
