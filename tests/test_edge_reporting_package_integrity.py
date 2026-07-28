"""
Project GOAT v0.6 — Package Tamper & Integrity Adversarial Unit Tests

Verifies detecting tampered artifacts, missing files, extraneous files, and corrupted digests.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.reporting import (
    EvidencePackageVerifier,
    EvidencePackageWriter,
    PackageIntegrityError,
    ValidationReportBuilder,
)


@pytest.fixture
def sample_package_environment():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Tamper Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_TAMPER")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_tamper",
        candidate_target_scope="UNIVERSAL",
    )

    repo.save_candidate_edge(edge)
    repo.save_validation_policy(policy)
    repo.save_validation_run(run)

    ev = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.DISCOVERY,
        dimension_key="disc_summary",
        partition_identity="train",
        sample_count=150,
        effect_size=0.35,
        effect_size_type="mean_difference",
        raw_p_value=0.001,
        statistic_value=3.5,
    )
    repo.save_evidence_record(ev)

    builder = ValidationReportBuilder(repo)
    report = builder.build(run.validation_run_id)
    return report, ev


def test_verifier_detects_tampered_report_json(sample_package_environment):
    report, ev = sample_package_environment
    with tempfile.TemporaryDirectory() as tmp_root:
        writer = EvidencePackageWriter(root_dir=tmp_root)
        pkg_dir = writer.write_package(report, [ev])

        # Tamper validation_report.json
        report_file = pkg_dir / "validation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write('{"tampered": true}')

        verifier = EvidencePackageVerifier()
        with pytest.raises(PackageIntegrityError) as excinfo:
            verifier.verify_package(pkg_dir)
        assert "Checksum mismatch" in str(excinfo.value) or "ValidationReport" in str(excinfo.value)


def test_verifier_detects_tampered_evidence_json(sample_package_environment):
    report, ev = sample_package_environment
    with tempfile.TemporaryDirectory() as tmp_root:
        writer = EvidencePackageWriter(root_dir=tmp_root)
        pkg_dir = writer.write_package(report, [ev])

        # Tamper evidence.json
        ev_file = pkg_dir / "evidence.json"
        with open(ev_file, "w", encoding="utf-8") as f:
            f.write("[]")

        verifier = EvidencePackageVerifier()
        with pytest.raises(PackageIntegrityError):
            verifier.verify_package(pkg_dir)


def test_verifier_detects_missing_artifact(sample_package_environment):
    report, ev = sample_package_environment
    with tempfile.TemporaryDirectory() as tmp_root:
        writer = EvidencePackageWriter(root_dir=tmp_root)
        pkg_dir = writer.write_package(report, [ev])

        # Delete validation_report.md
        (pkg_dir / "validation_report.md").unlink()

        verifier = EvidencePackageVerifier()
        with pytest.raises(PackageIntegrityError) as excinfo:
            verifier.verify_package(pkg_dir)
        assert "missing mandatory artifact" in str(excinfo.value)


def test_verifier_detects_extraneous_file(sample_package_environment):
    report, ev = sample_package_environment
    with tempfile.TemporaryDirectory() as tmp_root:
        writer = EvidencePackageWriter(root_dir=tmp_root)
        pkg_dir = writer.write_package(report, [ev])

        # Add illegal extra file inside package directory
        (pkg_dir / "extra_unauthorized.txt").write_text("malicious")

        verifier = EvidencePackageVerifier()
        with pytest.raises(PackageIntegrityError) as excinfo:
            verifier.verify_package(pkg_dir)
        assert "unexpected/unauthorized artifact" in str(excinfo.value)
