"""
Project GOAT v0.6 — Cross-Package Substitution Attack Unit Tests

Verifies rejecting mixed evidence packages (e.g. Package A report with Package B evidence or audit).
"""

from __future__ import annotations

import tempfile
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


def create_sample_package(edge_name: str, policy_id: str, run_fp: str, tmp_root: str):
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name=edge_name,
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id=policy_id)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint=run_fp,
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

    writer = EvidencePackageWriter(root_dir=tmp_root)
    pkg_dir = writer.write_package(report, [ev])
    return pkg_dir, report, ev


def test_cross_package_evidence_substitution_blocked():
    with tempfile.TemporaryDirectory() as tmp_root1, tempfile.TemporaryDirectory() as tmp_root2:
        pkg_dir1, report1, ev1 = create_sample_package("Edge A", "PLC_A", "DS_A", tmp_root1)
        pkg_dir2, report2, ev2 = create_sample_package("Edge B", "PLC_B", "DS_B", tmp_root2)

        # Substitute evidence.json from Package B into Package A
        ev_b_content = (pkg_dir2 / "evidence.json").read_text(encoding="utf-8")
        (pkg_dir1 / "evidence.json").write_text(ev_b_content, encoding="utf-8")

        verifier = EvidencePackageVerifier()
        with pytest.raises(PackageIntegrityError):
            verifier.verify_package(pkg_dir1)


def test_cross_package_report_json_substitution_blocked():
    with tempfile.TemporaryDirectory() as tmp_root1, tempfile.TemporaryDirectory() as tmp_root2:
        pkg_dir1, report1, ev1 = create_sample_package("Edge A", "PLC_A", "DS_A", tmp_root1)
        pkg_dir2, report2, ev2 = create_sample_package("Edge B", "PLC_B", "DS_B", tmp_root2)

        # Substitute validation_report.json from Package B into Package A
        report_b_content = (pkg_dir2 / "validation_report.json").read_text(encoding="utf-8")
        (pkg_dir1 / "validation_report.json").write_text(report_b_content, encoding="utf-8")

        verifier = EvidencePackageVerifier()
        with pytest.raises(PackageIntegrityError):
            verifier.verify_package(pkg_dir1)
