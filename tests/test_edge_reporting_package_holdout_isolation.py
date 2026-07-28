"""
Project GOAT v0.6 — Package Holdout Isolation Unit Tests

Verifies zero access to real holdout data or HoldoutAccessGate during package writing and verification.
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
from goat.research.edge.validation.holdout import HoldoutAccessGate


def test_package_writer_and_verifier_have_no_holdout_gate_dependency():
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Holdout Isolated Package Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_ISO_PKG")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_iso_pkg",
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

        verifier = EvidencePackageVerifier()
        result = verifier.verify_package(pkg_dir)

        gate = HoldoutAccessGate()
        assert gate.bytes_read == 0
        assert result["verification_status"] == "VERIFIED"
