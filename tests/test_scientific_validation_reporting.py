"""
Project GOAT v0.7 — Step 5.7 Reporting Subsystem Test Suite
"""

from __future__ import annotations

import json
import pytest

from goat.validation.core import DecisionType, ValidationRun, compute_run_fingerprint, compute_run_id
from goat.validation.decisions import ValidationDecision, compute_decision_id
from goat.validation.evidence import ValidationEvidence, compute_evidence_id
from goat.validation.reporting import (
    ValidationAuditReport,
    ValidationEvidenceReport,
    ValidationReport,
    ValidationStatisticsReport,
    ValidationSummary,
    generate_audit_report,
    generate_evidence_report,
    generate_statistics_report,
    generate_validation_report,
    generate_validation_summary,
    render_validation_markdown,
    serialize_validation_to_json,
)
from goat.validation.statistics import ValidationScores


@pytest.mark.parametrize("idx", list(range(20)))
def test_generate_validation_report_parametrized(idx: int):
    """Verify generate_validation_report returns deterministic ValidationReport across inputs."""
    fp = compute_run_fingerprint(f"HYP_{idx:04d}", [f"VEV_{idx}"])
    run_id, canon_hash = compute_run_id(fp)
    run = ValidationRun(
        validation_id=run_id,
        canonical_hash=canon_hash,
        scientific_fingerprint=fp,
        hypothesis_id=f"HYP_{idx:04d}",
        creation_timestamp="2026-01-01T00:00:00Z",
    )

    did, dhash = compute_decision_id(run_id, "accepted", "2026-01-01T00:00:00Z")
    decision = ValidationDecision(
        decision_id=did,
        decision_hash=dhash,
        validation_run_id=run_id,
        decision_type=DecisionType.ACCEPTED,
        reasoning="Test reasoning",
        timestamp="2026-01-01T00:00:00Z",
    )

    scores = ValidationScores(overall_confidence=0.85)
    evidence_summary = {"overall": {"total_count": 5}}

    report = generate_validation_report(run, decision, scores, evidence_summary, timestamp="2026-01-01T00:00:00Z")

    assert isinstance(report, ValidationReport)
    assert report.report_id.startswith("VRPT_")
    assert report.hypothesis_id == f"HYP_{idx:04d}"
    assert report.decision_summary == "accepted"


@pytest.mark.parametrize("idx", list(range(5)))
def test_generate_validation_summary_parametrized(idx: int):
    """Verify generate_validation_summary compact model across inputs."""
    fp = compute_run_fingerprint(f"HYP_{idx}", ["VEV_1"])
    run_id, canon_hash = compute_run_id(fp)
    run = ValidationRun(validation_id=run_id, canonical_hash=canon_hash, scientific_fingerprint=fp, hypothesis_id=f"HYP_{idx}", creation_timestamp="2026-01-01T00:00:00Z")
    did, dhash = compute_decision_id(run_id, "accepted", "2026-01-01T00:00:00Z")
    decision = ValidationDecision(decision_id=did, decision_hash=dhash, validation_run_id=run_id, decision_type=DecisionType.ACCEPTED, timestamp="2026-01-01T00:00:00Z")
    scores = ValidationScores(overall_confidence=0.9)

    summary = generate_validation_summary(run, decision, scores, evidence_count=3, passed_count=5, total_thresholds=6)
    assert isinstance(summary, ValidationSummary)
    assert summary.hypothesis_id == f"HYP_{idx}"
    assert summary.decision_type == "accepted"


def test_generate_sub_reports():
    """Verify audit, evidence, and statistics report generators."""
    fp = compute_run_fingerprint("HYP_100", ["VEV_1"])
    run_id, canon_hash = compute_run_id(fp)
    run = ValidationRun(validation_id=run_id, canonical_hash=canon_hash, scientific_fingerprint=fp, hypothesis_id="HYP_100", creation_timestamp="2026-01-01T00:00:00Z")

    audit = generate_audit_report(run, [{"event": "start"}], timestamp="2026-01-01T00:00:00Z")
    assert isinstance(audit, ValidationAuditReport)
    assert audit.report_id.startswith("VAUD_")

    eid, eh = compute_evidence_id(run_id, "EXP_1", "experiment", "2026-01-01T00:00:00Z")
    ev = ValidationEvidence(evidence_id=eid, evidence_hash=eh, timestamp="2026-01-01T00:00:00Z")
    ev_rpt = generate_evidence_report(run, [ev], {"overall": {"total_count": 1}}, timestamp="2026-01-01T00:00:00Z")
    assert isinstance(ev_rpt, ValidationEvidenceReport)
    assert ev_rpt.report_id.startswith("VEVR_")

    scores = ValidationScores()
    stat_rpt = generate_statistics_report(run, scores, timestamp="2026-01-01T00:00:00Z")
    assert isinstance(stat_rpt, ValidationStatisticsReport)
    assert stat_rpt.report_id.startswith("VSTR_")


def test_markdown_and_json_formatting():
    """Verify Markdown rendering and JSON serialization."""
    fp = compute_run_fingerprint("HYP_100", ["VEV_1"])
    run_id, canon_hash = compute_run_id(fp)
    run = ValidationRun(validation_id=run_id, canonical_hash=canon_hash, scientific_fingerprint=fp, hypothesis_id="HYP_100", creation_timestamp="2026-01-01T00:00:00Z")
    did, dhash = compute_decision_id(run_id, "accepted", "2026-01-01T00:00:00Z")
    decision = ValidationDecision(decision_id=did, decision_hash=dhash, validation_run_id=run_id, decision_type=DecisionType.ACCEPTED, timestamp="2026-01-01T00:00:00Z")
    scores = ValidationScores(overall_confidence=0.85)

    report = generate_validation_report(run, decision, scores, {"overall": {"total_count": 3}}, timestamp="2026-01-01T00:00:00Z")

    md = render_validation_markdown(report, decision)
    assert "# Validation Report —" in md
    assert "**Hypothesis ID**: HYP_100" in md

    json_dict = serialize_validation_to_json(report, decision, scores)
    assert "decision" in json_dict
    assert "report" in json_dict
    assert "scores" in json_dict
