"""
Project GOAT v0.7 — Step 5.7 Persistence Subsystem Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest

from goat.validation.core import (
    DecisionType,
    ScientificHypothesis,
    ValidationRun,
    compute_hypothesis_fingerprint,
    compute_hypothesis_id,
    compute_run_fingerprint,
    compute_run_id,
)
from goat.validation.decisions import ValidationDecision, compute_decision_id
from goat.validation.evidence import ValidationEvidence, compute_evidence_id
from goat.validation.persistence import (
    VALIDATION_SCHEMA_VERSION,
    SQLiteValidationRepository,
)
from goat.validation.reporting import generate_validation_report, ValidationReport
from goat.validation.statistics import ValidationScores


@pytest.fixture
def temp_repo():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteValidationRepository(db_path)
    yield repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_schema_version(temp_repo):
    """Verify SQLite database schema versioning."""
    repo, _ = temp_repo
    assert repo.get_schema_version() == VALIDATION_SCHEMA_VERSION == 1


@pytest.mark.parametrize("idx", list(range(10)))
def test_hypothesis_persistence_roundtrip_parametrized(temp_repo, idx: int):
    """Verify ScientificHypothesis save and retrieve roundtrip across inputs."""
    repo, _ = temp_repo

    fp = compute_hypothesis_fingerprint(f"Strategy Edge {idx}", f"EXP_{idx}", f"STD_{idx}")
    hyp_id, canon_hash = compute_hypothesis_id(fp)

    hyp = ScientificHypothesis(
        hypothesis_id=hyp_id,
        canonical_hash=canon_hash,
        scientific_fingerprint=fp,
        title=f"Strategy Edge {idx}",
        creation_time="2026-01-01T00:00:00Z",
    )

    repo.save_hypothesis(hyp)
    loaded = repo.get_hypothesis(hyp_id)

    assert loaded is not None
    assert loaded.hypothesis_id == hyp.hypothesis_id
    assert loaded.title == hyp.title


@pytest.mark.parametrize("idx", list(range(10)))
def test_validation_run_persistence_roundtrip_parametrized(temp_repo, idx: int):
    """Verify ValidationRun save and retrieve roundtrip across inputs."""
    repo, _ = temp_repo

    hfp = compute_hypothesis_fingerprint(f"Test Hyp {idx}", f"EXP_{idx}", f"STD_{idx}")
    hid, hhash = compute_hypothesis_id(hfp)
    hyp = ScientificHypothesis(hypothesis_id=hid, canonical_hash=hhash, scientific_fingerprint=hfp, title=f"Test Hyp {idx}", creation_time="2026-01-01T00:00:00Z")
    repo.save_hypothesis(hyp)

    rfp = compute_run_fingerprint(hid, [f"VEV_{idx}"])
    rid, rhash = compute_run_id(rfp)

    run = ValidationRun(
        validation_id=rid,
        canonical_hash=rhash,
        scientific_fingerprint=rfp,
        hypothesis_id=hid,
        creation_timestamp="2026-01-01T00:00:00Z",
    )

    repo.save_run(run)
    loaded = repo.get_run(rid)

    assert loaded is not None
    assert loaded.validation_id == rid
    assert loaded.hypothesis_id == hid


def test_evidence_persistence_roundtrip(temp_repo):
    """Verify ValidationEvidence save and retrieve roundtrip."""
    repo, _ = temp_repo

    eid, ehash = compute_evidence_id("VRN_100", "EXP_1", "experiment", "2026-01-01T00:00:00Z")
    ev = ValidationEvidence(
        evidence_id=eid,
        evidence_hash=ehash,
        validation_run_id="VRN_100",
        confidence=0.8,
        timestamp="2026-01-01T00:00:00Z",
    )

    repo.save_evidence(ev)
    loaded = repo.get_evidence(eid)

    assert loaded is not None
    assert loaded.evidence_id == eid
    assert loaded.confidence == 0.8


def test_decision_persistence_roundtrip(temp_repo):
    """Verify ValidationDecision save and retrieve roundtrip."""
    repo, _ = temp_repo

    did, dhash = compute_decision_id("VRN_100", "accepted", "2026-01-01T00:00:00Z")
    dec = ValidationDecision(
        decision_id=did,
        decision_hash=dhash,
        validation_run_id="VRN_100",
        decision_type=DecisionType.ACCEPTED,
        timestamp="2026-01-01T00:00:00Z",
    )

    repo.save_decision(dec)
    loaded = repo.get_decision(did)

    assert loaded is not None
    assert loaded.decision_id == did


def test_report_persistence_roundtrip(temp_repo):
    """Verify ValidationReport save and retrieve roundtrip."""
    repo, _ = temp_repo

    rfp = compute_run_fingerprint("HYP_1", ["VEV_1"])
    rid, rhash = compute_run_id(rfp)
    run = ValidationRun(validation_id=rid, canonical_hash=rhash, scientific_fingerprint=rfp, hypothesis_id="HYP_1", creation_timestamp="2026-01-01T00:00:00Z")
    did, dhash = compute_decision_id(rid, "accepted", "2026-01-01T00:00:00Z")
    decision = ValidationDecision(decision_id=did, decision_hash=dhash, validation_run_id=rid, decision_type=DecisionType.ACCEPTED, timestamp="2026-01-01T00:00:00Z")

    report = generate_validation_report(run, decision, ValidationScores(), {"overall": {}}, timestamp="2026-01-01T00:00:00Z")

    repo.save_report(report)
    loaded = repo.get_report(report.report_id)

    assert loaded is not None
    assert loaded.report_id == report.report_id


def test_export_import_and_integrity(temp_repo):
    """Verify export_validation_run, import_validation_run, and verify_integrity."""
    repo, _ = temp_repo

    hfp = compute_hypothesis_fingerprint("Test Hyp", "EXP_1", "STD_1")
    hid, hhash = compute_hypothesis_id(hfp)
    hyp = ScientificHypothesis(hypothesis_id=hid, canonical_hash=hhash, scientific_fingerprint=hfp, title="Test Hyp", creation_time="2026-01-01T00:00:00Z")
    repo.save_hypothesis(hyp)

    rfp = compute_run_fingerprint(hid, ["VEV_100"])
    rid, rhash = compute_run_id(rfp)
    run = ValidationRun(validation_id=rid, canonical_hash=rhash, scientific_fingerprint=rfp, hypothesis_id=hid, creation_timestamp="2026-01-01T00:00:00Z")
    repo.save_run(run)

    eid, ehash = compute_evidence_id(rid, "EXP_1", "experiment", "2026-01-01T00:00:00Z")
    ev = ValidationEvidence(evidence_id=eid, evidence_hash=ehash, validation_run_id=rid, timestamp="2026-01-01T00:00:00Z")
    repo.save_evidence(ev)

    did, dhash = compute_decision_id(rid, "accepted", "2026-01-01T00:00:00Z")
    dec = ValidationDecision(decision_id=did, decision_hash=dhash, validation_run_id=rid, decision_type=DecisionType.ACCEPTED, timestamp="2026-01-01T00:00:00Z")
    repo.save_decision(dec)

    assert repo.verify_integrity(rid) is True

    exported = repo.export_validation_run(rid)
    assert exported["schema_version"] == VALIDATION_SCHEMA_VERSION
    assert exported["run"]["validation_id"] == rid

    tmp2 = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path2 = tmp2.name
    tmp2.close()
    repo2 = SQLiteValidationRepository(db_path2)

    repo2.save_hypothesis(hyp)
    imported_run = repo2.import_validation_run(exported)

    assert imported_run.validation_id == rid
    assert repo2.get_evidence(eid) is not None

    repo2.close()
    if os.path.exists(db_path2):
        os.remove(db_path2)
