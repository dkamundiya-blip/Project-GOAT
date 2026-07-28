"""
Project GOAT v0.6 — Scientific Evidence Package Unit Tests

Verifies writing and verifying complete filesystem scientific evidence packages.
"""

from __future__ import annotations

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
    ValidationReportBuilder,
)


def test_write_and_verify_evidence_package():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Package Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_PKG")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_pkg",
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

    with tempfile.TemporaryDirectory() as tmp_root:
        writer = EvidencePackageWriter(root_dir=tmp_root)
        pkg_dir = writer.write_package(report, [ev])

        assert pkg_dir.exists()
        assert (pkg_dir / "manifest.json").exists()
        assert (pkg_dir / "validation_report.json").exists()
        assert (pkg_dir / "validation_report.md").exists()
        assert (pkg_dir / "evidence.json").exists()
        assert (pkg_dir / "integrity.json").exists()

        verifier = EvidencePackageVerifier()
        result = verifier.verify_package(pkg_dir)
        assert result["verification_status"] == "VERIFIED"
        assert result["report_id"] == report.report_id
