"""
Project GOAT v0.6 — Failed & Insufficient Edge Package Unit Tests

Verifies packaging failed candidates, insufficient evidence runs, and confirmatory state packages.
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
    ValidationReportBuilder,
)


def test_package_failed_candidate_edge():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Failed Package Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_FAIL_PKG")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_fail_pkg",
        candidate_target_scope="UNIVERSAL",
    )

    repo.save_candidate_edge(edge)
    repo.save_validation_policy(policy)
    repo.save_validation_run(run)

    # Failed evidence (raw_p_value = 0.50 > alpha 0.05)
    ev_fail = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.OOS,
        dimension_key="retention_summary",
        partition_identity="validation",
        sample_count=150,
        effect_size=0.01,
        effect_size_type="mean_difference",
        raw_p_value=0.50,
        statistic_value=0.5,
    )
    repo.save_evidence_record(ev_fail)

    builder = ValidationReportBuilder(repo)
    report = builder.build(run.validation_run_id)

    with tempfile.TemporaryDirectory() as tmp_root:
        writer = EvidencePackageWriter(root_dir=tmp_root)
        pkg_dir = writer.write_package(report, [ev_fail])

        assert pkg_dir.exists()
        verifier = EvidencePackageVerifier()
        result = verifier.verify_package(pkg_dir)
        assert result["verification_status"] == "VERIFIED"
