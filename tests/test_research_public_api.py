"""
Project GOAT v0.9 — Comprehensive Public API & Canonical Hash Integrity Tests
"""

import pytest

import goat.research as research
from goat.research import (
    ApprovalRepository,
    EvidenceLevel,
    HypothesisApproval,
    HypothesisPriority,
    HypothesisRegistrySummary,
    HypothesisRepository,
    HypothesisRevision,
    HypothesisStatus,
    HypothesisValidation,
    HypothesisValidationEngine,
    ResearchPersistenceContext,
    RevisionRepository,
    ScientificHypothesis,
    ScientificHypothesisRegistry,
    ScientificResearchEngine,
    SummaryRepository,
    ValidationRepository,
    compute_approval_id,
    compute_canonical_sha256,
    compute_hypothesis_id,
    compute_revision_id,
    compute_summary_id,
    compute_validation_id,
    generate_executive_report,
    generate_json_report,
    generate_markdown_report,
    generate_registry_summary_report,
    generate_validation_report,
    init_research_db,
    serialize_canonical_json,
)


def test_public_api_exports():
    expected_exports = [
        "ApprovalRepository",
        "EvidenceLevel",
        "HypothesisApproval",
        "HypothesisPriority",
        "HypothesisRegistrySummary",
        "HypothesisRepository",
        "HypothesisRevision",
        "HypothesisStatus",
        "HypothesisValidation",
        "HypothesisValidationEngine",
        "ResearchPersistenceContext",
        "RevisionRepository",
        "ScientificHypothesis",
        "ScientificHypothesisRegistry",
        "ScientificResearchEngine",
        "SummaryRepository",
        "ValidationRepository",
        "compute_approval_id",
        "compute_canonical_sha256",
        "compute_hypothesis_id",
        "compute_revision_id",
        "compute_summary_id",
        "compute_validation_id",
        "generate_executive_report",
        "generate_json_report",
        "generate_markdown_report",
        "generate_registry_summary_report",
        "generate_validation_report",
        "init_research_db",
        "serialize_canonical_json",
    ]

    for export_name in expected_exports:
        assert hasattr(research, export_name)
        assert export_name in research.__all__

    assert len(research.__all__) == len(expected_exports)


@pytest.mark.parametrize("i", range(1, 501))
def test_hypothesis_id_determinism_large(i: int):
    title = f"Parameterized Title #{i}"
    null_h = f"H0 Null Statement #{i}"
    alt_h = f"H1 Alternative Statement #{i}"
    author = f"AUTHOR_{i % 5}"

    id1, hash1 = compute_hypothesis_id(title=title, null_hypothesis=null_h, alternative_hypothesis=alt_h, author=author)
    id2, hash2 = compute_hypothesis_id(title=title, null_hypothesis=null_h, alternative_hypothesis=alt_h, author=author)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("HYP_")
    assert len(id1) == 20  # HYP_ + 16 hex chars
    assert len(hash1) == 64


@pytest.mark.parametrize("r", range(1, 501))
def test_revision_id_determinism_large(r: int):
    hyp_id = f"HYP_{r:016X}"
    prev_hash = f"PREV_HASH_{r:064X}"

    id1, hash1 = compute_revision_id(hypothesis_id=hyp_id, revision_number=r, previous_hash=prev_hash)
    id2, hash2 = compute_revision_id(hypothesis_id=hyp_id, revision_number=r, previous_hash=prev_hash)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("REV_")
    assert len(id1) == 20


@pytest.mark.parametrize("v", range(1, 501))
def test_validation_id_determinism_large(v: int):
    hyp_id = f"HYP_{v:016X}"
    reviewer = f"REVIEWER_{v % 10}"

    id1, hash1 = compute_validation_id(hypothesis_id=hyp_id, reviewer=reviewer, is_valid=(v % 2 == 0))
    id2, hash2 = compute_validation_id(hypothesis_id=hyp_id, reviewer=reviewer, is_valid=(v % 2 == 0))

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("HVL_")
    assert len(id1) == 20


@pytest.mark.parametrize("a", range(1, 501))
def test_approval_id_determinism_large(a: int):
    hyp_id = f"HYP_{a:016X}"
    status_list = list(HypothesisStatus)
    status_val = status_list[a % len(status_list)].value

    id1, hash1 = compute_approval_id(hypothesis_id=hyp_id, approver="BOARD", status=status_val)
    id2, hash2 = compute_approval_id(hypothesis_id=hyp_id, approver="BOARD", status=status_val)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("HAP_")
    assert len(id1) == 20


@pytest.mark.parametrize("s", range(1, 501))
def test_summary_id_determinism_large(s: int):
    id1, hash1 = compute_summary_id(total_hypotheses=s, timestamp=f"2026-08-04T12:{s % 60:02d}:00Z")
    id2, hash2 = compute_summary_id(total_hypotheses=s, timestamp=f"2026-08-04T12:{s % 60:02d}:00Z")

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("HRS_")
    assert len(id1) == 20
